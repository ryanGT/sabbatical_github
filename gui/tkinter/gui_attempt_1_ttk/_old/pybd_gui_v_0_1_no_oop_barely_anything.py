"""
===============
Embedding in Tk
===============

"""

import tkinter
import tkinter as tk
from tkinter import ttk

#from matplotlib.backends.backend_tkagg import (
#    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

import numpy as np


root = tkinter.Tk()
root.wm_title("Embedding in Tk")

root.columnconfigure(0, weight=3)
root.columnconfigure(1, weight=1)
root.rowconfigure(0, weight=3)

btn = ttk.Label(root, text='A simple plot')
btn.grid(row=0, column=1, padx=20, pady=10)

fig = Figure(figsize=(9, 6), dpi=100)
t = np.arange(0, 3, .01)
ax = fig.add_subplot(111)
ax.plot(t, 2 * np.sin(2 * np.pi * t))

#canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
#canvas.draw()
##canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
#canvas.get_tk_widget().grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=0, ipadx=40, ipady=20)

#toolbar = NavigationToolbar2Tk(canvas, root)
#toolbar.update()
#canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
#toolbar.get_tk_widget().grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

# navigation toolbar
toolbarFrame = ttk.Frame(master=root)
toolbarFrame.grid(row=1,column=0)
toolbar = NavigationToolbar2Tk(canvas, toolbarFrame)


#column=0, row=0, sticky=tk.W, padx=5, pady=5)
ax.set_xlim([0,0.5])

def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, toolbar)


canvas.mpl_connect("key_press_event", on_key_press)

def onclick(event):
    print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          ('double' if event.dblclick else 'single', event.button,
           event.x, event.y, event.xdata, event.ydata))

cid = canvas.mpl_connect('button_press_event', onclick)


def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


button = ttk.Button(master=root, text="Quit", command=_quit)
#button.pack(side=tkinter.BOTTOM)
button.grid(column=1, row=1, sticky=tk.W, padx=5, pady=5)

#w = 1200 # width for the Tk root
#h = 1000 # height for the Tk root
w = 800
h = 600
x = 100
y = 100
#root.geometry('%dx%d+%d+%d' % (w, h, x, y))
root.geometry('%dx%d' % (w, h))
#root.state('zoomed')
tkinter.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.
