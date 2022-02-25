import tkinter
import tkinter as tk
from tkinter import ttk

from tkinter import ttk
from tkinter.messagebox import showinfo

from tkinter_utils import my_toplevel_window

import py_block_diagram as pybd

import copy

class input_chooser(my_toplevel_window):
    def __init__(self, block, parent, title="Input Chooser Dialog", \
                 geometry='300x200'):        
        super().__init__(parent, title=title, geometry=geometry)
        self.bd = self.parent.block_diagram
        self.columnconfigure(0, weight=4)
        self.block = block
        self.make_widgets()


    def make_widgets(self):
        mycol = 0
        block_name = self.block.variable_name
        main_label = "Choose the input for block: %s" % block_name
        self.make_label_and_grid_sw(main_label, 0, mycol)
        self.make_combo_and_var_grid_nw("input_chooser", 1, mycol)
        self.all_block_names = self.bd.block_name_list
        myind = self.all_block_names.index(block_name)
        self.other_block_names = copy.copy(self.all_block_names)
        self.other_block_names.pop(myind)
        self.input_chooser_combobox['values'] =  self.other_block_names
        #self.input_chooser_combobox.bind('<<ComboboxSelected>>', self.input_combo_selected)
        
        # go button
        self.go_button = self.make_button_and_grid("Set Input", 10, mycol, \
                                                   command=self.on_go_button)


    def on_go_button(self, *args, **kwargs):
        print("on_go_button pressed")
        input_name = self.input_chooser_var.get()
        print("input_name: %s" % input_name)
        input_block = self.bd.get_block_by_name(input_name)
        self.block.set_input_block1(input_block)
        self.destroy()
        # - get name from combobox
        # - get the selected block by name
        # - call the set input method of self.block
        # - handle second input if applicable
