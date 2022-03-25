"""
This is the main file in the tkinter gui.  The main class is
`pybd_gui`.  The main gui building function is
`pybd_gui.make_widgets`.  The main gui window has two columns and
placement is handled by tkinter's `grid` function.  The first column
of the main gui contains the main matplotlib graph canvas.  The other
column has a tkinter notebook with several pages.

The `pybd_gui` class also has a reference to is associate
`block_diagram` model, which can be accessed as
`pybd_gui.bd` (`self.bd)`.

There are several helper gui's in this module.  Most of them derive
from the utility top-level class `tkinter_utils.my_toplevel_window`
which provides convienence functions for easily adding and griding
widgets.  Tkinter widgets often have an associated string variable for
getting and setting the values or contents of the widgets.
`tkinter_utils.py` also includes helper functions for creating a widget
and its string variable in one step based on a `basename` and having
certain tail strings for the varialbe and widget (entrybox, listbox,
combobox, ...).  `setattr` is used to assign the variable and widget
to the gui dialog.

The helper dialogs are:

- `add_block_dialog.py`
- `place_block_dialog.py`
- `actuator_or_sensor_chooser.py`

"""


############################################
#
# Next Steps:
#
# ----------------
#
# - **allow parameters to be specified using the add_block_dialog**
# - what does my gui need to be fully ready for student use?
# - what would it take for the gui to generate micropython code?
# - what do I need to do to do line following with micropython using the gui?
#     - do "dumb" line following at 250 Hz
#     - start reading pendulum
#     - do vib supression
#     - add check for new line sensor reading to the template
#
# ## Plan:
#    - try generating the micropython line following BD and see what is needed
#         - how to handle **two sensors** and no actuator <----
#         - suggested name for cart_pend plant should be G
#
#
# - why does the feedback wire on my summing junction look terrible?
# - figure out how to zoom the block diagram sketch well
#     - first full BD (model 5 simple) looks like crap
# - view and edit block details
#     - probably another page on the notebook
#     - combobox to choose the block
#     - labels and entry boxes that show or disapper
#         - labels from from block.param_list
#         - I already do this in the actuator/sensor dialog
# - click on a block on the mpl graph canvas and find the nearest block
# - add wire waypoints
#     - probably an option under the place blocks gui
#     - may need a show grid option
#
#############################################

#iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
#
# Issues:
#
#
# Resovled:
# - generate code menu functions
# - make the set input buttons work
# - make the load csv method handle the new format with actuators and sensors
#     - break the file into three chunks: actuators, sensors, and blocks
#     - create actuators and sensors from the first two chunks
#     - create the other blocks
#         - plant blocks need to find their actuators and sensors
#         - does my save csv stuff save the actutor and sensor for each plant?
#             - probably not
#         - you are already not saving params for the blocks
#             - Kp and Kd for PD
#             - amp and step time for a step input
#             - you need some columns for key:value for param1, param2, ...
# - create a place block dialog
# - draw the block diagram
# - selecting a block type and then selecting an input block messes up
#   the current selection of the block type listbox
#
# - how do I handle cases with input(s) set when creating new blocks?
#     - pass kwargs to the create block function?
#         - I need to handle blocks with more than one input differently
#             - input vs. input1
#     - how do I make this work without marrying it to the gui?
#         - but only the gui knows if an input was chosen
#         - the gui can pass along chosen input name(s)
#         - the create block function in pydb can handle
#           input vs. input1 depending on block type
#
# - **how do I handle sensors and actuators so that plants can be
#   created?**
#     - gui could show actuator and sensor comboboxes when plant is selected
#         - or only sensor for plant_no_actuator
#     - what does it take to create an actuator?
#     - what does it take to create a sensor?
#     - what about custom sensors and actuators?
#     - example code:
#         - encoder = pybd.encoder(11)
#         - HB = pybd.h_bridge(6,4,9)
#     - Approach:
#         - combobox to select a standard actuator or sensor or custom
#         - entry boxes for appropriate params
#             - making these appear and disapper and have the labels change
#               will get a little complicated
#             - if they are numbered with a pattern, I think it can work:
#               - self.actuator_param1_label
#               - self.actuator_param1_var
#               - self.actuator_param1_entry
#             - then a dict or list to map to the params for a particular sensor or actuator
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

