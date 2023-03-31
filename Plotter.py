import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PlotterApp:

    def __init__(self, master):
        self.master = master
        master.title("CSV Plotter")

        # Creating Browse Button
        self.browse_button = tk.Button(master, text="Browse", command=self.browse_file)
        self.browse_button.pack()

       # Creating X Label Entry Box
        self.x_label_frame = tk.Frame(master)
        self.x_label_frame.pack()
        self.x_label_title = tk.Label(self.x_label_frame, text="Rename X-axis: ")
        self.x_label_title.pack(side=tk.LEFT)
        self.x_label_entry = tk.Entry(self.x_label_frame)
        self.x_label_entry.pack(side=tk.LEFT)

        # Creating Y Label Entry Box
        self.y_label_frame = tk.Frame(master)
        self.y_label_frame.pack()
        self.y_label_title = tk.Label(self.y_label_frame, text="Rename Y-axis: ")
        self.y_label_title.pack(side=tk.LEFT)
        self.y_label_entry = tk.Entry(self.y_label_frame)
        self.y_label_entry.pack(side=tk.LEFT)

        # Creating Plot Button
        self.plot_button = tk.Button(master, text="Plot", command=self.plot_data)
        self.plot_button.pack()

        # Creating Quit Button
        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.pack()

        # Creating Figure and Axes for Plot
        self.fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        
        # Adjusting Figure Subplots
        self.fig.subplots_adjust(left=0.15, bottom=0.15, right=0.95, top=0.95)
        
        # Creating Canvas for Plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Initializing Filepath Variable
        self.filepath = ""

    def browse_file(self):
        # Open file dialog to select CSV file
        self.filepath = filedialog.askopenfilename(initialdir="./", title="Select a File", filetypes=(("CSV Files", "*.csv"),))

    def plot_data(self):
        # Check if CSV file selected
        if self.filepath == "":
            messagebox.showerror(title="Error", message="No file selected")
            return

        # Read CSV File
        try:
            df = pd.read_csv(self.filepath)
        except:
            messagebox.showerror(title="Error", message="Error reading CSV file")
            return

        # Check if CSV file has correct columns
        if set(["X", "Y"]).issubset(set(df.columns)):
            # Clear Axes
            self.ax.clear()

            # Plot Data
            self.ax.plot(df["X"], df["Y"])

            # Set X and Y Labels
            x_label = self.x_label_entry.get()
            y_label = self.y_label_entry.get()
            self.ax.set_xlabel(x_label)
            self.ax.set_ylabel(y_label)

            # Draw Plot
            self.canvas.draw()

            # Save Plot as PNG File
            try:
                self.fig.savefig(self.filepath[:-4] + ".png")
            except:
                messagebox.showerror(title="Error", message="Error saving plot as PNG file")

        else:
            messagebox.showerror(title="Error", message="CSV file must have columns named 'X' and 'Y'")


root = tk.Tk()
app = PlotterApp(root)
root.mainloop()