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

from tkinter_utils import my_toplevel_window

class add_block_dialog(my_toplevel_window):
    def __init__(self, parent, title="Add Block Dialog"):
        super().__init__(parent, title=title, geometry="600x400")
        self.selected_block_type = None
        self.input_block_name = None
        self.input2_block_name = None
        self.input3_block_name = None
        self.parent = parent
        self.bd = self.parent.bd
        self.make_widgets()



    #def __init__(self, parent, title):
        self.my_username = None
        self.my_password = None
        #super().__init__(parent, title)
        #print("self: %s" % self)
        #print("parent: %s" % parent)


    def make_widgets(self):
        #def body(self):
        #print("frame: %s" % frame)
        # print(type(frame)) # tkinter.Frame

        #=================================
        #
        # column 0 
        #
        #=================================
        self.label1 = ttk.Label(self, text="Block Category")


        #self.label1.grid(row=0, column=0)

        self.selected_category = tk.StringVar()
        self.category_combobox = ttk.Combobox(self, textvariable=self.selected_category)

        # get first 3 letters of every month name
        self.category_combobox['values'] = pybd.block_categories

        # prevent typing a value
        self.category_combobox['state'] = 'readonly'
        self.category_combobox.bind('<<ComboboxSelected>>', self.category_selected)
        start_key = 'input'
        self.category_combobox.set(start_key)
        label2 = ttk.Label(self, text="Block Type")

        self.block_choice_list = tk.StringVar(value=pybd.block_category_dict[start_key])

        self.blockchoice = tk.Listbox(self, \
                                      listvariable=self.block_choice_list, \
                                      height=6, \
                                      width=40, \
                                      #selectmode='extended'
                                      )

        self.blockchoice.bind("<<ListboxSelect>>", self.on_block_type_selected)
        #self.category_combobox.grid(row=1, column=0)

        column0_widgets = [self.label1, self.category_combobox, label2, self.blockchoice]

        for i, widget in enumerate(column0_widgets):
            widget.grid(row=i, column=0, sticky='W', **pad_options)


        currow = i+1
        self.make_label_and_grid_sw("Actuators", row=currow, col=0,  attr="actuators_label")
        currow += 1
        self.make_combo_and_var_grid_nw("actuators", row=currow, col=0)
        #=================================
        #
        # column 1 
        #
        #=================================
        label_BN = ttk.Label(self, text="Block Name")

        self.block_name = tk.StringVar()
        self.block_name_box = ttk.Entry(self, textvariable=self.block_name)

        label_input = ttk.Label(self, text="Input Block")
        self.input_block_list = tk.StringVar(value=self.parent.get_block_name_list())

        self.input_choice = tk.Listbox(self, \
                                       listvariable=self.input_block_list, \
                                       height=6, \
                                       width=25, \
                                       #selectmode='extended'
                                       )
        self.input_choice.bind("<<ListboxSelect>>", self.on_input_selected)

        self.go_button = ttk.Button(self, text='Add Block', command=self.go_pressed)

        column1_widgets = [label_BN, self.block_name_box, label_input, \
                           self.input_choice]#, self.go_button]
        for i, widget in enumerate(column1_widgets):
            widget.grid(row=i, column=1, sticky='W', **pad_options)

        currow = i+1
        mycol = 1
        self.make_label_and_grid_sw("Sensors", row=currow, col=mycol,  attr="sensors_label")
        currow += 1
        print("currow = %s" % currow)
        self.make_combo_and_var_grid_nw("sensors", row=currow, col=mycol)
        currow += 1
        print("currow = %s" % currow)
        self.go_button.grid(row=20, columnspan=2, column=0, padx=5, pady=5)

        self.act_and_sense_list = ['sensors_label','actuators_label','sensors_combobox', 'actuators_combobox']

    def hide_act_and_sense_combos(self):
        for attr in self.act_and_sense_list:
            widget = getattr(self, attr)
            widget.grid_remove()


    def show_act_and_sense_combos(self):
        for attr in self.act_and_sense_list:
            widget = getattr(self, attr)
            widget.grid()



    def on_input_selected(self, *args):
        selection = self.input_choice.curselection()
        print("input selection:")
        print(selection)
        if selection:
            self.input_block_name = self.get_input_block_name()
            print("input selected: %s" % self.input_block_name)
        else:
            print("no selection")


    def on_block_type_selected(self, *args):
        """This is the method that is called when the user chooses a
        specific class for the block that is being added"""
        selection = self.blockchoice.curselection()
        print("block type selection:")
        print(selection)
        if not selection:
            print("no selection")
            return None
        block_type = self.get_selected_block_type()
        print("block_type: %s" % block_type)
        self.selected_block_type = block_type
        suggested_name = self.parent.bd.suggest_block_name(block_type)
        self.block_name.set(suggested_name)
            

    def get_selected_block_type(self):
        block_type = self.blockchoice.get(self.blockchoice.curselection())
        return block_type


    def get_input_block_name(self):
        input_name = self.input_choice.get(self.input_choice.curselection())
        return input_name


    def go_pressed(self):
        assert self.selected_block_type is not None, "block_type has not been set"
        print("you pressed go")
        block_type = self.selected_block_type
        print("block_type: %s" % block_type)
        kwargs = {}

        # ultimately, input_block_names need to be converted to actual block instances
        # - look up the block in parent.bd
        #
        # Approach:
        # - input_block_name, input2_block_name, and input3_block_name are attributes of this
        #   dialog box that the user may have optionally set
        # - input_block1 through input_block3 are attributes recognized by pybd
        # - I need to map from one to the other
        input_pairs = [('input_block_name','input_block1'), \
                       ('input2_block_name','input_block2'), \
                       ('input3_block_name','input_block3'), \
                       ]

        for attr, key in input_pairs:
            input_block_name = getattr(self, attr)
            if input_block_name is not None:
                input_block = self.parent.get_block_by_name(input_block_name)
                kwargs[key] = input_block
                key2 = key + '_name'
                kwargs[key2] = input_block_name 

        
        block_name = self.block_name.get()
        block_class = getattr(pybd, block_type)
        # how do I handle cases with input(s) set?

        # get actuator and sensor if it is a plant
        print("plant classes: %s" % pybd.plant_class_names)
        if block_type in pybd.plant_class_names:
            print("this is a plant")
            actuator_name = self.actuators_var.get()
            print("actuator_name: %s" % actuator_name)
            sensor_name = self.sensors_var.get()
            print("sensor_name: %s" % sensor_name)
            myactuator = self.bd.get_actuator_by_name(actuator_name)
            mysensor = self.bd.get_sensor_by_name(sensor_name)
            kwargs['actuator'] = myactuator
            kwargs['sensor'] = mysensor

            
        print("creating block in go_pressed")
        print("kwargs:")
        print(kwargs)
        new_block = pybd.create_block(block_class, block_type, block_name, **kwargs)
        self.parent.append_block_to_dict(block_name, new_block)
        #self.parent.password = self.my_password
        self.destroy()


    def cancel_pressed(self):
        # print("cancel")
        self.destroy()


    def set_actuator_and_sensor_lists(self):
        self.actuator_names = self.bd.actuator_name_list
        self.sensor_names = self.bd.sensor_name_list
        N_act = len(self.actuator_names)
        N_sense = len(self.sensor_names)
        # - can I warn if there are no actuators and filter certain plants out of the list?
        # - how do you handle multiple sensors?
        if N_act*N_sense == 0:
            msg = "You cannot create a plant until an actuator and a sensor have been defined."
            showinfo(title='Information',
                     message=msg)
        else:
            self.actuators_combobox['values'] = self.actuator_names
            self.sensors_combobox['values'] = self.sensor_names


    def category_selected(self, event):
        """This is one of the main methods.  When the user chooses the
        type of block (plant, input, controller, ...), this method
        populates the block_choice_list box with corresponding class
        names."""
        chosen_cat = self.selected_category.get()
        print("category_selected: %s" % chosen_cat)
        new_list = pybd.block_category_dict[chosen_cat]
        print("new_list: %s" % new_list)
        #lb.delete(0,END)
        #Label(win, text="Nothing Found Here!",
        #font=('TkheadingFont, 20')).pack()

        # Add items in the Listbox
        #lb.insert("end","item1","item2","item3","item4","item5")

        self.block_choice_list.set(new_list)
        if chosen_cat == "plant":
            self.show_act_and_sense_combos()
            self.set_actuator_and_sensor_lists()
        else:
            self.hide_act_and_sense_combos()

