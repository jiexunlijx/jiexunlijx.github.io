import tkinter as tk
from tkinter import ttk, filedialog
from pytubefix import YouTube
import threading
import queue

# Create the main window
root = tk.Tk()
root.title("YouTube Video Downloader")

# Create a queue for thread communication
status_queue = queue.Queue()

# Create GUI elements
url_label = tk.Label(root, text="Enter YouTube URL:")
url_label.pack()

url_entry = tk.Entry(root, width=50)
url_entry.pack()

select_folder_button = tk.Button(root, text="Select Output Folder")
select_folder_button.pack()

folder_label = tk.Label(root, text="No folder selected")
folder_label.pack()

download_button = tk.Button(root, text="Download")
download_button.pack()

status_label = tk.Label(root, text="")
status_label.pack()

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack()

# Function to select output folder
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_label.config(text=folder)

select_folder_button.config(command=select_folder)

# Progress callback function
def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = (bytes_downloaded / total_size) * 100
    status_queue.put(("progress", percentage))

# Function to check the queue for status and progress updates
def check_queue():
    if not status_queue.empty():
        message = status_queue.get()
        if message[0] == "progress":
            percentage = message[1]
            status_label.config(text=f"Downloading... {percentage:.2f}%")
            progress_bar["value"] = percentage
        elif message[0] == "status":
            status_label.config(text=message[1])
            if message[1] == "Download complete." or message[1].startswith("Error"):
                download_button.config(state="normal")
                progress_bar["value"] = 0  # Reset progress bar
    root.after(100, check_queue)

# Function to download the video
def download_video(url, output_folder, status_queue):
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        stream = yt.streams.get_highest_resolution()
        stream.download(output_path=output_folder)
        status_queue.put(("status", "Download complete."))
    except Exception as e:
        status_queue.put(("status", f"Error: {str(e)}"))

# Function to handle download button click
def on_download():
    url = url_entry.get()
    output_folder = folder_label.cget("text")
    if not url or output_folder == "No folder selected":
        status_label.config(text="Please enter URL and select folder.")
        return
    status_label.config(text="Downloading...")
    progress_bar["value"] = 0
    download_button.config(state="disabled")
    thread = threading.Thread(target=download_video, args=(url, output_folder, status_queue))
    thread.start()
    root.after(100, check_queue)

download_button.config(command=on_download)

# Start the GUI event loop
root.mainloop()