from add_block_dialog import add_block_dialog
from place_block_dialog import place_block_dialog
from input_chooser import input_chooser, input2_chooser

#from tkinter import simpledialog

from actuator_or_sensor_chooser import actuator_chooser, sensor_chooser


import py_block_diagram as pybd
import os, txt_mixin

pad_options = {'padx': 5, 'pady': 5}


def dict_to_key_value_strings(mydict):
    """Helper function for saving a dictionary to a text value by
    converting it to key:value strings as a list"""
    mylist = []
    pat = "%s:%s"
    for key, value in mydict.items():
        val_str = str(value)
        cur_str = pat % (key, val_str)
        mylist.append(cur_str)

    return mylist


class pybd_gui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.option_add('*tearOff', False)
        self.geometry("900x600")
        self.mylabel = 'Python Block Diagram GUI'
        self.title(self.mylabel)
        self.resizable(1, 1)

        # configure the grid
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=4)

        self.options = {'padx': 5, 'pady': 5}

        self.menubar = tk.Menu(self)
        self['menu'] = self.menubar
        self.menu_file = tk.Menu(self.menubar)
        self.menu_edit = tk.Menu(self.menubar)
        self.menu_codegen = tk.Menu(self.menubar)        
        self.menubar.add_cascade(menu=self.menu_file, label='File')
        self.menubar.add_cascade(menu=self.menu_edit, label='Edit')
        self.menubar.add_cascade(menu=self.menu_codegen, label='Code Generation')        
        self.menu_file.add_command(label='Save', command=self.on_save_menu)
        self.menu_file.add_command(label='Load', command=self.on_load_menu)        
        #menu_file.add_command(label='Open...', command=openFile)
        self.menu_file.add_command(label='Quit', command=self._quit)
        self.menu_codegen.add_command(label='Set Arduino Template File', command=self.set_arduino_template)
        self.menu_codegen.add_command(label='Get Arduino Template File', command=self.get_arduino_template)
        self.menu_codegen.add_command(label='Set Arduino Output Path', \
                                      command=self.set_arduino_output_folder)
        self.menu_codegen.add_command(label='Generate Arduino Code', command=self.arduino_codegen)                

        #self.bind("<Key>", self.key_pressed)
        self.bind('<Control-q>', self._quit)
        self.bind('<Control-s>', self.on_save_menu)
        self.bind('<Control-l>', self.on_load_menu)
        self.bind('<Control-a>', self.add_block)
        self.bind('<Control-P>', self.on_place_btn)
        self.bind('<Alt-p>', self.on_place_btn)
        self.bind('<Control-d>', self.on_draw_btn)
        
        # configure the root window
        self.make_widgets()

        self.bd = pybd.block_diagram()
        """This is the block_diagram model for the gui, which refers
        to an instance of py_block_diagram.block_diagram"""

        # codegen variables
        self.arduino_template_path = ''
        """String for the path to the Arduino codegen template file."""
        self.arduino_output_folder = ''
        """String for the path to the folder where auto-generated
        Arduino code will be saved."""

        # params for saving
        self.param_list = ['arduino_template_path','arduino_output_folder']
        """List of parameters to save to the configuration file as
        'key:value' string pairs."""
        self.params_path = "gui_params_pybd.txt"
        """Path to the txt file used for saving gui parameters listed
        in pybd_gui.param_list, such as
        `pybd_gui.arduino_template_path`."""
        self.load_params()


    def load_params(self):
        """Load parameters for the gui from the txt file specified in
        `pybd_gui.params_path`.  The parameters are saved as key:value
        strings."""
        myfile = txt_mixin.txt_file_with_list(self.params_path)
        mylist = myfile.list
        mydict = pybd.break_string_pairs_to_dict(mylist)
        for key, value in mydict.items():
            setattr(self, key, value)
            

    def save_params(self):
        """Save parameters from pybd_gui.param_list to a txt values as
        key:value string pairs."""
        mydict = self.build_save_params_dict()
        my_string_list = dict_to_key_value_strings(mydict)
        txt_mixin.dump(self.params_path, my_string_list)
        
        
    def build_save_params_dict(self):
        """Build a dictionary of parameters to save to a txt file so
        that various things in the gui are preserved from session to
        session.  The parameters are listed in pybd_gui.param_list."""
        mydict = {}
        for key in self.param_list:
            value = str(getattr(self, key))
            mydict[key] = value
        return mydict


    def set_arduino_output_folder(self, *args, **kwargs):
        folder_path =  tk.filedialog.askdirectory()
        if folder_path:
            print("folder_path: %s" % folder_path)
            self.arduino_output_folder = folder_path


    def arduino_codegen(self, *args, **kwargs):
        """Generate the Arduino code by using the block diagram's
        `generate_arduino_code` function."""
        print("in arduino_codegen function")
        if not self.arduino_output_folder:
            self.set_arduino_output_folder()
        rest, output_name = os.path.split(self.arduino_output_folder)
        print("rest = %s" % rest)
        print("blocks: %s" % self.bd.block_name_list)
        self.bd.generate_arduino_code(output_name, \
                                      template_path=self.arduino_template_path, \
                                      output_folder=rest, \
                                      )
        ## def generate_arduino_code(self, output_name, \
        ##                           template_path, \
        ##                           output_folder='', \
        ##                           verbosity=0):


    def set_arduino_template(self, *args, **kwargs):
        """Use a file dialog to allow the user to set the path to the
        Arduino template file that will be used in code generation."""
        print("in set_arduino_template function")
        filename = tk.filedialog.askopenfilename(title = "Select Arduino Template File",\
                                                 filetypes = (("ino files","*.ino"),("all files","*.*")))
        print (filename)
        if filename:
            self.arduino_template_path = filename



    def get_arduino_template(self, *args, **kwargs):
        """Show the current path to the Arduino codegen template file
        on a showinfo dialog.  This just lets the use check the
        variable path."""
        print("in get_arduino_template function")
        # self.arduino_template_path #<--- put me on a dialog showinfo
        showinfo(title='Information',
                message='Arduino template file path: %s' % self.arduino_template_path)

        
    def make_label(self, text, root=None):
        if root is None:
            root = self
        widget = ttk.Label(root, text=text)
        return widget


    def grid_label_sw(self, widget, row, col):
        widget.grid(row=row, column=col, sticky='SW', pady=(5,1), padx=10)


    def grid_widget(self, widget, row, col, padx=10, pady=5, **kwargs):
        widget.grid(row=row, column=col, padx=padx, pady=pady, **kwargs)


    def grid_box_nw(self, widget, row, col, **grid_opts):
        if 'sticky' in grid_opts:
            sticky = grid_opts['sticky']
        else:
            sticky = 'NW'
        widget.grid(row=row, column=col, sticky=sticky, pady=(1,5), padx=10)


    def make_label_and_grid_sw(self, text, row, col, root=None):
        if root is None:
            root = self
        widget = self.make_label(text, root=root)
        self.grid_label_sw(widget, row, col)
        return widget


    def make_widget_and_var_grid_nw(self, basename, row, col, type="entry", root=None):
        if root is None:
            root = self
        
        myvar = tk.StringVar()
        if type.lower() == 'entry':
            widget_class = ttk.Entry
            tail = '_entry'
        elif 'combo' in type.lower():
            widget_class = ttk.Combobox
            tail = '_combobox'

        mywidget = widget_class(root, textvariable=myvar)
        self.grid_box_nw(mywidget, row, col)
        var_attr = basename + '_var'
        setattr(self, var_attr, myvar)
        widget_attr = basename + tail
        setattr(self, widget_attr, mywidget)
        return mywidget


    def _assign_widget_and_var_to_attrs(self, basename, tail, mywidget, myvar):
        var_attr = basename + '_var'
        setattr(self, var_attr, myvar)
        widget_attr = basename + tail
        setattr(self, widget_attr, mywidget)
        

    def make_listbox_and_var(self, basename, row, col, root=None, height=6, grid_opts={}):
        if root is None:
            root = self

        myvar = tk.StringVar([])

        mywidget = tk.Listbox(root, \
                              listvariable=myvar, \
                              height=height, \
                              #selectmode='extended'
                              )
        self.grid_box_nw(mywidget, row, col, **grid_opts)
        tail = "_listbox"
        self._assign_widget_and_var_to_attrs(basename, tail, mywidget, myvar)
        return mywidget


    def make_entry_and_var_grid_nw(self, basename, row, col, root=None):
        if root is None:
            root = self
        
        return self.make_widget_and_var_grid_nw(basename, row, col, type="entry", root=root)
        ## myvar = tk.StringVar()
        ## myentry = ttk.Entry(self, textvariable=myvar)
        ## self.grid_box_nw(myentry, row, col)
        ## var_attr = basename + '_var'
        ## setattr(self, var_attr, myvar)
        ## entry_attr = basename + '_entry'
        ## setattr(self, entry_attr, myentry)


    def make_combo_and_var_grid_nw(self, basename, row, col, root=None):
        if root is None:
            root = self
        
        return self.make_widget_and_var_grid_nw(basename, row, col, type="combobox", root=root)        


    def make_button_and_grid(self, btn_text, row, col, command=None, root=None, sticky=None):
        if root is None:
            root = self
            
        kwargs = {}
        if command is not None:
            kwargs['command'] = command

        grid_opts = {}
        if sticky is not None:
            print("sticky = %s" % sticky)
            grid_opts['sticky'] = sticky
            
        mybutton = ttk.Button(root, text=btn_text, **kwargs)
        mybutton.grid(column=col, row=row, pady=10, padx=10, **grid_opts)
        return mybutton
    
        
