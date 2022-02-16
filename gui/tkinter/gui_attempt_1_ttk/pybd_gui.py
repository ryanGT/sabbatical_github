"""
===============
Embedding in Tk
===============

"""


#iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii
#
# Issues:
#
# - how do I handle sensors and actuators so that plants can be
#   created?
#     - gui could show actuator and sensor comboboxes when plant is selected
#         - or only sensor for plant_no_actuator
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
# Resovled:
# - selecting a block type and then selecting an input block messes up
#   the current selection of the block type listbox
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

# Initialize style
#s = ttk.Style()
# Create style used by default for all Frames
#s.configure('TFrame', background='green')

# Create style for the first frame
#s.configure('Frame1.TFrame', background='red')

from tkinter import simpledialog

import py_block_diagram as pybd

pad_options = {'padx': 5, 'pady': 5}

#class MyDialog(simpledialog.Dialog):
class MyDialog(tk.Toplevel):
    def __init__(self, parent, title="Add Block Dialog"):
        super().__init__(parent)
        self.selected_block_type = None
        self.input_block_name = None
        self.input2_block_name = None
        self.input3_block_name = None
        self.parent = parent
        self.geometry('800x600')
        self.title(title)
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
                           self.input_choice, self.go_button]
        for i, widget in enumerate(column1_widgets):
            widget.grid(row=i, column=1, sticky='W', **pad_options)


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
        selection = self.blockchoice.curselection()
        print("block type selection:")
        print(selection)
        if not selection:
            print("no selection")
            return None
        block_type = self.get_selected_block_type()
        print("block_type: %s" % block_type)
        self.selected_block_type = block_type
        suggested_name = self.parent.block_diagram.suggest_block_name(block_type)
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
        # - look up the block in parent.block_diagram
        if self.input_block_name is not None:
            print("input block name: %s" % self.input_block_name)
            kwargs['input'] = self.input_block_name
        if self.input2_block_name is not None:
            kwargs['input2'] = self.input2_block_name
        if self.input3_block_name is not None:
            kwargs['input3'] = self.input3_block_name
            
        block_name = self.block_name.get()
        block_class = getattr(pybd, block_type)
        # how do I handle cases with input(s) set?
        new_block = pybd.create_block(block_class, block_type, block_name, **kwargs)
        self.parent.append_block_to_dict(block_name, new_block)
        #self.parent.password = self.my_password
        self.destroy()


    def cancel_pressed(self):
        # print("cancel")
        self.destroy()


    def category_selected(self, event):
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
        
#    def buttonbox(self):
#        self.ok_button = tk.Button(self, text='OK', width=5, command=self.ok_pressed)
#        self.ok_button.pack(side="left")
#        cancel_button = tk.Button(self, text='Cancel', width=5, command=self.cancel_pressed)
#        cancel_button.pack(side="right")
#        self.bind("<Return>", lambda event: self.ok_pressed())
#        self.bind("<Escape>", lambda event: self.cancel_pressed())


#def mydialog(app):
#    dialog = MyDialog(title="Login", parent=app)
#    return dialog.my_username, dialog.my_password



class pybd_gui(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("900x600")
        self.mylabel = 'Python Block Diagram GUI'
        self.title(self.mylabel)
        self.resizable(1, 1)

        # configure the grid
        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=4)

        self.options = {'padx': 5, 'pady': 5}
        
        # configure the root window
        self.make_widgets()

        self.block_diagram = pybd.block_diagram()
        

    def get_block_name_list(self):
        #block_list = self.block_diagram._build_block_list()
        mylist = self.block_diagram.block_name_list
        return mylist


    def append_block_to_dict(self, block_name, new_block):
        self.block_diagram.append_block_to_dict(block_name, new_block)
        # update listbox
        self.block_list_var.set(self.block_diagram.block_name_list)
        
        
    def add_block(self):
        #showinfo(title='Information',
        #        message='add block pressed')
        mydialog = MyDialog(title="Add New Block", parent=self)
        mydialog.grab_set()
        print("%s, %s" % (mydialog.my_username, mydialog.my_password))

        
    def _quit(self):
        self.quit()     # stops mainloop
        self.destroy()  # this is necessary on Windows to prevent
                        # Fatal Python Error: PyEval_RestoreThread: NULL tstate

    def items_selected(self, event):
        """ handle item selected event
        """
        # get selected indices
        selected_indices = self.blocklistbox.curselection()
        # get selected items
        selected_langs = ",".join([self.blocklistbox.get(i) for i in selected_indices])
        msg = f'You selected: {selected_langs}'
        
        showinfo(
            title='Information',
            message=msg)


        if hasattr(self, "password"):
            print("parent password = %s" % self.password)
            

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
        self.canvas.get_tk_widget().grid(row=1, column=0, ipadx=40, ipady=20, sticky="news")

        self.toolbarFrame = ttk.Frame(master=self)
        self.toolbarFrame.grid(row=2,column=0)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbarFrame)


        self.quit_button = ttk.Button(master=self, text="Quit", command=self._quit)
        self.quit_button.grid(column=0, row=3, **self.options)


        # Column 1
        cur_col = 1

        self.block_label = ttk.Label(self, text="Blocks")
        self.block_label.grid(row=0,column=cur_col,sticky='NW', **self.options)

        self.block_list_var = tk.StringVar(value=[])

        self.blocklistbox = tk.Listbox(self, \
                                        listvariable=self.block_list_var, \
                                        height=6, \
                                        #selectmode='extended'
                                       )

        
        self.blocklistbox.grid(column=cur_col, row=1,sticky='nwes', **self.options)
        self.blocklistbox.bind('<<ListboxSelect>>', self.items_selected)

        # button
        self.button = ttk.Button(self, text='Add Block')
        self.button['command'] = self.add_block
        self.button.grid(row=2,column=cur_col,**self.options)



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
