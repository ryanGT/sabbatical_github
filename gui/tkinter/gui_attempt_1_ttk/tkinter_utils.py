import tkinter
import tkinter as tk
from tkinter import ttk

from tkinter import ttk
from tkinter.messagebox import showinfo

def value_from_str(string_in):
    try:
        out = float(string_in)
        out2 = int(out)
        if abs(out2-out) < 1e-5:
            # it is basically an integer
            return out2
        else:
            return out
    except:
        # cannot be converted to float
        return string_in


class my_toplevel_window(tk.Toplevel):
    def __init__(self, parent, title="Cool Toplevel Window", geometry='800x600'):
        super().__init__(parent)
        self.parent = parent
        self.geometry(geometry)
        self.title(title)
        #self.make_widgets()


    def make_widgets(self):
        raise NotImplementedError("my_toplevel_window is intended to be an abstract class, you must override the make_widgets method")


    def make_label(self, text, root=None, attr=None):
        if root is None:
            root = self
        widget = ttk.Label(root, text=text)
        if attr is not None:
            # store widget to a parameter (attribute) of the class
            setattr(self, attr, widget)
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


    def make_label_and_grid_sw(self, text, row, col, root=None, attr=None):
        if root is None:
            root = self
        widget = self.make_label(text, root=root, attr=attr)
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


    def make_listbox_and_var(self, basename, row, col, root=None, height=6, grid_opts={}, \
                             selectmode='single'):
        if root is None:
            root = self

        myvar = tk.StringVar([])

        mywidget = tk.Listbox(root, \
                              listvariable=myvar, \
                              height=height, \
                              selectmode=selectmode, \
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



class window_with_param_widgets_that_appear_and_disappear(object):
    def update_param_labels(self, param_list):
        for i, param in enumerate(param_list):
            j = i+1
            label_attr = "param%i_label" % j
            widget = getattr(self, label_attr)
            widget['text'] = param


    def get_params_kwargs(self, N_params):
        kwargs = {}

        for i in range(N_params):
            j = i+1
            label_attr = "param%i_label" % j
            label_widget = getattr(self, label_attr)
            label_text = label_widget.cget("text")
            entry_attr = "param%i_var" % j
            entry_var = getattr(self, entry_attr)
            value = entry_var.get()
            value_out = value_from_str(value)
            kwargs[label_text] = value_out

        return kwargs


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

    
