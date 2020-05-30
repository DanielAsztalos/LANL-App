import tkinter as tk
import tkinter.ttk as ttk
from paramloader import ParamLoader
from functools import partial
from tasks import SearchParams, CheckSearch, TrainAndTest, BenchmarkModels
from multiprocessing import Queue
from models import get_model
from mainwindow import BenchmarkWindow
import threading
import numpy as np
import Pmw

# displayed on the left side of the main window
class ParamSelectionFrame(ttk.Frame):
    def __init__(self, parent, shared):
        ttk.Frame.__init__(self, parent)
        self.name = "Model selection"
        self.shared = shared

        self.top_bar = ttk.Frame(self)
        self.top_bar.pack(anchor=tk.NW, padx=10, pady=10)

        self.label = ttk.Label(self, text="Choose a model")
        self.label.pack(in_=self.top_bar, side=tk.LEFT, padx=10, pady=5, anchor=tk.NW)

        self.paramloader = ParamLoader()
        model_names = self.paramloader.get_model_names()

        self.tkvar = tk.StringVar()
        self.tkvar.set(model_names[0])

        self.shared.selected_model_lock.acquire()
        self.shared.selected_model = model_names[0]
        self.shared.selected_model_lock.release()

        self.dropdown = ttk.OptionMenu(self, self.tkvar, model_names[0], *model_names, command=partial(self.model_selection_change))
        self.dropdown.pack(in_=self.top_bar, side=tk.TOP, padx=10, pady=5, anchor=tk.NW)

        self.search_button = ttk.Button(self, text="Search for the best parameters", command=self.search_task)
        self.search_button.pack(in_=self.top_bar, side=tk.TOP, padx=10, pady=5)

        grid, types = self.paramloader.get_param_grid(model_names[0])
        hints = self.paramloader.get_hints_of_model(model_names[0])

        self.content = ParameterTemplateFrame(self, grid, types, self.shared, hints)
        self.content.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
   

    def get_name(self):
        return self.name

    def model_selection_change(self, name):
        grid, types = self.paramloader.get_param_grid(name)
        hints = self.paramloader.get_hints_of_model(name)
        new_content = ParameterTemplateFrame(self, grid, types, self.shared, hints)
        if self.content is not None:
            self.content.destroy()
        self.content = new_content
        self.content.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.shared.selected_model_lock.acquire()
        self.shared.selected_model = name
        self.shared.selected_model_lock.release()

    def search_task(self):
        self.shared.state_lock.acquire()
        self.shared.state.set("Searching for the optimal parameters")
        self.shared.state_lock.release()

        queue = Queue()
        grid, _ = self.paramloader.get_param_grid(self.shared.selected_model)
        search_task = SearchParams(get_model(self.shared.selected_model), grid, queue, self.shared.selected_model)
        p1 = threading.Thread(target=(lambda : search_task.execute()))
        p1.start()

        check_task = CheckSearch(p1, queue, self.shared, self.after_search)
        p2 = threading.Thread(target=(lambda : check_task.execute()))
        p2.start()

    def after_search(self, queue):
        grid = queue.get()
        pl = ParamLoader()
        pl.modify_defaults(grid)

        self.model_selection_change((list(grid.keys())[0]))
    
