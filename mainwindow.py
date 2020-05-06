import tkinter as tk
import tkinter.ttk as ttk
from multiprocessing import Queue
from sharedobject import SharedObject
from ttkthemes import ThemedStyle

class MainWindow:
    def __init__(self, frames):
        # initialize UI

        # window
        self.window = tk.Tk()
        self.window.geometry("900x600")
        self.window.title("LANL Earthquake Prediction Helper App")

        style = ThemedStyle(self.window)
        style.set_theme('arc')

        # status bar on the bottom
        self.var = tk.StringVar(self.window)
        self.var.set("Train data loaded successfully!")
        self.status_bar = ttk.Label(self.window, textvariable=self.var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # main container
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(anchor=tk.NW, expand=True, fill=tk.BOTH)

        # init shared object
        self.shared_obj = SharedObject(self.var, self.window)

        # frame on the left
        f = frames[0](self.main_frame, self.shared_obj)
        f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # separator
        sep = ttk.Separator(self.main_frame, orient=tk.VERTICAL)
        sep.pack(side=tk.LEFT, fill=tk.Y)

        # frame on the right
        f = frames[1](self.main_frame, self.shared_obj)
        f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # show window
    def show(self):
        self.window.mainloop()

class BenchmarkWindow:
    def __init__(self, root):
        self.root = root
        self.root.geometry("300x300")

        style = ThemedStyle(self.root)
        style.set_theme('arc')