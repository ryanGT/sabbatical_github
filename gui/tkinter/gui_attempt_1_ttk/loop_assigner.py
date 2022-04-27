import tkinter
import tkinter as tk
from tkinter import ttk

from tkinter import ttk
from tkinter.messagebox import showinfo

from tkinter_utils import my_toplevel_window

import py_block_diagram as pybd

import copy


def get_selected_blocks(widget, block_inds):
    block_names = []
    for ind in block_inds:
        curname = widget.get(ind)
        block_names.append(curname)
        
    return block_names


class loop_number_assigner(my_toplevel_window):
    def __init__(self, parent, title="Loop Number Assigner Dialog", \
                 geometry='500x450', max_loops=3, \
                 main_label_text="Assign blocks to loop numbers"):        
        super().__init__(parent, title=title, geometry=geometry)
        self.bd = self.parent.bd
        self.columnconfigure(0, weight=4)
        self.main_label_text = main_label_text
        self.max_loops = max_loops
        self.make_widgets()
        self.show_existing_assignments()


    def show_existing_assignments(self):
        """If blocks have been previously assigned, show them in the
        correct boxes."""
        # Approach:
        #
        # - check each block to see if it has a valid loop number
        # - send the block to that loop box if set
        print("in show_existing_assignments")
        for curname in self.all_block_names:
            print("curname: %s" % curname)
            block = self.bd.get_block_by_name(curname)
            if hasattr(block, "loop_number"):
                print("block.loop_number: %s" % block.loop_number)
                if block.loop_number:
                    self.send_blocks_to_loop(block.loop_number, [curname])
            else:
                print("no loop_number attr")
        

    def make_widgets(self):
        mycol = 0
        #self.make_label_and_grid_sw(self.main_label_text, 0, mycol)
        self.left_frame = ttk.Frame(self)
        currow = 0
        self.make_label_and_grid_sw("Assign Blocks to Loop Number", currow, mycol, root=self.left_frame)
        currow += 1
        self.make_combo_and_var_grid_nw("loop_number", currow, mycol, root=self.left_frame)
        self.loop_numbers = list(range(1,self.max_loops+1))
        self.loop_number_combobox['values'] = self.loop_numbers
        #self.loop_number_var.set(self.loop_numbers)
        currow += 1
        
        self.make_label_and_grid_sw("Available Blocks", currow, mycol, root=self.left_frame)
        currow += 1
        self.all_block_names = self.bd.block_name_list
        self.make_listbox_and_var("available_blocklist", currow, mycol, selectmode="multiple", \
                                  root=self.left_frame)
        currow += 1
        self.available_blocks = copy.copy(self.all_block_names)
        self.available_blocklist_var.set(self.available_blocks)
        
        

        self.assign_btn = self.make_button_and_grid("Assign", currow, mycol, \
                                                    command=self.on_assign_btn, root=self.left_frame)
        currow += 1
        self.save_btn = self.make_button_and_grid("Save and Exit", currow, mycol, \
                                                  command=self.on_save_btn, root=self.left_frame)
        currow += 1
        self.cancel_btn = self.make_button_and_grid("Cancel", currow, mycol, \
                                                    command=self.on_cancel_btn, root=self.left_frame)
        currow += 1
        
        self.left_frame.grid(row=0, column=0, rowspan=10, sticky='N')



        # widgets in col 1 contain the blocks assigned to each loop
        mycol = 1
        currow = 0
        for i in range(self.max_loops):
            j = i+1
            label_j = "Loop %i Blocks" % j
            self.make_label_and_grid_sw(label_j, currow, mycol)
            currow += 1
            attr_j = "loop_%i_blocks" % j
            self.make_listbox_and_var(attr_j, currow, mycol, selectmode="multiple")
            setattr(self, attr_j, [])
            currow += 1


        self.unassign_btn = self.make_button_and_grid("Unassign", currow, mycol, \
                                                      command=self.on_unassign_btn)
        currow += 1


    def send_blocks_to_loop(self, loop_number, block_names):
        # Approach:
        #
        # - put blocks whose names are in block_names into the listbox
        #   associated with loop_number
        #
        # - remove block names from available_blocklist
        #
        # - get things right in the various lists that I maintain
        #
        # - update the variables associated with the listbox widgets
        
        # send blocks to new listbox:
        list_attr = "loop_%i_blocks" % loop_number
        mylist = getattr(self, list_attr)
        mylist += block_names
        var_attr = list_attr + '_var'
        var = getattr(self, var_attr)
        var.set(mylist)

        # remove blocks from available widget:
        for curname in block_names:
            self.available_blocks.remove(curname)
            
        self.available_blocklist_var.set(self.available_blocks)


    def append_blocks_to_available(self, block_names):
        for curname in block_names:
            self.available_blocks.append(curname)
            
        self.available_blocklist_var.set(self.available_blocks)


    def remove_blocks_from_list(self, basename, block_names):
        print("block_names: %s" % block_names)
        mylist = getattr(self, basename)
        for name in block_names:
            mylist.remove(name)

        var_attr = basename + '_var'
        var = getattr(self, var_attr)
        var.set(mylist)
        print("after removal:")
        print("mylist: %s" % mylist)
        widget_attr = basename + "_listbox"
        widget = getattr(self, widget_attr)
        widget.selection_clear(0, 'end')
        
        
    def on_unassign_btn(self, *args, **kwargs):
        print("in on_unassign_btn")
        # Approach:
        # - find any selected blocks in any listbox above
        for i in range(self.max_loops):
            j = i+1
            basename_j = "loop_%i_blocks" % j
            attr_j = basename_j + "_listbox"
            widget_j = getattr(self, attr_j)
            selected_blocks = widget_j.curselection()
            if selected_blocks:
                selected_names = get_selected_blocks(widget_j, selected_blocks)
                print("selected_names: %s" % selected_names)
                # now move those namnes from widget_j to the available_blocks listbox
                self.append_blocks_to_available(selected_names)
                self.remove_blocks_from_list(basename_j, selected_names)
                

    def on_assign_btn(self, *args, **kwargs):
        # Approach:
        # - is loop # selected?
        # - are blocks selected?
        # - if both, send selected blocks to selected loop
        print("in on_assign_btn")
        loop_num_str = self.loop_number_var.get()
        if not loop_num_str:
            print("no loop selected")
            # exit this method:
            return
        print("loop_num_str: %s" % loop_num_str)
        loop_number = int(loop_num_str)
        print("loop_number: %i" % loop_number)
        selected_blocks = self.available_blocklist_listbox.curselection()
        if not selected_blocks:
            print("no blocks selected")
            # exit this method:
            return 
        print("selected_blocks: %s" % str(selected_blocks))
        block_names = []
        for ind in selected_blocks:
            curname = self.available_blocklist_listbox.get(ind)
            block_names.append(curname)
        print("block_names: %s" % str(block_names))
        self.send_blocks_to_loop(loop_number, block_names)


    def on_save_btn(self, *args, **kwargs):
        print("in on_save_btn")
        # Approach:
        #
        # - check that available blocks is empty
        #
        # - for each loop widget:
        #
        #     - get the blocks by name
        #     - assign their loop numbers
        #
        # - quit
        if len(self.available_blocks) > 0:
            #showinfo
            showinfo(title='Information',
                     message="You must assign all blocks to a loop number before saving")
            return

        for j in self.loop_numbers:
            attr_j = "loop_%i_blocks" % j
            list_j = getattr(self, attr_j)
            for curname in list_j:
                block = self.bd.get_block_by_name(curname)
                setattr(block, "loop_number", j)

        self.destroy()

    def on_cancel_btn(self, *args, **kwargs):
        print("in on_canel_btn")
        self.destroy()
