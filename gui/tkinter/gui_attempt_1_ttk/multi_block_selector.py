import tkinter
import tkinter as tk
from tkinter import ttk

from tkinter import ttk
from tkinter.messagebox import showinfo

from tkinter_utils import my_toplevel_window

import py_block_diagram as pybd

import copy

class multi_block_selector(my_toplevel_window):
    def __init__(self, parent, title="Input Chooser Dialog", \
                 geometry='300x200', selected_index=0, main_label_text="hello"):        
        super().__init__(parent, title=title, geometry=geometry)
        self.bd = self.parent.bd
        self.columnconfigure(0, weight=4)
        self.main_label_text = main_label_text
        self.set_all_blocks()
        self.make_widgets()


    def set_all_blocks(self):
        """All might not necessarily mean all...."""
        self.all_block_names = self.bd.block_name_list
        

    def make_widgets(self):
        mycol = 0
        self.make_label_and_grid_sw(self.main_label_text, 0, mycol)
        self.make_label_and_grid_sw("Blocks", 1, mycol)
        self.make_listbox_and_var("blocklist", 2, mycol, selectmode="multiple")
        self.blocklist_var.set(self.all_block_names)

        # go button
        self.go_button = self.make_button_and_grid("Done", 10, mycol, \
                                                   command=self.on_go_button)


    def on_go_button(self, *args, **kwargs):
        raise NotImplementedError



class print_block_selector(multi_block_selector):
    """Plants with two outputs do not work as print blocks, but
    sensors can also be print blocks."""
    def set_all_blocks(self):
        all_block_names = self.bd.block_name_list

        printable_blocks = []
        for block_name in all_block_names:
            block = self.bd.get_block_by_name(block_name)
            if not isinstance(block, pybd.plant_with_double_actuator_two_sensors):
                printable_blocks.append(block_name)

        # append all sensor names (might need to revisit later)
        printable_blocks += self.bd.sensor_name_list
        self.all_block_names = printable_blocks


    def on_go_button(self, *args, **kwargs):
        print("on_go_button pressed")
        selected_indices = self.blocklist_listbox.curselection()
        #print("selected_indices:")
        block_name_list = []
        for item in selected_indices:
            curname = self.blocklist_listbox.get(item)
            block_name_list.append(curname)
        print("block_name_list:" + str(block_name_list))
        self.bd.set_print_blocks_from_names(block_name_list)
        self.destroy()
        # - get name from combobox
        # - get the selected block by name
        # - call the set input method of self.block
        # - handle second input if applicable
