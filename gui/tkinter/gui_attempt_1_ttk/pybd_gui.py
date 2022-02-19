#iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
#
# Issues:
#
# - how do I handle sensors and actuators so that plants can be
#   created?
#     - gui could show actuator and sensor comboboxes when plant is selected
#         - or only sensor for plant_no_actuator
# - make the set input buttons work
# - create a place block dialog
# - draw the block diagram
#
# Resovled:
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

#from tkinter import simpledialog

import py_block_diagram as pybd

pad_options = {'padx': 5, 'pady': 5}




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
        self.menubar.add_cascade(menu=self.menu_file, label='File')
        self.menubar.add_cascade(menu=self.menu_edit, label='Edit')
        self.menu_file.add_command(label='Save', command=self.on_save_menu)
        self.menu_file.add_command(label='Load', command=self.on_load_menu)        
        #menu_file.add_command(label='Open...', command=openFile)
        self.menu_file.add_command(label='Close', command=self._quit)

        #self.bind("<Key>", self.key_pressed)
        self.bind('<Control-q>', self._quit)
        self.bind('<Control-s>', self.on_save_menu)
        self.bind('<Control-l>', self.on_load_menu)
        self.bind('<Control-a>', self.add_block)
        self.bind('<Control-p>', self.on_place_btn)
        self.bind('<Control-d>', self.on_draw_btn)
        
        # configure the root window
        self.make_widgets()

        self.block_diagram = pybd.block_diagram()



    def key_pressed(self, event):
        print("pressed:")
        print(repr(event.char))


    def on_load_menu(self, *args, **kwargs):
        print("in menu laod")
        filename = tk.filedialog.askopenfilename(title = "Select Model to Load (CSV)",\
                                                 filetypes = (("csv files","*.csv"),("all files","*.*")))
        print (filename)
        
    
    def on_save_menu(self, *args, **kwargs):
        print("in menu save")
        filename = tk.filedialog.asksaveasfilename(title = "Select filename",\
                                                   filetypes = (("csv files","*.csv"),("all files","*.*")))
        print (filename)
        if filename:
            self.block_diagram.save_model_to_csv(filename)
            

    def get_block_name_list(self):
        #block_list = self.block_diagram._build_block_list()
        mylist = self.block_diagram.block_name_list
        return mylist


    def get_block_by_name(self, block_name):
        return self.block_diagram.get_block_by_name(block_name)

    
    def append_block_to_dict(self, block_name, new_block):
        self.block_diagram.append_block_to_dict(block_name, new_block)
        # update listbox
        self.block_list_var.set(self.block_diagram.block_name_list)
        
        
    def add_block(self, *args, **kwargs):
        #showinfo(title='Information',
        #        message='add block pressed')
        mydialog = add_block_dialog(title="Add New Block", parent=self)
        mydialog.grab_set()
        #print("%s, %s" % (mydialog.my_username, mydialog.my_password))

        
    def _quit(self, *args, **kwargs):
        self.quit()     # stops mainloop
        self.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate


    def block_selected(self, event):
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
                                         sticky="news", rowspan=16)

        self.toolbarFrame = ttk.Frame(master=self)
        self.toolbarFrame.grid(row=19,column=0)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)


        self.button_frame1 = ttk.Frame(self)
        self.quit_button = ttk.Button(self.button_frame1, text="Quit", command=self._quit)
        self.quit_button.grid(column=0, row=0, **self.options)

        self.draw_button = ttk.Button(self.button_frame1, text="Draw", command=self.on_draw_btn)
        self.draw_button.grid(column=1, row=0, **self.options)

        ## self.xlim_label = ttk.Label(self.button_frame1, text="xlim:")
        ## self.xlim.grid(row=0,column=2,sticky='E')
        ## self.xlim_var = tk.StringVar()
        ## self.xlim_box = ttk.Entry(self.button_frame1, textvariable=self.xlim_var)
        ## self.xlim_box.grid(column=3, row=0, sticky="W", padx=(0,5))

        
        self.button_frame1.grid(row=20, column=0)

        # Column 1
        cur_col = 1

        self.block_label = ttk.Label(self, text="Blocks")
        self.block_label.grid(row=0,column=cur_col,sticky='SW', pady=(5,0), padx=5)

        self.block_list_var = tk.StringVar(value=[])

        self.blocklistbox = tk.Listbox(self, \
                                        listvariable=self.block_list_var, \
                                        height=6, \
                                        #selectmode='extended'
                                       )

        
        self.blocklistbox.grid(column=cur_col, row=1,sticky='nwes', pady=(0,5), padx=5)
        self.blocklistbox.bind('<<ListboxSelect>>', self.block_selected)


        padx_opts = {'padx':10}

        # Input display and buttons
        self.input1_label = ttk.Label(self, text="Input 1")
        self.input1_label.grid(column=cur_col, row=2, sticky="SW", pady=(5,0), **padx_opts)
        self.input1_var = tk.StringVar()
        self.input1_box = ttk.Entry(self, textvariable=self.input1_var)
        self.input1_box.grid(column=cur_col, row=3, sticky="NWE", pady=(0,5), **padx_opts)
        self.set_intput1_btn = ttk.Button(self, text='Set Input 1')
        self.set_intput1_btn.grid(column=cur_col, row=4, pady=(2,5))
        self.input2_label = ttk.Label(self, text="Input 2")
        self.input2_label.grid(column=cur_col, row=5, sticky="SW", pady=(5,0), **padx_opts)
        self.input2_var = tk.StringVar()
        self.input2_box = ttk.Entry(self, textvariable=self.input2_var)
        self.input2_box.grid(column=cur_col, row=6, sticky="NWE", pady=(0,5), **padx_opts)
        self.set_intput2_btn = ttk.Button(self, text='Set Input 2')
        self.set_intput2_btn.grid(column=cur_col, row=7, pady=(2,5))

        self.input1_widgets = [self.input1_label, self.input1_box, self.set_intput1_btn]
        self.input2_widgets = [self.input2_label, self.input2_box, self.set_intput2_btn]
        
        # Placement display and buttons
        self.placement_label = ttk.Label(self, text="Placement")
        self.placement_label.grid(column=cur_col, row=8, sticky="SW", pady=(5,0), **padx_opts)
        self.placement_var = tk.StringVar()
        self.placement_box = ttk.Entry(self, textvariable=self.placement_var)
        self.placement_box.grid(column=cur_col, row=9, sticky="NWE", pady=(0,5), **padx_opts)
        self.placement_btn = ttk.Button(self, text='Place', command=self.on_place_btn)
        self.placement_btn.grid(column=cur_col, row=10, pady=(2,5))

        col1_list = [self.input1_label, self.input1_box, self.set_intput1_btn, \
                     self.input2_label, self.input2_box, self.set_intput2_btn]

        #for i, widget in enumerate(col1_list):
        #    widget.grid(row=i+2, column=cur_col)
                                    

        #.grid_remove()
        # button
        self.button = ttk.Button(self, text='Add Block')
        self.button['command'] = self.add_block
        self.button.grid(row=20,column=cur_col,**self.options)




    def on_draw_btn(self, *args, **kwargs):
        print("you pressed draw")
        self.ax.clear()
        self.block_diagram.update_block_list()
        block_list = self.block_diagram.block_list
        print("block_list: %s" % block_list)
        self.block_diagram.ax = self.ax
        self.block_diagram.draw()
        xlims = self.block_diagram.get_xlims()
        ylims = self.block_diagram.get_ylims()
        self.ax.set_xlim(xlims)
        self.ax.set_ylim(ylims)
        self.block_diagram.axis_off()        
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