# displayed on the right side of the window
class ModelTrainingFrame(ttk.Frame):
    def __init__(self, parent, shared):
        ttk.Frame.__init__(self, parent)
        
        self.name = "Training model"
        self.shared = shared

        tooltip = Pmw.Balloon(parent)

        label1 = ttk.Label(self, text="Train and test parameters")
        label1.pack(side=tk.TOP, anchor=tk.NW, padx=10, pady=10)

        test_size = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        cv_num = [3, 5, 7, 9]
        labels = ["Test size", "Number of folds"]
        hints = ["The percentage of the train data that should be reserved for testing. Type: float between 0.0 and 1.0.", 
                "The number of folds for KFold validation. Type: integer (odd number)."]
        values = [test_size, cv_num]
        self.widgets = []

        for (i, val), label in zip(enumerate(values), labels):
            container = ttk.Frame(self)
            container.pack(anchor=tk.NW, padx=10, pady=10)

            label = ttk.Label(self, text=label)
            label.pack(in_=container, anchor=tk.NW)
            tooltip.bind(label, hints[i])

            spinner = tk.Spinbox(self, values=val)
            spinner.pack(in_=container, anchor=tk.NW)
            self.widgets.append(spinner)

        self.upload_selected = tk.IntVar()
        check_box = ttk.Checkbutton(self, text="Upload to kaggle", variable=self.upload_selected)
        check_box.pack(side=tk.TOP, anchor=tk.NW, padx=10)

        button_container = ttk.Frame(self)
        button_container.pack(side=tk.TOP, anchor=tk.NW, padx=10, pady=10)

        start_train = ttk.Button(self, text="Start training", command=self.train_task)
        start_train.pack(in_=button_container, side=tk.LEFT, anchor=tk.NW, padx=0, pady=0)
        tooltip.bind(start_train, "Train only the model selected on the model selection side.")

        benchmark = ttk.Button(self, text="Benchmark all models", command=self.benchmark_task)
        benchmark.pack(in_=button_container, side=tk.LEFT, anchor=tk.NW)

        label = ttk.Label(self, text="Results")
        label.pack(side=tk.TOP, anchor=tk.NW, padx=10, pady=20)
        tooltip.bind(label, "The results of the individual training processes are displayed in the box below.")

        self.table = ttk.Treeview(self, columns=('mean_abs_error'))
        self.table.heading('mean_abs_error', text="Mean abs error")
        self.table.pack(side=tk.TOP, anchor=tk.NW, padx=10, pady=0)

    def get_name(self):
        return self.name

    def train_task(self):
        queue = Queue()
        train_task = TrainAndTest(self.shared, queue, int(self.widgets[1].get()), float(self.widgets[0].get()), self.upload_selected.get())
        p1 = threading.Thread(target=(lambda : train_task.execute()))
        p1.start()

        check_task = CheckSearch(p1, queue, self.shared, self.after_train)
        p2 = threading.Thread(target=(lambda : check_task.execute()))
        p2.start()

    def benchmark_task(self):
        queue = Queue()
        task = BenchmarkModels(self.shared, queue, int(self.widgets[1].get()), float(self.widgets[0].get()))
        p1 = threading.Thread(target=lambda: task.execute())
        p1.start()

        check_task = CheckSearch(p1, queue, self.shared, self.after_benchmark)
        p2 = threading.Thread(target=lambda: check_task.execute())
        p2.start()

    def after_train(self, queue):
        results = queue.get()

        self.shared.state_lock.acquire()
        self.shared.state.set("Train finished!")
        self.shared.state_lock.release()

        try:
            self.table.delete('train')
            self.table.delete('test')
        except:
            pass

        self.table.insert('', 'end', 'train', text="Train scores", values=(np.mean(results["train_scores"])))
        for i, score in enumerate(results["train_scores"]):
            self.table.insert('train', 'end', text="Fold {}".format(i), values=(score))

        self.table.insert('', 'end', 'test', text="Test scores", values=(np.mean(results["test_scores"])))
        for i, score in enumerate(results["test_scores"]):
            self.table.insert('test', 'end', text="Fold {}".format(i), values=(score))

    def after_benchmark(self, queue):
        scores = queue.get()
        params = queue.get()

        self.new = tk.Toplevel(self.shared.root, bg="#F5F6F7")
        self.new.transient(self.shared.root)
        BenchmarkWindow(self.new, scores, params)

# embedded into the ParamSelection frame
class ParameterTemplateFrame(ttk.Frame):
    def __init__(self, parent, grid, types, shared, hints):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.shared = shared

        canvas = tk.Canvas(self, bg="#F5F6F7", highlightthickness=0)

        scrollbar = ttk.Scrollbar(self, orient='vertical', command=canvas.yview)

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

        self.widgets = []
        self.labels = []

        defaults = self.parent.paramloader.load_defaults()
        defaults = defaults[self.parent.tkvar.get()]

        self.shared.param_grid_lock.acquire()
        self.shared.param_grid = defaults
        self.shared.param_grid_lock.release()
        tooltip = Pmw.Balloon(self.parent)

        for i, param in enumerate(grid.keys()):
            self.labels.append(param)

            container = ttk.Frame(self.scrollable_frame)
            container.pack(anchor=tk.NW, padx=10, pady=10)

            label = ttk.Label(self.scrollable_frame, text=param)
            label.pack(in_=container, anchor=tk.NW)
            tooltip.bind(label, hints[i])

            if types[i] == 0:
                tkVar = tk.StringVar()
                tkVar.set(defaults[param])
                widget = ttk.OptionMenu(self.scrollable_frame, tkVar, grid[param][0], *grid[param])
                widget.pack(in_=container, anchor=tk.NW)
                self.widgets.append(tkVar)

            elif types[i] == 1:
                widget = tk.Spinbox(self.scrollable_frame, values=grid[param])
                while widget.get() != str(defaults[param]):
                    widget.invoke("buttonup")
                widget.pack(in_=container, anchor=tk.NW)
                self.widgets.append(widget)

        save_settings = ttk.Button(self.scrollable_frame, text="Save settings as default", command=self.save_params)
        save_settings.pack(anchor=tk.NW, padx=10, pady=10)

            
    def save_params(self):
        name = self.parent.tkvar.get()
        params = dict()
        params[name] = dict()

        for i in range(len(self.labels)):
            params[name][self.labels[i]] = self.widgets[i].get()
        
        self.parent.paramloader.modify_defaults(params)