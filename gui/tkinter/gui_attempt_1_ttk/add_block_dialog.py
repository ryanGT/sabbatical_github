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
xpad_options = {'padx': 5, 'pady': 0}
ypad_options = {'padx': 0, 'pady': 5}

from tkinter_utils import my_toplevel_window, window_with_param_widgets_that_appear_and_disappear

###############################################################
# To do:
#
# - when adding a new block, I need to be able to specify parameters
#   whose labels adjust, similar to the sensors and actuators
#
#
# - Plan:
#
#    - each block type should be able to create an empty default where
#      any unknown init params are set to None
#
#    - the default block should have a py_param attribute along with a
#      default_params attr
#
#    - the gui will use the py_params as the labels for the parameter
#      boxes and then use the default_params (both from the empty
#      default block) to populate the default values
#
#    - create a base class from actuator_or_sensor_chooser.py that has boxes
#      that appear and disappear and whose labels adapt based on the number
#      of py_params and the labels get set to the py_params and whose default
#      values come from the empty blocks
#
#
###############################################################


class add_block_dialog(my_toplevel_window, window_with_param_widgets_that_appear_and_disappear):
    def __init__(self, parent, title="Add Block Dialog"):
        super().__init__(parent, title=title, geometry="700x600")
        self.selected_block_type = None
        self.input_block_name = None
        self.input2_block_name = None
        self.input3_block_name = None
        self.parent = parent
        self.bd = self.parent.bd
        self.max_params = 8
        self.make_widgets()



    #def __init__(self, parent, title):
        self.my_username = None
        self.my_password = None
        #super().__init__(parent, title)
        #print("self: %s" % self)
        #print("parent: %s" % parent)


    def make_widgets(self, startrow=0):
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
            widget.grid(row=startrow+i, column=0, sticky='W', **pad_options)


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
            widget.grid(row=startrow+i, column=1, sticky='W', **pad_options)

        currow = i+1
        mycol = 1
        self.make_label_and_grid_sw("Sensors", row=currow, col=mycol,  attr="sensors_label")
        currow += 1
        print("currow = %s" % currow)
        self.make_combo_and_var_grid_nw("sensors", row=currow, col=mycol)
        currow += 1
        print("currow = %s" % currow)
        self.make_label_and_grid_sw("Sensor 2", row=currow, col=mycol,  attr="sensor2_label")
        currow += 1
        print("currow = %s" % currow)
        self.make_combo_and_var_grid_nw("sensor2", row=currow, col=mycol)
        currow += 1
        print("currow = %s" % currow)

        # create numbered parameter widgets for showing and hiding boxes
        # that allow block parameters to be set
        for i in range(self.max_params):
            j = i+1
            # how do I do this as two columns?
            if j % 2 == 1:
                # this is an add # widget
                mycol = 0
            else:
                mycol = 1
                
            label_attr = "param%i_label" % j
            text = "param%i" % j
            self.make_label_and_grid_sw(text, currow, mycol, attr=label_attr)
            basename = "param%i" % j
            self.make_entry_and_var_grid_nw(basename, currow+1, mycol)

            if j % 2 == 0:
                # increment the row for even # widgets
                # - increment by 2 because we added labels and boxes
                currow += 2


        self.go_button.grid(row=30, columnspan=2, column=0, padx=5, pady=5)

        self.actuator_widget_list = ['actuators_label', 'actuators_combobox']
        self.sensor1_widget_list = ['sensors_label','sensors_combobox']
        self.act_and_sense_list = self.actuator_widget_list + self.sensor1_widget_list
        self.sensor2_widget_list = ['sensor2_label','sensor2_combobox']
        self.hide_act_and_sense_combos()
        

    def hide_act_and_sense_combos(self):
        fulllist = self.act_and_sense_list + self.sensor2_widget_list
        for attr in fulllist:
            widget = getattr(self, attr)
            widget.grid_remove()


    def _show_from_attr_name_list(self, attr_list):
        for attr in attr_list:
            widget = getattr(self, attr)
            widget.grid()


    def _hide_from_attr_name_list(self, attr_list):
        for attr in attr_list:
            widget = getattr(self, attr)
            widget.grid_remove()


    def hide_actuator_widgets(self):
        self._hide_from_attr_name_list(self.actuator_widget_list)



    def show_act_and_sense_combos(self):
        for attr in self.act_and_sense_list:
            widget = getattr(self, attr)
            widget.grid()


    def show_sensor2_widgets(self):
        for attr in self.sensor2_widget_list:
            widget = getattr(self, attr)
            widget.grid()

    def show_sensor1_widgets(self):
        self._show_from_attr_name_list(self.sensor1_widget_list)


    def hide_sensor2_widgets(self):
        for attr in self.sensor2_widget_list:
            widget = getattr(self, attr)
            widget.grid_remove()
            

    def on_input_selected(self, *args):
        selection = self.input_choice.curselection()
        print("input selection:")
        print(selection)
        if selection:
            self.input_block_name = self.get_input_block_name()
            print("input selected: %s" % self.input_block_name)
        else:
            print("no selection")


    def show_params_for_block_type(self, block_type):
        myclass = pybd.block_classes_dict[block_type]
        temp_block = myclass()
        py_params = temp_block.py_params
        default_params = {}
        if hasattr(temp_block, "default_params"):
            for key in py_params:
                if key in temp_block.default_params:
                    value = temp_block.default_params[key]
                else:
                    value = ''
                default_params[key] = value
        else:
            empty_list = ['']*len(py_params)
            default_params = dict(zip(py_params, empty_list))
            
        print("block py_params:")
        for key, value in default_params.items():
            print("%s : %s" % (key, value))

        # - pop sensors and actuators from py_params before setting N_params
        # - set defaults

        # actuators and sensors are handled separately, so filter them out:
        all_params = copy.copy(py_params)
        mypoplist = ['actuator','sensor','sensor1','sensor2']
        param_list = [item for item in all_params if item not in mypoplist]
        
        N_params = len(param_list)
        N_unused = self.max_params - N_params
        self.N_params = N_params
        self.unhide_used_widgets(N_params)
        self.hide_unsed_widgets(N_unused)
        self.update_param_labels(param_list)
        self.set_default_params(param_list, default_params)
            

    def on_block_type_selected(self, *args):
        """This is the method that is called when the user chooses a
        specific class for the block that is being added.  Parameter
        boxes update their labels and unused ones are hidden.  The
        sensor and actuator combo boxes are hidden or shown and
        populated."""
        selection = self.blockchoice.curselection()
        print("block type selection:")
        print(selection)
        if not selection:
            print("no selection")
            return None
        block_type = self.get_selected_block_type()
        print("block_type: %s" % block_type)
        if block_type in pybd.plants_with_two_sensors_names:
            # show sensor 2 selection option
            self.show_sensor2_widgets()
        else:
            self.hide_sensor2_widgets()
        self.selected_block_type = block_type
        suggested_name = self.parent.bd.suggest_block_name(block_type)
        self.block_name.set(suggested_name)
        self.show_params_for_block_type(block_type)
            

    def get_selected_block_type(self):
        block_type = self.blockchoice.get(self.blockchoice.curselection())
        return block_type


    def get_input_block_name(self):
        input_name = self.input_choice.get(self.input_choice.curselection())
        return input_name


    def _create_new_block(self):
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
            # we need to handle plant classes with no actuator and those with two sensors
            print("this is a plant")

            # possible cases:
            # - actuator or no actuator
            # - one sensor or two
            #     - must have at least one sensor to be a plant
            if block_type not in pybd.plants_with_no_actuators_names:
                # it has an actuator
                actuator_name = self.actuators_var.get()
                print("actuator_name: %s" % actuator_name)
                myactuator = self.bd.get_actuator_by_name(actuator_name)
                kwargs['actuator'] = myactuator

            if block_type in pybd.plants_with_two_sensors_names:
                # it has two sensors
                sensor1_name = self.sensors_var.get()
                print("sensor1_name: %s" % sensor1_name)
                sensor2_name = self.sensor2_var.get()
                print("sensor2_name: %s" % sensor2_name)
                sensor1 = self.bd.get_sensor_by_name(sensor1_name)                
                kwargs['sensor1'] = sensor1
                sensor2 = self.bd.get_sensor_by_name(sensor2_name)                
                kwargs['sensor2'] = sensor2                
            else:
                # it has only one sensor
                sensor_name = self.sensors_var.get()
                print("sensor_name: %s" % sensor_name)
                mysensor = self.bd.get_sensor_by_name(sensor_name)
                kwargs['sensor'] = mysensor



        # get additional kwargs from param boxes here:
        other_kwargs = self.get_params_kwargs(self.N_params)
        ## print("other_kwargs:")
        ## print(other_kwargs)
        kwargs.update(other_kwargs) 
        print("creating block in go_pressed")
        print("kwargs:")
        print(kwargs)
        new_block = pybd.create_block(block_class, block_type, block_name, **kwargs)
        return new_block


    def go_pressed(self):
        # Next step:
        # - read parameters from the numbered param boxes for kwargs
        block_name = self.block_name.get()
        new_block = self._create_new_block()
        self.parent.append_block_to_dict(block_name, new_block)
        #self.parent.password = self.my_password
        self.destroy()


    def cancel_pressed(self):
        # print("cancel")
        self.destroy()


    def set_actuator_and_sensor_lists(self):
        # - can I warn if there are no actuators and filter certain plants out of the list?
        # - how do you handle multiple sensors?
        if not hasattr(self, "actuator_names"):
            self.check_actuators_and_sensors()
            
        self.actuators_combobox['values'] = self.actuator_names
        self.sensors_combobox['values'] = self.sensor_names
        self.sensor2_combobox['values'] = self.sensor_names


    def check_actuators_and_sensors(self):
        self.actuator_names = self.bd.actuator_name_list
        self.sensor_names = self.bd.sensor_name_list
        self.N_act = len(self.actuator_names)
        self.N_sense = len(self.sensor_names)


    def category_selected(self, event):
        """This is one of the main methods.  When the user chooses the
        type of block (plant, input, controller, ...), this method
        populates the block_choice_list box with corresponding class
        names."""
        self.check_actuators_and_sensors()
        chosen_cat = self.selected_category.get()
        print("category_selected: %s" % chosen_cat)
        new_list = pybd.block_category_dict[chosen_cat]
        print("new_list: %s" % new_list)
        #lb.delete(0,END)
        #Label(win, text="Nothing Found Here!",
        #font=('TkheadingFont, 20')).pack()

        # Add items in the Listbox
        #lb.insert("end","item1","item2","item3","item4","item5")

        # if no actuators have been defined, we need to filter out
        # some plants, if plant is the chosen_cat

        if chosen_cat == "plant":
            if self.N_sense == 0:
                msg = "You cannot create a plant until a sensor have been defined.  Some plants also require an actuator to be defined."
                showinfo(title='Information',
                         message=msg)
                return
            elif self.N_act == 0 and self.N_sense > 0:
                # allow only plants without explicit actuators
                msg = "Showing only plants that do not require an actuator to be defined."
                showinfo(title='Information',
                         message=msg)
                # filter plant names
                new_list = pybd.plants_with_no_actuators_names
                self.hide_actuator_widgets()
                self.show_sensor1_widgets()

            # if neither of the above cases is true, than both
            # actuators and sensors are defined and all plants should
            # be shown
            else:
                self.show_act_and_sense_combos()
                
            self.set_actuator_and_sensor_lists()
        else:
            self.hide_act_and_sense_combos()

        self.block_choice_list.set(new_list)



