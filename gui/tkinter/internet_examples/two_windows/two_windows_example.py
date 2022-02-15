import tkinter as tk
from tkinter import ttk

class Demo1:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)
        self.button1 = ttk.Button(self.frame, text = 'New Window', width = 25, command = self.new_window)
        self.button1.pack()
        self.frame.pack()

    def new_window(self):
        self.newWindow = tk.Toplevel(self.master)
        self.app = Demo2(self.newWindow)
        print("text = %s" % self.app.mytext)
        


class Demo2:
    def __init__(self, master):
        self.master = master
        self.frame = ttk.Frame(self.master)
        self.quitButton = ttk.Button(self.frame, text = 'Quit', width = 25, command = self.close_windows)
        self.quitButton.pack()
        self.mytext = tk.StringVar()
        self.myentry = ttk.Entry(self.master, textvariable=self.mytext)
        self.myentry.pack()
        self.frame.pack()


    def close_windows(self):
        self.
        self.master.destroy()


def main(): 
    root = tk.Tk()
    app = Demo1(root)
    root.mainloop()

if __name__ == '__main__':
    main()
