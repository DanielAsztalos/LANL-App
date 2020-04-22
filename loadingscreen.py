import tkinter as tk
from tkinter import HORIZONTAL, CENTER, StringVar
from tkinter.ttk import Progressbar, Label, Button
from time import sleep

window = tk.Tk()

window.geometry("200x100")
window.columnconfigure(0, weight=1)

var = StringVar()
message = Label(window, anchor=CENTER, textvariable=var)
var.set("lol")
message.grid(row=0, column=0, padx=10, pady=5)

bar = Progressbar(window, orient=HORIZONTAL, length=180, mode='determinate')
bar.grid(row=1, column=0, padx=10, pady=5)

def cancel_action():
    window.destroy()

cancel = Button(window, command=cancel_action, text="Cancel")
cancel.grid(row=2, column=0)


window.mainloop()