import tkinter as tk
from tkinter import ttk


class CustomProgressBar:

    def __init__(self, length, progress):
        self.progress = progress
        self.frame = tk.Frame(width=500, height=50)
        self.frame.grid()
        self.progressbar = ttk.Progressbar( self.frame, orient='horizontal', length = length, mode='determinate', maximum=100)
        self.progressbar["value"] = progress
        self.progressbar.grid(row=0, column=0)
        self.label = ttk.Label(self.frame, text=str(self.progress) + "%")
        self.label.grid(row=0, column=1)
    
    def set_progress(self, progress):
        self.progressbar["value"] = progress
        self.label.config(text = str(progress) + "%")
        self.progress = progress

    def get_progress(self):
        return self.progress
    
    def __str__(self):
        print("Progress: %s" % self.progress)