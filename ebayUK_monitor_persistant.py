import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
import webbrowser
import threading
import time
import re
import os
import json
from queue import Queue

class eBayMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("eBay UK Monitor Pro")
        self.tracked_items = []
        self.notification_queue = Queue()
        self.monitoring_active = False
        self.history_file = "ebay.txt"
        self.notified_ids = self.load_notified_ids()
        self.file_lock = threading.Lock()
        
        self.setup_gui()
        self.load_tracked_items()  # Load saved items on startup
        self.check_notifications()

    def setup_gui(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Entry fields
        ttk.Label(main_frame, text="Keyword:").grid(row=0, column=0, sticky="w")
        self.keyword_entry = ttk.Entry(main_frame, width=30)
        self.keyword_entry.grid(row=0, column=1, padx=5)

        ttk.Label(main_frame, text="Min Price (£):").grid(row=1, column=0, sticky="w")
        self.min_price_entry = ttk.Entry(main_frame, width=30)
        self.min_price_entry.grid(row=1, column=1, padx=5)

        ttk.Label(main_frame, text="Max Price (£):").grid(row=2, column=0, sticky="w")
        self.max_price_entry = ttk.Entry(main_frame, width=30)
        self.max_price_entry.grid(row=2, column=1, padx=5)

        ttk.Label(main_frame, text="Exclude Keywords (comma separated):").grid(row=3, column=0, sticky="w")
        self.exclude_entry = ttk.Entry(main_frame, width=30)
        self.exclude_entry.grid(row=3, column=1, padx=5)

        # Buttons
        self.add_btn = ttk.Button(main_frame, text="Add Tracker", command=self.add_tracker)
        self.add_btn.grid(row=4, column=0, pady=5)
        
        self.remove_btn = ttk.Button(main_frame, text="Remove Selected", command=self.remove_tracker)
        self.remove_btn.grid(row=4, column=1, pady=5)

        # Tracked items list
        self.listbox = tk.Listbox(main_frame, width=50, height=10)
        self.listbox.grid(row=5, column=0, columnspan=2, pady=5)

        # Monitoring controls
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=6, column=0, columnspan=2, pady=5)
        
        self.monitor_btn = ttk.Button(control_frame, text="Start Monitoring", 
                                    command=self.toggle_monitoring)
        self.monitor_btn.grid(row=0, column=0, padx=5)
        
        self.buy_it_now_var = tk.BooleanVar()
        self.buy_it_now_cb = ttk.Checkbutton(
            control_frame, 
            text="Only Buy-It-Now Listings",
            variable=self.buy_it_now_var
        )
        self.buy_it_now_cb.grid(row=0, column=1, padx=5)

    def load_tracked_items(self):
        try:
            if os.path.exists("tracked_items.json"):
                with open("tracked_items.json", "r") as f:
                    self.tracked_items = json.load(f)
                    # Populate listbox with loaded items
                    for item in self.tracked_items:
                        display_text = f"{item['keyword']} (£{item['min_price']}-£{item['max_price']})"
                        if item['exclude']:
                            display_text += f" [Excl: {', '.join(item['exclude'])}]"
                        self.listbox.insert(tk.END, display_text)
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load tracked items: {e}")

    def save_tracked_items(self):
        try:
            with open("tracked_items.json", "w") as f:
                json.dump(self.tracked_items, f)
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save tracked items: {e}")

    def load_notified_ids(self):
        if not os.path.exists(self.history_file):
            return set()
        with open(self.history_file, "r") as f:
            return set(line.strip() for line in f if line.strip())

    def save_notified_id(self, listing_id):
        with self.file_lock:
            with open(self.history_file, "a") as f:
                f.write(f"{listing_id}\n")
            self.notified_ids.add(listing_id)

    def add_tracker(self):
        keyword = self.keyword_entry.get().strip()
        min_price = self.min_price_entry.get() or "0"
        max_price = self.max_price_entry.get()
        exclude_keywords = [kw.strip().lower() for kw in self.exclude_entry.get().split(",") if kw.strip()]

        try:
            min_price = float(min_price)
            max_price = float(max_price)
            
            if min_price > max_price:
                raise ValueError("Minimum price cannot exceed maximum price")
            if not keyword:
                raise ValueError("Keyword cannot be empty")

            self.tracked_items.append({
                'keyword': keyword,
                'min_price': min_price,
                'max_price': max_price,
                'exclude': exclude_keywords
            })
            
            display_text = f"{keyword} (£{min_price}-£{max_price})"
            if exclude_keywords:
                display_text += f" [Excl: {', '.join(exclude_keywords)}]"
            
            self.listbox.insert(tk.END, display_text)
            self.clear_entries()
            self.save_tracked_items()  # Save after adding

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def clear_entries(self):
        self.keyword_entry.delete(0, tk.END)
        self.min_price_entry.delete(0, tk.END)
        self.max_price_entry.delete(0, tk.END)
        self.exclude_entry.delete(0, tk.END)

    def remove_tracker(self):
        selected = self.listbox.curselection()
        if selected:
            index = selected[0]
            self.listbox.delete(index)
            del self.tracked_items[index]
            self.save_tracked_items()  # Save after removal

    def toggle_monitoring(self):
        self.monitoring_active = not self.monitoring_active
        if self.monitoring_active:
            self.monitor_btn.config(text="Stop Monitoring")
            threading.Thread(target=self.monitor_listings, daemon=True).start()
        else:
            self.monitor_btn.config(text="Start Monitoring")

    def monitor_listings(self):
        while self.monitoring_active:
            for item in self.tracked_items:
                try:
                    params = {
                        '_nkw': item['keyword'],
                        '_sop': '10',
                        '_loc': '1',
                        'LH_Sold': '0',
                        'LH_Complete': '0'
                    }

                    if item['exclude']:
                        params['_ex_kw'] = '+'.join(item['exclude'])
                    
                    if self.buy_it_now_var.get():
                        params['LH_BIN'] = '1'

                    response = requests.get(
                        'https://www.ebay.co.uk/sch/i.html',
                        params=params,
                        timeout=10
                    )

                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    for listing in soup.find_all('li', class_='s-item'):
                        listing_id = listing.get('data-view')
                        if not listing_id or listing_id in self.notified_ids:
                            continue

                        price_elem = listing.find('span', class_='s-item__price')
                        title_elem = listing.find('div', class_='s-item__title')
                        link_elem = listing.find('a', class_='s-item__link')
                        location_elem = listing.find('span', class_='s-item__location')

                        if not all([price_elem, title_elem, link_elem, location_elem]):
                            continue

                        location = location_elem.text.lower()
                        if 'uk' not in location and 'united kingdom' not in location:
                            continue

                        price_text = re.sub(r'[^\d.]', '', price_elem.text.split()[-1])
                        if not price_text:
                            continue

                        try:
                            price = float(price_text)
                            if item['min_price'] <= price <= item['max_price']:
                                self.save_notified_id(listing_id)
                                self.notification_queue.put({
                                    'title': title_elem.text.strip(),
                                    'price': price_elem.text.strip(),
                                    'link': link_elem['href']
                                })
                        except ValueError:
                            continue

                except Exception as e:
                    print(f"Monitoring error: {e}")
                time.sleep(5)

    def check_notifications(self):
        while not self.notification_queue.empty():
            notification = self.notification_queue.get()
            self.show_notification(notification)
        self.root.after(1000, self.check_notifications)

    def show_notification(self, notification):
        popup = tk.Toplevel(self.root)
        popup.title("Price Alert!")
        msg = f"{notification['title']}\nPrice: {notification['price']}"
        ttk.Label(popup, text=msg).pack(padx=20, pady=10)
        
        def open_link():
            webbrowser.open(notification['link'])
            popup.destroy()
            
        ttk.Button(popup, text="View Listing", command=open_link).pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Button(popup, text="Dismiss", command=popup.destroy).pack(side=tk.RIGHT, padx=10, pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = eBayMonitor(root)
    root.mainloop()
