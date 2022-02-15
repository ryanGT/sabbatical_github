from tkinter import *
from tkinter import ttk

def selectItem(a):
    curItem = tree.focus()
    print(tree.item(curItem))

root = Tk()
tree = ttk.Treeview(root, columns=("blocks"))
#tree["columns"] = ("date", "time", "loc")

#tree.column("date", width=65)
#tree.column("time", width=40)
#tree.column("loc", width=100)

#tree.heading("blocks", text="Date")
#tree.heading("time", text="Time")
#tree.heading("loc", text="Loc")
tree.bind('<ButtonRelease-1>', selectItem)

tree.insert("","end",text = "Block1")#,values = ("I","don't",'know'))

tree.grid()
root.mainloop()
