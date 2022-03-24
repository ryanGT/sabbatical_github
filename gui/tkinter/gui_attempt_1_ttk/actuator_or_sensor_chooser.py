######################################
#
# To Do:
#
# - pybd needs to suggest actuator and sensor names
#     - these are methods of a block_diagram model
#     - the parent of the actuator or sensor chooser dialog must have a block diagram model
#
#
#
######################################
import tkinter
import tkinter as tk
from tkinter import ttk

from tkinter import ttk
from tkinter.messagebox import showinfo

from tkinter_utils import my_toplevel_window

import py_block_diagram as pybd


    
class actuator_or_sensor_chooser(my_toplevel_window):
    def __init__(self, parent, title="act or sensor adder dialog", \
                 geometry='600x300', max_params=5):        
        super().__init__(parent, title=title, geometry=geometry)
        self.bd = self.parent.bd
        self.columnconfigure(0, weight=4)
        self.max_params = max_params
        
        self.make_widgets()


    def make_widgets(self):
        mycol = 0
        self.make_label_and_grid_sw(self.main_label, 0, mycol)
        self.make_combo_and_var_grid_nw("main_chooser", 1, mycol)
        self.main_chooser_combobox['values'] =  self.class_names
        self.main_chooser_combobox.bind('<<ComboboxSelected>>', self.main_combo_selected)
        
        self.make_label_and_grid_sw(self.name_label, 2, mycol)
        self.make_entry_and_var_grid_nw("variable_name", 3, mycol)
        #suggest_actuator_name
        
        cur_row = 4
        for i in range(self.max_params):
            j = i+1
            label_attr = "param%i_label" % j
            text = "param%i" % j
            self.make_label_and_grid_sw(text, cur_row, mycol, attr=label_attr)
            cur_row += 1
            basename = "param%i" % j
            self.make_entry_and_var_grid_nw(basename, cur_row, mycol)
            cur_row += 1


        self.go_button = self.make_button_and_grid(self.go_text, 20, mycol, \
                                                   command=self.on_go_button)


    def update_param_labels(self, param_list):
        for i, param in enumerate(param_list):
            j = i+1
            label_attr = "param%i_label" % j
            widget = getattr(self, label_attr)
            widget['text'] = param
        

    def _hide_boxes_by_number(self, j):
        label_attr = "param%i_label" % j
        entry_attr = "param%i_entry" % j
        label_widget = getattr(self, label_attr)
        label_widget.grid_remove()
        entry_widget = getattr(self, entry_attr)
        entry_widget.grid_remove()


    def _unhide_boxes_by_number(self, j):
        label_attr = "param%i_label" % j
        entry_attr = "param%i_entry" % j
        label_widget = getattr(self, label_attr)
        label_widget.grid()
        entry_widget = getattr(self, entry_attr)
        entry_widget.grid()

        
    def hide_unsed_widgets(self, N_unused):
        for i in range(N_unused):
            j = self.max_params - i
            self._hide_boxes_by_number(j)
            

    def unhide_used_widgets(self, N_params):
        for i in range(N_params):
            j = i+1
            self._unhide_boxes_by_number(j)
            


    def set_default_params(self, param_list, default_params):
        for i, param in enumerate(param_list):
            j = i+1
            entry_attr = "param%i_var" % j
            entry_var = getattr(self, entry_attr)
            if param in default_params:
                value = default_params[param]
            else:
                value = ""
            entry_var.set(str(value))


    def get_params_list(self):
        chosen_type = self.main_chooser_var.get()
        params_list = self.params_dict[chosen_type]
        return params_list


    def get_suggested_name(self):
        raise NotImplementedError()


            
    def main_combo_selected(self, *args, **kwargs):
        chosen_type = self.main_chooser_var.get()
        print("chosen_type: %s" % chosen_type)
        # - get suggested name
        # - get parameters list
        # - update parameter entry labels
        # - get defaults
        # - fill entry boxes with defaults
        #
        # Question:
        # - when reading values, how do I know which ones are floats?
        #     - can I get the data types from defaults?
        msg = "cannot create actuators or sensors if self.parent doesn't have a block diagram"
        assert hasattr(self.parent, "bd"), msg
        assert self.parent.bd is not None, msg
        param_list = self.get_params_list()
        

        self.update_param_labels(param_list)
        N_params = len(param_list)
        N_unused = self.max_params - N_params
        self.hide_unsed_widgets(N_unused)
        self.unhide_used_widgets(N_params)

        # suggest actuator name
        suggest_name = self.get_suggested_name()
        name_var = getattr(self, "variable_name_var")
        name_var.set(suggest_name)
        
        # set defaults
        default_params = self.get_default_params()
        self.set_default_params(param_list, default_params)

        # save things for other methods
        self.chosen_type = chosen_type
        self.param_list = param_list


    def get_default_params(self):
        raise NotImplementedError()

    
    def get_params_kwargs(self):
        kwargs = {}
        variable_name = self.variable_name_var.get()
        kwargs["variable_name"] = variable_name

        for i, param in enumerate(self.param_list):
            j = i+1
            entry_attr = "param%i_var" % j
            entry_var = getattr(self, entry_attr)
            value = entry_var.get()
            value_out = pybd.value_from_str(value)
            kwargs[param] = value_out

        return kwargs

    

    def on_go_button(self, *args, **kwargs):
        print("go button pressed")
        # steps:
        # - get chosen class
        # - get parameters
        # - convert parameters to float or int if needed
        # - create actuator or sensor
        # - append actuator or sensor to parent's block_diagram
        chosen_type = self.main_chooser_var.get()
        print("chosen_type: %s" % chosen_type)

        myclass = getattr(pybd, chosen_type)
        variable_name = self.variable_name_var.get()
        print("variable_name: %s" % variable_name)

        kwargs = self.get_params_kwargs()
        print("kwargs = %s" % kwargs)

        myinstance = myclass(**kwargs)
        self.append_instance_to_bd(myinstance)
        self.update_parent_gui()
        self.destroy()
        

    def append_instance_to_bd(self):
        raise NotImplementedError()
    

    def update_parent_gui(self):
        raise NotImplementedError()

    
