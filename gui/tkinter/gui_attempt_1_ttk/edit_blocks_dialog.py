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
import copy
from tkinter import ttk
from tkinter.messagebox import showinfo

import py_block_diagram as pybd
pad_options = {'padx': 5, 'pady': 5}

from tkinter_utils import my_toplevel_window, \
     window_with_param_widgets_that_appear_and_disappear, \
     value_from_str

class edit_blocks_dialog(my_toplevel_window, window_with_param_widgets_that_appear_and_disappear):
    def __init__(self, parent, title="Edit Block Dialog"):
        super().__init__(parent, title=title, geometry="300x700")
        self.bd = self.parent.bd
        self.max_params = 6#not counting variable_name and label
        self.make_widgets()


    def make_widgets(self):
        #def body(self):
        #print("frame: %s" % frame)
        # print(type(frame)) # tkinter.Frame
        self.block_names = self.bd.block_name_list
        
        #=================================
        #
        # column 0 
        #
        #=================================
        self.label1 = ttk.Label(self, text="Block")
        mycol = 0
        currow = 0
        self.make_label_and_grid_sw("Block", currow, mycol)
        currow += 1
        self.make_combo_and_var_grid_nw("block_selector", currow, mycol)
        currow += 1
        self.block_selector_combobox['values'] =  self.block_names
        self.block_selector_combobox.bind('<<ComboboxSelected>>', self.on_block_selected)
        
        self.required_attrs = ['variable_name','label']
        self.numbered_attrs = ["param%i" % i for i in range(1,self.max_params+1)]
        all_attrs = self.required_attrs + self.numbered_attrs
        
        for attr in all_attrs:
            # make a label and an entry box for each thing in the list
            label_attr = attr + "_label"
            self.make_label_and_grid_sw(attr, currow, mycol, attr=label_attr)
            currow += 1
            basename = attr
            self.make_entry_and_var_grid_nw(basename, currow, mycol)
            currow += 1

        self.save_changes_btn = self.make_button_and_grid("Save Changes", currow, mycol, \
                                                          command=self.on_save_changes_btn)
        currow += 1

        self.cancel_btn = self.make_button_and_grid("Cancel", currow, mycol, \
                                                    command=self.on_cancel_btn)
        currow += 1


    def populate_required_variable_boxes(self, block_instance):
        for attr in self.required_attrs:
            value = getattr(block_instance, attr)
            gui_attr = attr + '_var'
            gui_var = getattr(self, gui_attr)
            gui_var.set(str(value))


    def get_required_attrs_as_dict(self):
        mydict = {}
        for attr in self.required_attrs:
            gui_attr = attr + '_var'
            gui_var = getattr(self, gui_attr)
            value = gui_var.get()
            mydict[attr] = value
        return mydict
        


    def populate_params_boxes(self):
        self.update_param_labels(self.other_params)
        self.set_default_params(self.other_params, self.block_kwargs)
        self.N_params = len(self.other_params)
        N_unused = self.max_params - self.N_params
        self.hide_unsed_widgets(N_unused)
        self.unhide_used_widgets(self.N_params)
        

    def build_block_kwargs(self, block_instance):
        all_block_keys = ['variable_name', 'label'] + block_instance.py_params
        all_kwargs_for_block = {}
        for key in all_block_keys:
            value = getattr(block_instance, key)
            all_kwargs_for_block[key] = value
        return all_kwargs_for_block
    
        
    def on_block_selected(self, *args, **kwargs):
        block_name = self.block_selector_var.get()
        print("selected block name: %s" % block_name)
        block_instance = self.bd.get_block_by_name(block_name)
        self.populate_required_variable_boxes(block_instance)
        self.selected_block = block_instance
        # next steps:
        # - get numbered params, update the labels and populate the boxes
        # - hide unused boxes
        # - save initial values
        self.other_params = block_instance.py_params#<-- or param_list
        self.block_kwargs = {}
        for key in self.other_params:
            value = getattr(block_instance, key)
            self.block_kwargs[key] = value

        self.populate_params_boxes()
        self.original_kwargs = self.build_block_kwargs(block_instance)


    def on_save_changes_btn(self, *args, **kwargs):
        # approach:
        # - read the values from the widgets (done)
        # - see which values have changed (done)
        # - assign the changes to the block params
        # - deal with variable name changes if they have occured
        #     - how do we check for any blocks that have this block as an input?
        # - what happens if the user changed a sensor or actuator name?
        #     - do we want to make this impossible?
        #     - do we want to show comboxes for these
        other_kwargs = self.get_params_kwargs(self.N_params)
        kwargs = self.get_required_attrs_as_dict()
        kwargs.update(other_kwargs)
        self.new_kwargs = kwargs
        print("new_kwargs = %s" % self.new_kwargs)

        for key, value in self.original_kwargs.items():
            new_value = self.new_kwargs[key]
            if new_value != value:
                print("this changed: %s, %s --> %s" % (key, value, new_value))
                new_value = value_from_str(new_value)
                setattr(self.selected_block, key, new_value)
                if key == "variable_name":
                    self.bd.change_block_name(self.selected_block, new_value, value)
                    self.parent.block_list_var.set(self.bd.block_name_list)

        self.destroy()
                

    def on_cancel_btn(self, *args, **kwargs):
        print("in on_cancel_btn")
        self.destroy()
