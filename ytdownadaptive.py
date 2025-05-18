import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re
import threading
import yt_dlp

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title('YouTube High Quality Downloader')
        self.root.geometry('600x400')
        self.setup_ui()
        
    def setup_ui(self):
        # URL input section
        url_frame = tk.Frame(self.root, pady=10)
        url_frame.pack(fill='x', padx=20)
        
        tk.Label(url_frame, text='YouTube URL:').pack(anchor='w')
        self.url_entry = tk.Entry(url_frame, width=70)
        self.url_entry.pack(fill='x', pady=5)
        
        # Output folder section
        folder_frame = tk.Frame(self.root, pady=10)
        folder_frame.pack(fill='x', padx=20)
        
        tk.Label(folder_frame, text='Output Folder:').pack(anchor='w')
        
        path_frame = tk.Frame(folder_frame)
        path_frame.pack(fill='x', pady=5)
        
        self.folder_path = tk.StringVar()
        self.folder_entry = tk.Entry(path_frame, textvariable=self.folder_path, width=50)
        self.folder_entry.pack(side='left', fill='x', expand=True)
        
        browse_btn = tk.Button(path_frame, text='Browse...', command=self.select_folder)
        browse_btn.pack(side='right', padx=5)
        
        # Download button
        btn_frame = tk.Frame(self.root, pady=10)
        btn_frame.pack(fill='x', padx=20)
        
        self.download_btn = tk.Button(btn_frame, text='Download', command=self.start_download, 
                                     bg='#4CAF50', fg='white', height=2)
        self.download_btn.pack(fill='x')
        
        # Progress and status
        status_frame = tk.Frame(self.root, pady=10)
        status_frame.pack(fill='x', padx=20)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(status_frame, textvariable=self.status_var, anchor='w')
        status_label.pack(fill='x')
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = tk.Scale(status_frame, variable=self.progress_var, from_=0, to=100, 
                                    orient='horizontal', state='disabled')
        self.progress_bar.pack(fill='x')
    
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
    
    def start_download(self):
        url = self.url_entry.get().strip()
        output_path = self.folder_path.get().strip()
        
        # Validate inputs
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        if not self.is_valid_youtube_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL format")
            return
        
        if not output_path:
            messagebox.showerror("Error", "Please select an output folder")
            return
        
        if not os.path.exists(output_path):
            messagebox.showerror("Error", "Selected output folder does not exist")
            return
        
        # Disable UI during download
        self.download_btn.config(state='disabled')
        self.status_var.set("Starting download...")
        
        # Start download in a separate thread
        download_thread = threading.Thread(target=self.download_video, args=(url, output_path))
        download_thread.daemon = True
        download_thread.start()
    
    def download_video(self, url, output_path):
        try:
            def progress_hook(d):
                if d['status'] == 'downloading':
                    # Update progress
                    p = d.get('_percent_str', '0%').replace('%', '')
                    try:
                        self.progress_var.set(float(p))
                    except ValueError:
                        pass
                    self.status_var.set(f"Downloading: {d.get('_percent_str', '0%')}")
                elif d['status'] == 'finished':
                    self.status_var.set("Download finished. Processing...")
                elif d['status'] == 'error':
                    self.status_var.set(f"Error: {d.get('error')}")
            
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',  # Download best quality
                'ffmpeg_location': r'C:\ffmpeg\bin\ffmpeg.exe',  # Use your actual path here
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'merge_output_format': 'mp4',  # Merge into mp4
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor', 
                    'preferedformat': 'mp4',
                }],
                'progress_hooks': [progress_hook],
                'noplaylist': True,  # Don't download playlists
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Enable UI after download
            self.root.after(0, lambda: self.status_var.set("Download completed successfully!"))
            self.root.after(0, lambda: self.download_btn.config(state='normal'))
            self.root.after(0, lambda: messagebox.showinfo("Success", "Video downloaded successfully!"))
        
        except Exception as e:
            # Error handling
            error_message = str(e)
            self.root.after(0, lambda: self.status_var.set(f"Error: {error_message}"))
            self.root.after(0, lambda: self.download_btn.config(state='normal'))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {error_message}"))
    
    def is_valid_youtube_url(self, url):
        # Handle various YouTube URL formats
        youtube_regex = (
            r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        youtube_regex_match = re.match(youtube_regex, url)
        
        # Handle YouTube shortened URLs
        youtube_short_regex = r'(https?://)?(www\.)?youtu\.be/([^&=%\?]{11})'
        youtube_short_regex_match = re.match(youtube_short_regex, url)
        
        # Handle YouTube share URLs
        youtube_share_regex = r'(https?://)?(www\.)?youtube\.com/shorts/([^&=%\?]{11})'
        youtube_share_regex_match = re.match(youtube_share_regex, url)
        
        return bool(youtube_regex_match or youtube_short_regex_match or youtube_share_regex_match)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