############################
    def key_pressed(self, event):
        print("pressed:")
        print(repr(event.char))


    def on_load_menu(self, *args, **kwargs):
        print("in menu laod")
        filename = tk.filedialog.askopenfilename(title = "Select Model to Load (CSV)",\
                                                 filetypes = (("csv files","*.csv"),("all files","*.*")))
        print (filename)
        if filename:
            new_bd = pybd.load_model_from_csv(filename)
            self.bd = new_bd
            self.block_list_var.set(self.bd.block_name_list)
            # actuators and sensors
            self.actuators_var.set(self.bd.actuator_name_list)
            self.sensors_var.set(self.bd.sensor_name_list)
            
    
    def on_save_menu(self, *args, **kwargs):
        print("in menu save")
        filename = tk.filedialog.asksaveasfilename(title = "Select filename",\
                                                   filetypes = (("csv files","*.csv"),("all files","*.*")))
        print (filename)
        if filename:
            self.bd.save_model_to_csv(filename)
            

    def get_block_name_list(self):
        #block_list = self.bd._build_block_list()
        mylist = self.bd.block_name_list
        return mylist


    def get_block_by_name(self, block_name):
        return self.bd.get_block_by_name(block_name)

    
    def append_block_to_dict(self, block_name, new_block):
        self.bd.append_block_to_dict(block_name, new_block)
        # update listbox
        self.block_list_var.set(self.bd.block_name_list)
        
        
    def add_block(self, *args, **kwargs):
        #showinfo(title='Information',
        #        message='add block pressed')
        mydialog = add_block_dialog(title="Add New Block", parent=self)
        mydialog.grab_set()
        #print("%s, %s" % (mydialog.my_username, mydialog.my_password))

        
    def _quit(self, *args, **kwargs):
        print("in _quit")
        self.save_params()
        self.quit()     # stops mainloop
        self.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate


    def block_selected(self, event=0):
        # get selected indices
        selected_indices = self.blocklistbox.curselection()
        if not selected_indices:
            # if no blocks are selected, clear input and placement boxes
            self.clear_boxes()
            return
        # - if the selected block is an input, hide input widgets
        #     - pybd.source_block
        # - if the selected block is not an instance of block_with_two_inputs, hide input2 widgets
        #     - pybd.block_with_two_inputs
        #     - could also be an if_block with three inputs
        # - populate entry boxes if input1 or input2 blocks are set
        block_name = self.blocklistbox.get(selected_indices)
        block = self.get_block_by_name(block_name)

        place_str = block.get_placememt_str()
        print("place_str: %s" % place_str)
        self.fill_placement_entry(place_str)

        if isinstance(block, pybd.source_block):
            self.hide_input_widgets()
            # exit before populating the input boxes
            return
        elif isinstance(block, pybd.block_with_two_inputs):
            self.unhide_input_widgets()
        else:
            # assume one input
            self.unhide_input1_widgets()
            self.hide_input2_widgets()

        # populate the entry boxes if appropriate
        if block.input_block1 is not None:
            in1_name = block.input_block1.variable_name
            self.input1_var.set(in1_name)
        else:
            # clear
            self.input1_var.set("")
            
        if isinstance(block, pybd.block_with_two_inputs):
            if block.input_block2 is not None:
                in2_name = block.input_block2.variable_name
                self.input2_var.set(in2_name)
            else:
                # clear
                self.input2_var.set("")

        
                
    def _hide_widgets(self, widget_list):
        for widget in widget_list:
            widget.grid_remove()


    def _unhide_widgets(self, widget_list):
        for widget in widget_list:
            widget.grid()
        

    def hide_input_widgets(self):
        self._hide_widgets(self.input1_widgets)
        self._hide_widgets(self.input2_widgets)


    def unhide_input_widgets(self):
        self._unhide_widgets(self.input1_widgets)
        self._unhide_widgets(self.input2_widgets)


    def unhide_input1_widgets(self):
        self._unhide_widgets(self.input1_widgets)


    def unhide_input2_widgets(self):
        self._unhide_widgets(self.input2_widgets)


    def hide_input2_widgets(self):
        self._hide_widgets(self.input2_widgets)
        

    def make_widgets(self):
        # don't assume that self.parent is a root window.
        # instead, call `winfo_toplevel to get the root window
        #self.winfo_toplevel().title("Simple Prog")
        #self.wm_title("Python Block Diagram GUI")        


        # column 0
        self.label = ttk.Label(self, text=self.mylabel)
        self.label.grid(row=0,column=0,sticky='NW', **self.options)


        #self.big_button = ttk.Button(self, text='Big Button')
        #self.big_button.grid(row=1,column=0,sticky='news',**self.options)
        self.fig = Figure(figsize=(9, 6), dpi=100)
        t = np.arange(0, 3, .01)
        self.ax = self.fig.add_subplot(111)
        self.ax.plot(t, 2 * np.sin(2 * np.pi * t))
        self.ax.set_xlim([0,0.5])

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0, ipadx=40, ipady=20, \
                                         sticky="news")#, rowspan=16)

        self.toolbarFrame = ttk.Frame(master=self)
        self.toolbarFrame.grid(row=19,column=0)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)


        mywidth=5
        
        self.button_frame1 = ttk.Frame(self)
        self.quit_button = ttk.Button(self.button_frame1, text="Quit", width=mywidth, \
                                      command=self._quit)
        self.quit_button.grid(column=0, row=0,  **self.options)

        self.draw_button = ttk.Button(self.button_frame1, text="Draw", width=mywidth, \
                                      command=self.on_draw_btn)
        self.draw_button.grid(column=1, row=0, **self.options)

        # x and y lims for the plot
        xlim_label = ttk.Label(self.button_frame1, text="xlims:")
        self.xmin_var = tk.StringVar(value="0")
        self.xmin_box = ttk.Entry(self.button_frame1, width=mywidth, textvariable=self.xmin_var)
        self.xmax_var = tk.StringVar(value="5")
        self.xmax_box = ttk.Entry(self.button_frame1, width=mywidth, textvariable=self.xmax_var)
        xlim_label.grid(column=2, row=0, padx=5, pady=5, sticky='E')
        self.xmin_box.grid(column=3, row=0, padx=5, pady=5)#, sticky='E')
        self.xmax_box.grid(column=4, row=0, padx=5, pady=5)#,sticky='E')

        ylim_label = ttk.Label(self.button_frame1, text="ylims:")
        self.ymin_var = tk.StringVar(value="-5")
        self.ymin_box = ttk.Entry(self.button_frame1, width=mywidth, textvariable=self.ymin_var)
        self.ymax_var = tk.StringVar(value="5")
        self.ymax_box = ttk.Entry(self.button_frame1, width=mywidth, textvariable=self.ymax_var)
        ylim_label.grid(column=5, row=0, padx=5, pady=5, sticky='E')
        self.ymin_box.grid(column=6, row=0, padx=5, pady=5)#, sticky='E')
        self.ymax_box.grid(column=7, row=0, padx=5, pady=5)#,sticky='E')
        self.zoom_btn = ttk.Button(self.button_frame1, text="Zoom", width=mywidth, command=self.on_zoom_btn)
        self.zoom_btn.grid(column=8, row=0, padx=5, pady=5)#,sticky='E')
        
        ## self.xlim_label = ttk.Label(self.button_frame1, text="xlim:")
        ## self.xlim.grid(row=0,column=2,sticky='E')
        ## self.xlim_var = tk.StringVar()
        ## self.xlim_box = ttk.Entry(self.button_frame1, textvariable=self.xlim_var)
        ## self.xlim_box.grid(column=3, row=0, sticky="W", padx=(0,5))

        
        self.button_frame1.grid(row=20, column=0)

        # Column 1
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=1, ipadx=10, ipady=10, \
                                         sticky="news")
        self.notebook.columnconfigure(0, weight=4)
        self.notebook.rowconfigure(0, weight=4)

        self.frame1 = ttk.Frame(self.notebook)#, width=400, height=280)
        self.frame1.grid(row=0, column=0, sticky="news")
        self.frame1.columnconfigure(0, weight=4)
        self.frame1.rowconfigure(1, weight=4)

        self.notebook.add(self.frame1, text='Blocks')
        
        cur_col = 0# switching to notebook changes this

        self.block_label = ttk.Label(self.frame1, text="Blocks")
        self.block_label.grid(row=0,column=cur_col,sticky='SW', pady=(5,0), padx=5)

        self.block_list_var = tk.StringVar(value=[])

        self.blocklistbox = tk.Listbox(self.frame1, \
                                        listvariable=self.block_list_var, \
                                        height=6, \
                                        #selectmode='extended'
                                       )

        
        self.blocklistbox.grid(column=cur_col, row=1,sticky='nwes', pady=(0,5), padx=5)
        self.blocklistbox.bind('<<ListboxSelect>>', self.block_selected)


        padx_opts = {'padx':10}

        # Input display and buttons
        self.input1_label = ttk.Label(self.frame1, text="Input 1")
        self.input1_label.grid(column=cur_col, row=2, sticky="SW", pady=(5,0), **padx_opts)
        self.input1_var = tk.StringVar()
        self.input1_box = ttk.Entry(self.frame1, textvariable=self.input1_var)
        self.input1_box.grid(column=cur_col, row=3, sticky="NWE", pady=(0,5), **padx_opts)
        self.set_intput1_btn = ttk.Button(self.frame1, text='Set Input 1', command=self.on_set_input1)
        self.set_intput1_btn.grid(column=cur_col, row=4, pady=(2,5))
        self.input2_label = ttk.Label(self.frame1, text="Input 2")
        self.input2_label.grid(column=cur_col, row=5, sticky="SW", pady=(5,0), **padx_opts)
        self.input2_var = tk.StringVar()
        self.input2_box = ttk.Entry(self.frame1, textvariable=self.input2_var)
        self.input2_box.grid(column=cur_col, row=6, sticky="NWE", pady=(0,5), **padx_opts)
        self.set_intput2_btn = ttk.Button(self.frame1, text='Set Input 2', command=self.on_set_input2)
        self.set_intput2_btn.grid(column=cur_col, row=7, pady=(2,5))

        self.input1_widgets = [self.input1_label, self.input1_box, self.set_intput1_btn]
        self.input2_widgets = [self.input2_label, self.input2_box, self.set_intput2_btn]
        
        # Placement display and buttons
        self.placement_label = ttk.Label(self.frame1, text="Placement")
        self.placement_label.grid(column=cur_col, row=8, sticky="SW", pady=(5,0), **padx_opts)
        self.placement_var = tk.StringVar()
        self.placement_box = ttk.Entry(self.frame1, textvariable=self.placement_var)
        self.placement_box.grid(column=cur_col, row=9, sticky="NWE", pady=(0,5), **padx_opts)
        self.placement_btn = ttk.Button(self.frame1, text='Place', command=self.on_place_btn)
        self.placement_btn.grid(column=cur_col, row=10, pady=(2,5))

        col1_list = [self.input1_label, self.input1_box, self.set_intput1_btn, \
                     self.input2_label, self.input2_box, self.set_intput2_btn]

        #for i, widget in enumerate(col1_list):
        #    widget.grid(row=i+2, column=cur_col)
                                    

        #.grid_remove()
        # button
        self.button = ttk.Button(self.frame1, text='Add Block')
        self.button['command'] = self.add_block
        self.button.grid(row=20,column=cur_col,**self.options)

        # make other frames for notebook
        self.make_actuator_frame()
        self.make_sensors_frame()


    def on_zoom_btn(self, event=None):
        xmin = float(self.xmin_var.get())
        xmax = float(self.xmax_var.get())
        ymin = float(self.ymin_var.get())
        ymax = float(self.ymax_var.get())
        self.ax.set_xlim([xmin,xmax])
        self.ax.set_ylim([ymin,ymax])
        self.bd.axis_off()        
        self.canvas.draw()


    def check_block_selected(self, msg):
        selected_indices = self.blocklistbox.curselection()
        if not selected_indices:
            showinfo(title='Information',
                     message=msg)
            return 0
        # everything is fine:
        return 1


    def get_selected_block_index(self):
        selected_indices = self.blocklistbox.curselection()
        if type(selected_indices) == list:
            return selected_indices[0]
        else:
            return selected_indices


    def get_selected_block_name(self, msg):
        if not self.check_block_selected(msg):
            return None
        else:
            selected_indices = self.blocklistbox.curselection()
            print("selected_indices: %s" % selected_indices)
            block_name = self.blocklistbox.get(selected_indices)
            return block_name


    def on_set_input1(self, *args, **kwargs):
        print("in on_set_input1")
        selected_index = self.get_selected_block_index()
        block_name = self.get_selected_block_name("you must select a block before setting its input(s)")
        if not block_name:
            return None
        block = self.get_block_by_name(block_name)
        input_dialog = input_chooser(block, parent=self, geometry='300x200', \
                                     selected_index=selected_index)
        input_dialog.grab_set()#<-- this "unchooses" the block

        # reset the block choice and show selected inputs:
        print("back to main window")
        self.blocklistbox.select_set(selected_index)

        #class input_chooser(my_toplevel_window):
        #    def __init__(self, block, parent, title="Input Chooser Dialog", \
        

        # - pop up a small custom dialog
        # - let user choose the input
        # - set the block's input
        # - destroy the dialog

    def on_set_input2(self, *args, **kwargs):
        block_name = self.get_selected_block_name("you must select a block before setting its input(s)")
        selected_index = self.get_selected_block_index()
        if not block_name:
            return None
        block = self.get_block_by_name(block_name)
        input2_dialog = input2_chooser(block, parent=self, geometry='300x200', \
                                       selected_index=selected_index)
        input2_dialog.grab_set()


    def make_actuator_frame(self):
        self.act_frame = ttk.Frame(self.notebook)#, width=400, height=280)
        self.act_frame.grid(row=0, column=0, sticky="news")
        self.act_frame.columnconfigure(0, weight=4)
        self.act_frame.rowconfigure(1, weight=4)


        myroot = self.act_frame
        kwargs = {'root':myroot}# note: helper functions handle padding
        curcol = 0# switching to notebook changes this

        self.act_label1 = self.make_label_and_grid_sw("Actuators", 0, curcol, **kwargs)
        self.make_listbox_and_var("actuators", 1, curcol, root=myroot, grid_opts={'sticky':'news'})
        self.add_actuator_btn = self.make_button_and_grid("Add Actuator", \
                                                          row=2, col=curcol, \
                                                          command=self.on_add_actuator_btn, \
                                                          sticky='n', \
                                                          **kwargs)
        self.notebook.add(self.act_frame, text='Actuators')


    def refresh_actuator_names(self):
        self.actuators_var.set(self.bd.actuator_name_list)


    def refresh_sensor_names(self):
        self.sensors_var.set(self.bd.sensor_name_list)
        
        

    def on_add_actuator_btn(self, *args, **kwargs):
        ## place_dialog.set_block_to_place(block_name)
        ## place_dialog.grab_set()
        actuator_dialog = actuator_chooser(parent=self, geometry='300x600', \
                                           max_params=5)
        actuator_dialog.grab_set()


    def on_add_sensor_btn(self, *arg, **kwargs):
        sensor_dialog = sensor_chooser(parent=self, geometry='300x600', \
                                           max_params=5)
        sensor_dialog.grab_set()
        

    def make_sensors_frame(self):
        self.sensors_frame = ttk.Frame(self.notebook)#, width=400, height=280)
        self.sensors_frame.grid(row=0, column=0, sticky="news")
        self.sensors_frame.columnconfigure(0, weight=4)
        self.sensors_frame.rowconfigure(1, weight=4)

        myroot = self.sensors_frame
        kwargs = {'root':myroot}# note: helper functions handle padding
        curcol = 0# switching to notebook changes this

        self.sensors_label1 = self.make_label_and_grid_sw("Sensors", 0, curcol, **kwargs)
        self.make_listbox_and_var("sensors", 1, curcol, root=myroot, grid_opts={'sticky':'news'})
        self.add_sensor_btn = self.make_button_and_grid("Add Sensor", \
                                                          row=2, col=curcol, \
                                                          command=self.on_add_sensor_btn, \
                                                          sticky='n', \
                                                          **kwargs)
        
        self.notebook.add(self.sensors_frame, text='Sensors')


    def on_draw_btn(self, *args, **kwargs):
        print("you pressed draw")
        self.ax.clear()
        self.bd.update_block_list()
        block_list = self.bd.block_list
        print("block_list: %s" % block_list)
        self.bd.ax = self.ax
        self.bd.draw()
        xlims = self.bd.get_xlims()
        ylims = self.bd.get_ylims()
        self.ax.set_xlim(xlims)
        self.ax.set_ylim(ylims)
        self.xmin_var.set(str(xlims[0]))
        self.xmax_var.set(str(xlims[1]))
        self.ymin_var.set(str(ylims[0]))
        self.ymax_var.set(str(ylims[1]))
        
        self.bd.axis_off()        
        self.canvas.draw()
        
        
    def fill_placement_entry(self, place_str):
        self.placement_var.set(place_str)

        
    def clear_boxes(self, *args, **kwargs):
        attr_list = ["input1_var", "input2_var", "placement_var"]
        for attr in attr_list:
            myvar = getattr(self, attr)
            myvar.set("")


    def on_place_btn(self, *args, **kwargs):
        selected_indices = self.blocklistbox.curselection()
        if not selected_indices:
            showinfo(title='Information',
                     message='You must select a block before placing it.')
            return
        
        place_dialog = place_block_dialog(title="Place Block", parent=self)
        block_name = self.blocklistbox.get(selected_indices)
        place_dialog.set_block_to_place(block_name)
        place_dialog.grab_set()

        