class replace_block_dialog(add_block_dialog):
    def __init__(self, parent, title="Replace Block Dialog"):
        # Not sure how the tk super method actually works (would it be better
        # to use the normal python method of calling the parent class' __init__
        # method?):
        super().__init__(parent, title=title)
        # self.block_to_replace = block_to_replace
        # I should also set the inputs and other things based on the
        # block_to_replace passed in


    def make_widgets(self):
        # big idea: add a widget at the top to choose the 
        # block to replace.  Then call the parent method with startrow=2
        replacement_label = ttk.Label(self, text="Block to Replace")
        replacement_label.grid(row=0, column=0, sticky='SW', **xpad_options)

        self.replacement_block_list = self.parent.get_block_name_list()

        self.replacement_block_name = tk.StringVar()
        
        self.replacement_combo = ttk.Combobox(self,
                textvariable=self.replacement_block_name)
        self.replacement_combo['values'] = self.replacement_block_list 

        # prevent typing a value
        self.replacement_combo['state'] = 'readonly'
        self.replacement_combo.bind('<<ComboboxSelected>>',
                self.on_replacement_selected)
 
        self.replacement_combo.grid(row=1, column=0, sticky='NW', **xpad_options)
        add_block_dialog.make_widgets(self, startrow=2)

        self.go_button.config(text="Replace")
    
    def on_replacement_selected(self, *args, **kwargs):
        # what needs to actually happen here?
        # - copy any info from the block to replace into a kwargs dict
        # - the new block should have the same input(s) and placement info
        #   as the block it is replacing
        # - is there anything else to copy over?
        print("in on_replacement_selected")
        # if the old block has inputs, set the input widget values here
        self.old_block_name = self.replacement_block_name.get()
        print("self.old_block_name = %s" % self.old_block_name)
        self.old_block = self.parent.get_block_by_name(self.old_block_name)
        #self.input_block1 = input_block1
        if hasattr(self.old_block, "input_block1_name"):
            input1_name = self.old_block.input_block1_name
            if input1_name:
                #selection_clear(0, END), then selection_set
                mylist = self.input_choice.get(0, "end")
                ind = int(mylist.index(input1_name))
                self.input_choice.selection_set(ind)


    def get_input_names(self):
        input_kwargs = {}
        for i in range(1,3):
            attr = "input_block%i_name" % i
            if hasattr(self.old_block, attr):
                val = getattr(self.old_block, attr)
                input_kwargs[attr] = val
        self.input_kwargs = input_kwargs


    def get_old_position_info(self):
        placement_kwargs = {}
        if hasattr(self.old_block, "placement_type") and self.old_block.placement_type:
            pt = self.old_block.placement_type
            placement_kwargs['placement_type'] = pt
            if pt == 'absolute':
                mykeys = ['abs_x','abs_y']
            else:
                mykeys = ['rel_block_name','rel_pos','rel_distance','xshift','yshift']
            
            for key in mykeys:
                attr = getattr(self.old_block, key)
                placement_kwargs[key] = attr

        self.placement_kwargs = placement_kwargs
        return self.placement_kwargs




    def set_inputs(self, new_block):
        for i in range(1,3):
            attr = "input_block%i_name" % i
            if attr in self.input_kwargs:
                name = self.input_kwargs[attr]
                if name:
                    # the defaults inherited from block might nead to an empty
                    # name
                    in_block = self.parent.get_block_by_name(name)
                    method_name = "set_input_block%i" % i
                    if hasattr(new_block, method_name):
                        mymethod = getattr(new_block, method_name)
                        mymethod(in_block)
     


    def go_pressed(self):
        # Next step:
        # - read parameters from the numbered param boxes for kwargs
        # - kwargs are handled by self._create_new_block, which mostly reads
        #   from the widgets
        # - if we want to pass kwargs from old block to new block, we should
        #   probably pass those values to the widgets as an intermediate step
        # - placement stuff needs to be handled separately
        #
        # Conceptual question: do I force the new block to have the same
        # input(s) as the old block?
        new_block = self._create_new_block()
        self.get_input_names()
        self.set_inputs(new_block)
        self.get_old_position_info()
        place_dict = copy.copy(self.placement_kwargs)
        pt = place_dict.pop('placement_type')

        if pt == 'absolute':
            # get abs kwargs
            new_block.place_absolute(**place_dict)
        elif pt == 'relative':
            rel_block_name = place_dict.pop('rel_block_name')
            rel_block = self.parent.get_block_by_name(rel_block_name)
            new_block.place_relative(rel_block, **place_dict)
        else:
            pt_str = pt.strip()
            if pt_str:
                raise ValueError("placement type not understood: %s" % pt_str)
            
        # - handle input(s)
        # get_block_by_name
        # set_input_block1
        # set_input_block2
        # - handled placement
        # - find all references in self.parent.bd and replace them:
        self.parent.bd.replace_block(self.old_block, new_block)
        self.destroy()