class actuator_chooser(actuator_or_sensor_chooser):
    def __init__(self,  parent, title="Add Actuator Dialog", \
                 geometry='600x300', max_params=5):        
        self.main_label = 'Actuators'
        self.name_label = "Actuator Name"
        self.class_names = pybd.actuator_class_names
        self.go_text = "Add Actuator"
        self.params_dict = pybd.actuator_params_dict
        super().__init__(parent, title=title, geometry=geometry)
        
                    

    def get_suggested_name(self):
        chosen_type = self.main_chooser_var.get()
        suggest_name = self.bd.suggest_actuator_name(chosen_type)
        return suggest_name


    def get_default_params(self):
        chosen_type = self.main_chooser_var.get()
        default_params = pybd.actuator_default_params[chosen_type]
        return default_params
    

    def append_instance_to_bd(self, myinstance):
        self.bd.append_actuator(myinstance)


    def update_parent_gui(self):
        self.parent.refresh_actuator_names()



class sensor_chooser(actuator_or_sensor_chooser):
    def __init__(self,  parent, title="Add Sensor Dialog", \
                 geometry='600x300', max_params=5):        
        self.main_label = 'Sensors'
        self.name_label = "Sensor Name"
        self.class_names = pybd.sensor_class_names
        self.go_text = "Add Sensor"
        self.params_dict = pybd.sensor_params_dict
        super().__init__(parent, title=title, geometry=geometry)



    def get_suggested_name(self):
        chosen_type = self.main_chooser_var.get()
        suggest_name = self.bd.suggest_sensor_name(chosen_type)
        return suggest_name


    def get_default_params(self):
        chosen_type = self.main_chooser_var.get()
        default_params = pybd.sensor_default_params[chosen_type]
        return default_params


    def append_instance_to_bd(self, myinstance):
        self.bd.append_sensor(myinstance)


    def update_parent_gui(self):
        self.parent.refresh_sensor_names()
