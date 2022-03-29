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

import py_block_diagram as pybd
pad_options = {'padx': 5, 'pady': 5}

class place_block_dialog(tk.Toplevel):
    def __init__(self, parent, title="Place Block Dialog"):
        super().__init__(parent)
        self.parent = parent
        self.geometry('400x600')
        self.title(title)
        self.make_widgets()



    def make_label(self, text):
        widget = ttk.Label(self, text=text)
        return widget


    def grid_label_sw(self, widget, row, col):
        widget.grid(row=row, column=col, sticky='SW', pady=(5,1), padx=10)


    def grid_widget(self, widget, row, col, padx=10, pady=5, **kwargs):
        widget.grid(row=row, column=col, padx=padx, pady=pady, **kwargs)


    def grid_box_nw(self, widget, row, col):
        widget.grid(row=row,column=col,sticky='NW', pady=(1,5), padx=10)


    def make_label_and_grid_sw(self, text, row, col):
        widget = self.make_label(text)
        self.grid_label_sw(widget, row, col)
        return widget


    def make_widget_and_var_grid_nw(self, basename, row, col, type="entry"):
        myvar = tk.StringVar()
        if type.lower() == 'entry':
            widget_class = ttk.Entry
            tail = '_entry'
        elif 'combo' in type.lower():
            widget_class = ttk.Combobox
            tail = '_combobox'
            
        mywidget = widget_class(self, textvariable=myvar)
        self.grid_box_nw(mywidget, row, col)
        var_attr = basename + '_var'
        setattr(self, var_attr, myvar)
        widget_attr = basename + tail
        setattr(self, widget_attr, mywidget)
        return mywidget
    

    def make_entry_and_var_grid_nw(self, basename, row, col):
        return self.make_widget_and_var_grid_nw(basename, row, col, type="entry")
        ## myvar = tk.StringVar()
        ## myentry = ttk.Entry(self, textvariable=myvar)
        ## self.grid_box_nw(myentry, row, col)
        ## var_attr = basename + '_var'
        ## setattr(self, var_attr, myvar)
        ## entry_attr = basename + '_entry'
        ## setattr(self, entry_attr, myentry)


    def make_combo_and_var_grid_nw(self, basename, row, col):
        return self.make_widget_and_var_grid_nw(basename, row, col, type="combobox")        
    
                                   
    def make_widgets(self):
        #def body(self):
        #print("frame: %s" % frame)
        # print(type(frame)) # tkinter.Frame
        
        #=================================
        #
        # column 0 
        #
        #=================================
        curcol = 0

        # Block to place
        self.label1 = self.make_label_and_grid_sw("Block to Place", 0, curcol)
        
        self.block_to_place_var = tk.StringVar()
        self.block_to_place_combobox = ttk.Combobox(self, textvariable=self.block_to_place_var)

        self.block_to_place_combobox['values'] = self.parent.get_block_name_list()
        self.grid_box_nw(self.block_to_place_combobox, 1, curcol)

        # Placement type
        self.label2 = self.make_label_and_grid_sw("Placement Type", 2, curcol)
        self.placement_type_var = tk.StringVar()
        self.placement_type_combobox = ttk.Combobox(self, textvariable=self.placement_type_var)

        self.placement_type_combobox['values'] = ['absolute','relative']
        self.grid_box_nw(self.placement_type_combobox, 3, curcol)

        self.placement_type_combobox.bind('<<ComboboxSelected>>', self.on_placement_type_selected)

        # Abs placement widgets
        self.label3 = self.make_label_and_grid_sw("abs x", 4, curcol)
        self.make_entry_and_var_grid_nw("abs_x", 5, curcol)


        self.label4 = self.make_label_and_grid_sw("abs y", 6, curcol)
        self.make_entry_and_var_grid_nw("abs_y", 7, curcol)

        self.abs_widgets = [self.label3, self.label4, self.abs_x_entry, self.abs_y_entry]
        

        # Relative Placement Widgets
        self.label5 = self.make_label_and_grid_sw("Relative Block", 4, curcol)
        self.make_combo_and_var_grid_nw("relative_block", 5, curcol)
        self.relative_block_combobox['values'] = self.parent.get_block_name_list()

        self.label6 = self.make_label_and_grid_sw("Relative Direction", 6, curcol)
        self.make_combo_and_var_grid_nw("relative_direction", 7, curcol)
        self.relative_direction_combobox['values'] = ['right','left','above','below']


        self.rel_dist_label = self.make_label_and_grid_sw("Relative Distance", 8, curcol)
        self.make_entry_and_var_grid_nw("rel_dist", 9, curcol)

        # xshift and yshift for relative placement
        self.xshift_label = self.make_label_and_grid_sw("x shift", 10, curcol)
        self.make_entry_and_var_grid_nw("xshift", 11, curcol)
        self.yshift_label = self.make_label_and_grid_sw("y shift", 12, curcol)
        self.make_entry_and_var_grid_nw("yshift", 13, curcol)
                
        self.relative_widgets = [self.label5, self.label6, self.relative_block_combobox, \
                                 self.relative_direction_combobox, \
                                 self.rel_dist_label, self.rel_dist_entry, \
                                 self.xshift_label, self.xshift_entry, \
                                 self.yshift_label, self.yshift_entry, \
                                 ]

        

        
        # go button
        self.go_button = ttk.Button(self, text='Place Block', command=self.go_pressed)
        self.grid_widget(self.go_button, 15, curcol)


        # setup for relative placement default
        self.set_defaults()
        self.hide_abs_widgets()
        self.unhide_relative_widgets()


    def set_defaults(self):
        print("setting defaults")
        self.placement_type_var.set("relative")
        self.relative_direction_var.set("right")
        self.rel_dist_var.set("4")
        self.xshift_var.set("0")
        self.yshift_var.set("0")        


    def set_widgets_to_block(self, block):
        print("setting widgets to block values")
        self.placement_type_var.set(block.placement_type)
        self.relative_block_var.set(block.rel_block_name)
        self.relative_direction_var.set(block.rel_pos)
        self.rel_dist_var.set(str(block.rel_distance))
        self.xshift_var.set(str(block.xshift))
        self.yshift_var.set(str(block.yshift))
        

    def set_block_to_place(self, block_name):
        self.block_to_place_var.set(block_name)
        block = self.parent.get_block_by_name(block_name)
        if block.placement_type:
            self.set_widgets_to_block(block)
        else:
            self.set_defaults()

    def go_pressed(self, *args, **kwargs):
        place_type = self.placement_type_var.get()
        print("place_type:")
        print(place_type)
        if not place_type:
            # do nothing
            print("doing nothing")
            return

        block_name = self.block_to_place_var.get()
        block = self.parent.get_block_by_name(block_name)
        
        if place_type == "absolute":
            print("going absolute")
            block.placement_type = "absolute"
            block.abs_x = float(self.abs_x_var.get())
            block.abs_y = float(self.abs_y_var.get())
            block.place_absolute(block.abs_x, block.abs_y)
        else:
            print("relative placement")
            #place_relative(self, rel_block, rel_pos='right', ref_distance=4, xshift=0, yshift=0):
            rel_block_name = self.relative_block_var.get()
            rel_block = self.parent.get_block_by_name(rel_block_name)
            rel_pos = self.relative_direction_var.get()
            rel_dist = float(self.rel_dist_var.get())
            xshift = self.xshift_var.get()
            if not xshift:
                xshift = 0
            else:
                xshift = float(xshift)
                
            yshift = self.yshift_var.get()
            if not yshift:
                yshift = 0
            else:
                yshift = float(yshift)
                
            block.placement_type = "relative"
            block.place_relative(rel_block=rel_block, rel_pos=rel_pos, rel_distance=rel_dist, \
                                 xshift=xshift, yshift=yshift)

        block_place_str = block.get_placememt_str()
        print("block_place_str: %s" % block_place_str)
        self.parent.fill_placement_entry(block_place_str)
            
        self.destroy()

    def cancel_pressed(self):
        # print("cancel")
        self.destroy()



    def _hide_widgets(self, widget_list):
        for widget in widget_list:
            widget.grid_remove()

            
    def _unhide_widgets(self, widget_list):
        for widget in widget_list:
            widget.grid()


    def hide_abs_widgets(self):
        self._hide_widgets(self.abs_widgets)


    def hide_relative_widgets(self):
        self._hide_widgets(self.relative_widgets)


    def unhide_abs_widgets(self):
        self._unhide_widgets(self.abs_widgets)


    def unhide_relative_widgets(self):
        self._unhide_widgets(self.relative_widgets)


    def on_placement_type_selected(self, *args, **kwargs):
        place_type = self.placement_type_var.get()
        if not place_type:
            # do nothing
            return
        if place_type == "absolute":
            self.unhide_abs_widgets()
            self.hide_relative_widgets()
        elif place_type == "relative":
            self.hide_abs_widgets()
            self.unhide_relative_widgets()
            self.set_defaults()
            