#root = tkinter.Tk()
#root.wm_title("Embedding in Tk")


#btn = ttk.Label(root, text='A simple plot')



#canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
#canvas.draw()
##canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
#canvas.get_tk_widget().grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

#toolbar = NavigationToolbar2Tk(canvas, root)
#toolbar.update()
#canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
#toolbar.get_tk_widget().grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

# navigation toolbar

#_____________________________
#

#def on_key_press(event):
#    print("you pressed {}".format(event.key))
#    key_press_handler(event, canvas, toolbar)


#canvas.mpl_connect("key_press_event", on_key_press)

## def onclick(event):
##     print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
##           ('double' if event.dblclick else 'single', event.button,
##            event.x, event.y, event.xdata, event.ydata))

## cid = canvas.mpl_connect('button_press_event', onclick)


## def _quit():
##     root.quit()     # stops mainloop
##     root.destroy()  # this is necessary on Windows to prevent
##                     # Fatal Python Error: PyEval_RestoreThread: NULL tstate


## button = ttk.Button(master=root, text="Quit", command=_quit)
## #button.pack(side=tkinter.BOTTOM)
## button.grid(column=1, row=1, sticky=tk.W, padx=5, pady=5)

#w = 1200 # width for the Tk root
#h = 1000 # height for the Tk root
#w = 800
#h = 600
#x = 100
#y = 100
#root.geometry('%dx%d+%d+%d' % (w, h, x, y))
#root.geometry('%dx%d' % (w, h))
#root.state('zoomed')
#tkinter.mainloop()
# If you put root.destroy() here, it will cause an error if the window is
# closed with the window manager.



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        # configure the root window
        self.title('My Awesome App')
        self.geometry('900x600')
        #self.columnconfigure(0, weight=3)
        #self.columnconfigure(1, weight=1)
        #self.rowconfigure(1, weight=3)
        #self.grid_columnconfigure(0, weight=3)

if __name__ == "__main__":
    app = pybd_gui()
    app.mainloop()
