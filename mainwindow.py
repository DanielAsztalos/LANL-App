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
import numpy as np
from report import ReportGenerator
from tkinterhtml import HtmlFrame

class MainWindow:
    def __init__(self, frames):
        # initialize UI

        # window
        self.window = tk.Tk()
        self.window.geometry("900x600")
        self.window.title("Earthquake Prediction Helper App")
        self.window.configure(bg="#ccd9ed")

        style = ThemedStyle(self.window)
        style.set_theme('arc')

        menu = tk.Menu(self.window)
        self.window.config(menu=menu)

        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Exit")
        menu.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="About", command=self.open_help)
        menu.add_cascade(label="Help", menu=help_menu)

        # status bar on the bottom
        self.var = tk.StringVar(self.window)
        self.var.set("Application initialized successfully!")
        s = ttk.Style()
        s.configure("new.TLabel", foreground="#000000", background="#ccd9ed")
        self.status_bar = ttk.Label(self.window, textvariable=self.var, style="new.TLabel", anchor=tk.W)
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

    def exit(self):
        self.window.destroy()

    def open_help(self):
        tl = tk.Toplevel(self.window, bg="#F5F6F7")
        tl.transient(self.window)
        HelpWindow(tl)

class HelpWindow:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x600")

        canvas = tk.Canvas(self.root, bg="#F5F6F7", highlightthickness=0)

        scrollbar = ttk.Scrollbar(self.root, orient='vertical', command=canvas.yview)

        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        title = ttk.Label(self.scrollable_frame, text="Earthquake Prediction App", font=("Sans Serif", 18))
        title.pack(anchor=tk.NW, padx=20, pady=10)

        lines = []
        with open("data/help.txt", "rt") as inf:
            lines = inf.readlines()

        for line in lines:
            label = ttk.Label(self.scrollable_frame, text=line, wraplength=700, font=("Sans Serif", 12))
            label.pack(anchor=tk.NW, padx=20, pady=10)


class BenchmarkWindow:
    def __init__(self, root, scores, params):
        self.root = root
        self.root.geometry("800x600")
        self.scores = scores
        self.params = params

        keys = list(self.scores.keys())
        w = .75
        num_bars = len(keys)
        bar_w = w / num_bars
        x_axis = list(range(len(self.scores[keys[0]]["train"])))

        self.selected_figure = 1

        # figure with train scores
        f1 = Figure(figsize=(7, 5), dpi=100)
        a = f1.add_subplot(111)
        for i, key in enumerate(keys):
            a.bar([x + i * bar_w for x in x_axis], self.scores[key]["train"], bar_w)
        
        a.legend(keys)
        a.set_title("Validation scores during training")
        a.set_yscale('log')
        a.set_xticks(x_axis)
        a.set_xticklabels(["Fold " + str(i+1) for i in x_axis])

        # figure with test scores
        f2 = Figure(figsize=(7,5), dpi=100)
        a = f2.add_subplot(111)
        for i, key in enumerate(keys):
            a.bar([x + i * bar_w for x in x_axis], self.scores[key]["validation"], bar_w)
        
        a.legend(keys)
        a.set_title("Test scores")
        a.set_yscale('log')
        a.set_xticks(x_axis)
        a.set_xticklabels(["Fold " + str(i+1) for i in x_axis])

        # figure with averages
        f3 = Figure(figsize=(7, 5), dpi=100)
        a = f3.add_subplot(111)
        w = 0.20
        
        for i, key in enumerate(keys):
            train = np.array(self.scores[key]["train"])
            valid = np.array(self.scores[key]["validation"])
            a.bar([x + i * w for x in range(2)], [np.mean(train), np.mean(valid)], w)
        a.set_yscale('log')
        a.legend(keys)
        a.set_title("Average MAEs of the models")
        a.set_xticks([0, 1])
        a.set_xticklabels(["Train set", "Validation set"])

        self.figures = [f1, f2, f3]
        
        container = ttk.Frame(self.root)
        container.pack(side=tk.TOP, fill=tk.X, expand=True)

        # left navigation button
        button1 = ttk.Button(self.root, text="<", command=lambda: self.switch_figures(-1))
        button1.pack(in_=container, side=tk.LEFT)

        # right navigation button
        button2 = ttk.Button(self.root, text=">", command=lambda: self.switch_figures(+1))
        button2.pack(in_=container, side=tk.LEFT)

        # Export plots button
        button3 = ttk.Button(self.root, text="Export plots", command=self.export_plots)
        button3.pack(in_=container, side=tk.LEFT)

        # Generate report button
        button4 = ttk.Button(self.root, text="Generate report", command=self.generate_report)
        button4.pack(in_=container, side=tk.LEFT)

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
            fig.savefig(os.path.join(path, "figure_" + str(i) + ".png"), dpi=300, bbox_inches="tight")

    def generate_report(self):
        for fig in self.figures:
            FigureCanvasTkAgg(fig)

        path = tk.filedialog.askdirectory(title="Select the directory to save the report")

        generator = ReportGenerator(out_path=path)
        generator.generate_report(self.scores, self.params, self.figures)

