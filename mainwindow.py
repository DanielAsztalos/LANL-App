import tkinter as tk
import tkinter.ttk as ttk
from multiprocessing import Queue
from sharedobject import SharedObject
from ttkthemes import ThemedStyle
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import math
from statistics import mean
from time import sleep
import os

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
    def __init__(self, root, scores):
        self.root = root
        self.root.geometry("800x600")
        self.scores = scores

        keys = list(self.scores.keys())
        w = .75
        num_bars = len(keys)
        bar_w = w / num_bars
        x_axis = list(range(len(self.scores[keys[0]]["train"])))

        self.selected_figure = 1

        # figure with train scores
        f1 = Figure(figsize=(5, 5), dpi=100)
        a = f1.add_subplot(111)
        for i, key in enumerate(keys):
            a.bar([x + i * bar_w for x in x_axis], self.scores[key]["train"], bar_w)
        
        a.legend(keys)
        a.set_title("Validation scores during training")
        a.set_yscale('log')
        # a.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

        # figure with test scores
        f2 = Figure(figsize=(5,5), dpi=100)
        a = f2.add_subplot(111)
        for i, key in enumerate(keys):
            a.bar([x + i * bar_w for x in x_axis], self.scores[key]["validation"], bar_w)
        
        a.legend(keys)
        a.set_title("Test scores")
        a.set_yscale('log')
        # a.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())

        # figure with averages
        f3 = Figure(figsize=(5, 5), dpi=100)
        a = f3.add_subplot(111)
        w = 0.20
        for i, key in enumerate(keys):
            a.bar([x + i * w for x in range(2)], [mean(self.scores[key]["train"]), mean(self.scores[key]["validation"])], w)
        a.set_yscale('log')
        a.legend(keys)
        a.set_title("Average MAEs of the models")

        self.figures = [f1, f2, f3]
        
        container = ttk.Frame(self.root)
        container.pack(side=tk.TOP, fill=tk.X, expand=True)

        button1 = ttk.Button(self.root, text="<", command=lambda: self.switch_figures(-1))
        button1.pack(in_=container, side=tk.LEFT)

        button2 = ttk.Button(self.root, text=">", command=lambda: self.switch_figures(+1))
        button2.pack(in_=container, side=tk.LEFT)

        button3 = ttk.Button(self.root, text="Export plots", command=self.export_plots)
        button3.pack(in_=container, side=tk.LEFT)

        self.canvas = FigureCanvasTkAgg(f1, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def switch_figures(self, direction):
        try:
            self.canvas.get_tk_widget().destroy()
        except:
            pass

        if self.selected_figure + direction > len(self.figures):
            self.selected_figure = 1
        elif self.selected_figure + direction < 1:
            self.selected_figure = len(self.figures)
        else:
            self.selected_figure += direction

        self.canvas = FigureCanvasTkAgg(self.figures[self.selected_figure-1], self.root)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def export_plots(self):
        path = tk.filedialog.askdirectory()

        for i, fig in enumerate(self.figures):
            fig.savefig(os.path.join(path, "figure_" + str(i) + ".png"))

