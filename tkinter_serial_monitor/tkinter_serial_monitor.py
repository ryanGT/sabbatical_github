"""
This is a serial monitor gui that is intended to replace the standard
Arduino one and allow for easy graphing and other Python-based data
processing.
"""

############################################
#
# Next Steps:
#
# ----------------
#

#############################################

#iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
#
# Issues:
#
#
# Resovled:
#  
#iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii

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

from tkinter import ttk
from tkinter.messagebox import showinfo

import tkinter_utils

import os, txt_mixin

pad_options = {'padx': 5, 'pady': 5}



class tkinter_serial_gui(tk.Tk, tkinter_utils.abstract_window):
    def __init__(self):
        super().__init__()
        self.option_add('*tearOff', False)
        self.geometry("900x600")
        self.mylabel = 'Tkinter Python Serial GUI'
        self.title(self.mylabel)
        self.resizable(1, 1)

        # configure the grid
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(4, weight=2)

        self.options = {'padx': 5, 'pady': 5}

        ## self.menubar = tk.Menu(self)
        ## self['menu'] = self.menubar
        ## self.menu_file = tk.Menu(self.menubar)
        ## self.menu_edit = tk.Menu(self.menubar)
        ## self.menu_codegen = tk.Menu(self.menubar)        
        ## self.menubar.add_cascade(menu=self.menu_file, label='File')
        ## self.menubar.add_cascade(menu=self.menu_edit, label='Edit')
        ## self.menubar.add_cascade(menu=self.menu_codegen, label='Code Generation')        
        ## self.menu_file.add_command(label='Save', command=self.on_save_menu)
        ## self.menu_file.add_command(label='Load', command=self.on_load_menu)        
        ## #menu_file.add_command(label='Open...', command=openFile)
        ## self.menu_file.add_command(label='Quit', command=self._quit)
        ## self.menu_codegen.add_command(label='Set Arduino Template File', command=self.set_arduino_template)
        ## self.menu_codegen.add_command(label='Get Arduino Template File', command=self.get_arduino_template)
        ## self.menu_codegen.add_command(label='Set Arduino Output Path', \
        ##                               command=self.set_arduino_output_folder)
        ## self.menu_codegen.add_command(label='Generate Arduino Code', command=self.arduino_codegen)                

        ## #self.bind("<Key>", self.key_pressed)
        ## self.bind('<Control-q>', self._quit)
        ## self.bind('<Control-s>', self.on_save_menu)
        ## self.bind('<Control-l>', self.on_load_menu)
        ## self.bind('<Control-a>', self.add_block)
        ## self.bind('<Control-P>', self.on_place_btn)
        ## self.bind('<Alt-p>', self.on_place_btn)
        ## self.bind('<Control-d>', self.on_draw_btn)
        
        # configure the root window
        self.make_widgets()


    ## def key_pressed(self, event):
    ##     print("pressed:")
    ##     print(repr(event.char))


    ## def on_load_menu(self, *args, **kwargs):
    ##     print("in menu laod")
    ##     filename = tk.filedialog.askopenfilename(title = "Select Model to Load (CSV)",\
    ##                                              filetypes = (("csv files","*.csv"),("all files","*.*")))
    ##     print (filename)
    ##     if filename:
    ##         new_bd = pybd.load_model_from_csv(filename)
    ##         self.bd = new_bd
    ##         self.block_list_var.set(self.bd.block_name_list)
            
    
    ## def on_save_menu(self, *args, **kwargs):
    ##     print("in menu save")
    ##     filename = tk.filedialog.asksaveasfilename(title = "Select filename",\
    ##                                                filetypes = (("csv files","*.csv"),("all files","*.*")))
    ##     print (filename)
    ##     if filename:
    ##         self.bd.save_model_to_csv(filename)
    def _quit(self, *args, **kwargs):
        print("in _quit")
        #self.save_params()
        self.quit()     # stops mainloop
        self.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate


    def make_widgets(self):
        # don't assume that self.parent is a root window.
        # instead, call `winfo_toplevel to get the root window
        #self.winfo_toplevel().title("Simple Prog")
        #self.wm_title("Python Block Diagram GUI")        


        # column 0
        mycol = 0
        self.make_label_and_grid_sw("Send Text", 0, mycol)
        self.make_entry_and_var_grid_nw("send_text", 1,mycol, sticky='new')
        self.send_button = self.make_button_and_grid("Transmit", 2, mycol, \
                                                     command=None, sticky='e')
        self.make_label_and_grid_sw("Received Text", 3, mycol)
        self.make_entry_and_var_grid_nw("receive_text", 4,mycol, sticky='news')


        # column 1
        mycol = 1
        self.make_label_and_grid_sw("Portname", 0, mycol)
        self.make_entry_and_var_grid_nw("portname", 1,mycol, sticky='new')


        ## self.fig = Figure(figsize=(9, 6), dpi=100)
        ## t = np.arange(0, 3, .01)
        ## self.ax = self.fig.add_subplot(111)
        ## self.ax.plot(t, 2 * np.sin(2 * np.pi * t))
        ## self.ax.set_xlim([0,0.5])

        ## self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        ## self.canvas.draw()
        ## self.canvas.get_tk_widget().grid(row=1, column=0, ipadx=40, ipady=20, \
        ##                                  sticky="news")#, rowspan=16)

        ## self.toolbarFrame = ttk.Frame(master=self)
        ## self.toolbarFrame.grid(row=19,column=0)
        ## self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)


        ## self.button_frame1 = ttk.Frame(self)
        ## self.quit_button = ttk.Button(self.button_frame1, text="Quit", command=self._quit)
        ## self.quit_button.grid(column=0, row=0, **self.options)

        ## self.draw_button = ttk.Button(self.button_frame1, text="Draw", command=self.on_draw_btn)
        ## self.draw_button.grid(column=1, row=0, **self.options)

        ## self.xlim_label = ttk.Label(self.button_frame1, text="xlim:")
        ## self.xlim.grid(row=0,column=2,sticky='E')
        ## self.xlim_var = tk.StringVar()
        ## self.xlim_box = ttk.Entry(self.button_frame1, textvariable=self.xlim_var)
        ## self.xlim_box.grid(column=3, row=0, sticky="W", padx=(0,5))

        
        ##self.button_frame1.grid(row=20, column=0)

    ## def on_draw_btn(self, *args, **kwargs):
    ##     print("you pressed draw")
    ##     self.ax.clear()
    ##     self.bd.update_block_list()
    ##     block_list = self.bd.block_list
    ##     print("block_list: %s" % block_list)
    ##     self.bd.ax = self.ax
    ##     self.bd.draw()
    ##     xlims = self.bd.get_xlims()
    ##     ylims = self.bd.get_ylims()
    ##     self.ax.set_xlim(xlims)
    ##     self.ax.set_ylim(ylims)
    ##     self.bd.axis_off()        
    ##     self.canvas.draw()
        
        
if __name__ == "__main__":
    app = tkinter_serial_gui()
    app.mainloop()
