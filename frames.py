import tkinter as tk
import tkinter.ttk as ttk
from paramloader import ParamLoader
from functools import partial
from tasks import SearchParams, CheckSearch, TrainAndTest
from multiprocessing import Queue
from models import get_model
import threading
import numpy as np

class ParamSelectionFrame(tk.Frame):
    def __init__(self, parent, shared):
        tk.Frame.__init__(self, parent)
        self.name = "Model selection"
        self.shared = shared

        self.top_bar = tk.Frame(self)
        self.top_bar.pack(anchor=tk.NW, padx=10, pady=10)

        self.label = tk.Label(self, text="Choose a model")
        self.label.pack(in_=self.top_bar, side=tk.LEFT, padx=10, pady=5, anchor=tk.NW)

        self.paramloader = ParamLoader()
        model_names = self.paramloader.get_model_names()

        self.tkvar = tk.StringVar()
        self.tkvar.set(model_names[0])

        self.shared.selected_model_lock.acquire()
        self.shared.selected_model = model_names[0]
        self.shared.selected_model_lock.release()

        self.dropdown = tk.OptionMenu(self, self.tkvar, *model_names, command=partial(self.model_selection_change))
        self.dropdown.pack(in_=self.top_bar, side=tk.TOP, padx=10, pady=5, anchor=tk.NW)

        self.search_button = tk.Button(self, text="Search for the best parameters", command=self.search_task)
        self.search_button.pack(in_=self.top_bar, side=tk.TOP, padx=10, pady=5)

        grid, types = self.paramloader.get_param_grid(model_names[0])

        self.content = ParameterTemplateFrame(self, grid, types, self.shared)
        self.content.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
   

    def get_name(self):
        return self.name

    def model_selection_change(self, name):
        grid, types = self.paramloader.get_param_grid(name)
        new_content = ParameterTemplateFrame(self, grid, types, self.shared)
        if self.content is not None:
            self.content.destroy()
        self.content = new_content
        self.content.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.shared.selected_model_lock.acquire()
        self.shared.selected_model = name
        self.shared.selected_model_lock.release()

    def search_task(self):
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
    

class ModelTrainingFrame(tk.Frame):
    def __init__(self, parent, shared):
        tk.Frame.__init__(self, parent)
        
        self.name = "Training model"
        self.shared = shared

        label1 = tk.Label(self, text="Train and test parameters")
        label1.pack(side=tk.TOP, anchor=tk.NW, padx=10, pady=10)

        test_size = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
        cv_num = [3, 5, 7, 9]
        labels = ["Test size", "Number of folds"]
        values = [test_size, cv_num]
        self.widgets = []

        for val, label in zip(values, labels):
            container = tk.Frame(self)
            container.pack(anchor=tk.NW, padx=10, pady=10)

            label = tk.Label(self, text=label)
            label.pack(in_=container, anchor=tk.NW)

            spinner = tk.Spinbox(self, values=val)
            spinner.pack(in_=container, anchor=tk.NW)
            self.widgets.append(spinner)

        start_train = tk.Button(self, text="Start training", command=self.train_task)
        start_train.pack(side=tk.TOP, anchor=tk.NW, padx=10, pady=10)

        self.table = ttk.Treeview(self, columns=('mean_abs_error'))
        self.table.heading('mean_abs_error', text="Mean abs error")
        self.table.pack(side=tk.TOP, anchor=tk.NW, padx=10, pady=30)

    def get_name(self):
        return self.name

    def train_task(self):
        queue = Queue()
        train_task = TrainAndTest(self.shared, queue, int(self.widgets[1].get()), float(self.widgets[0].get()))
        p1 = threading.Thread(target=(lambda : train_task.execute()))
        p1.start()

        self.shared.state_lock.acquire()
        self.shared.state.set("Searching for the optimal parameters")
        self.shared.state_lock.release()

        check_task = CheckSearch(p1, queue, self.shared, self.after_train)
        p2 = threading.Thread(target=(lambda : check_task.execute()))
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

class ParameterTemplateFrame(tk.Frame):
    def __init__(self, parent, grid, types, shared):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.shared = shared

        canvas = tk.Canvas(self)

        scrollbar = tk.Scrollbar(self, orient='vertical', command=canvas.yview)

        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.widgets = []
        self.specials = []
        self.labels = []
        l = 0
        x = True
        defaults = self.parent.paramloader.load_defaults()
        defaults = defaults[self.parent.tkvar.get()]

        self.shared.param_grid_lock.acquire()
        self.shared.param_grid = defaults
        self.shared.param_grid_lock.release()

        for i, param in enumerate(grid.keys()):
            self.labels.append(param)

            container = tk.Frame(self.scrollable_frame)
            container.pack(anchor=tk.NW, padx=10, pady=10)

            label = tk.Label(self.scrollable_frame, text=param)
            label.pack(in_=container, anchor=tk.NW)

            if types[i] == 0:
                tkVar = tk.StringVar()
                tkVar.set(defaults[param])
                widget = tk.OptionMenu(self.scrollable_frame, tkVar, *grid[param])
                widget.pack(in_=container, anchor=tk.NW)
                self.widgets.append(tkVar)

            elif types[i] == 1:
                widget = tk.Spinbox(self.scrollable_frame, values=grid[param])
                while widget.get() != str(defaults[param]):
                    widget.invoke("buttonup")
                widget.pack(in_=container, anchor=tk.NW)
                self.widgets.append(widget)

            else:
                var = tk.StringVar()
                var.set(str(defaults[param]))
                widget = tk.Spinbox(self.scrollable_frame, textvariable=var, values=grid[param])
                widget.pack(in_=container, anchor=tk.NW)

                if x == True:
                    x = False
                else:
                    for _ in range(5):
                        widget.invoke("buttonup")
                    x = True
                self.widgets.append(widget)
                widget.config(command=partial(self.special_action, l))

                l +=1
                self.specials.append(self.widgets.index(widget))

        save_settings = tk.Button(self.scrollable_frame, text="Save settings as default", command=self.save_params)
        save_settings.pack(anchor=tk.NW, padx=10, pady=10)

            
    def save_params(self):
        name = self.parent.tkvar.get()
        params = dict()
        params[name] = dict()

        for i in range(len(self.labels)):
            params[name][self.labels[i]] = self.widgets[i].get()
        
        self.parent.paramloader.modify_defaults(params)

    def special_action(self, idx):
        val1 = float(self.widgets[self.specials[0]].get())
        val2 = float(self.widgets[self.specials[1]].get())

        if idx == self.specials[0]:
            if val1 + val2 < 1.0:
                self.widgets[self.specials[1]].config(command=lambda: 1)
                self.widgets[self.specials[1]].invoke("buttonup")
                self.widgets[self.specials[1]].config(command=partial(self.special_action, 1))
            elif val1 + val2 > 1.0:
                self.widgets[self.specials[1]].config(command=lambda: 1)
                self.widgets[self.specials[1]].invoke("buttondown")
                self.widgets[self.specials[1]].config(command=partial(self.special_action, 1))
        else:
            if val1 + val2 < 1.0:
                self.widgets[self.specials[0]].config(command=lambda: 1)
                self.widgets[self.specials[0]].invoke("buttonup")
                self.widgets[self.specials[0]].config(command=partial(self.special_action, 0))
            elif val1 + val2 > 1.0:
                self.widgets[self.specials[0]].config(command=lambda: 1)
                self.widgets[self.specials[0]].invoke("buttondown")
                self.widgets[self.specials[0]].config(command=partial(self.special_action, 0))