import tkinter as tk
import tkinter.ttk as ttk
from multiprocessing import Queue
from sharedobject import SharedObject

class MainWindow:
    def __init__(self, frames):
        # initialize UI

        # window
        self.window = tk.Tk()
        self.window.geometry("900x600")
        self.window.title("LANL Earthquake Prediction Helper App")

        # status bar on the bottom
        self.var = tk.StringVar(self.window)
        self.var.set("Train data loaded successfully!")
        self.status_bar = tk.Label(self.window, textvariable=self.var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # main container
        self.main_frame = tk.Frame(self.window)
        self.main_frame.pack(anchor=tk.NW, expand=True, fill=tk.BOTH)

        # init shared object
        self.shared_obj = SharedObject(self.var, self.window)

        # frame on the left
        f = frames[0](self.main_frame, self.shared_obj)
        f.pack(side=tk.LEFT, fill=tk.BOTH)

        # separator
        sep = ttk.Separator(self.main_frame, orient=tk.VERTICAL)
        sep.pack(side=tk.LEFT, fill=tk.Y)

        # frame on the right
        f = frames[1](self.main_frame, self.shared_obj)
        f.pack(side=tk.LEFT, fill=tk.BOTH)

    # show window
    def show(self):
        self.window.mainloop()