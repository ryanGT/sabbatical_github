import tkinter
import mbox

root = tkinter.Tk()

Mbox = mbox.Mbox
Mbox.root = root

D = {'user':'Bob'}

b_login = tkinter.Button(root, text='Log in')
b_login['command'] = lambda: Mbox('Name?', (D, 'user'))
b_login.pack()

b_loggedin = tkinter.Button(root, text='Current User')
b_loggedin['command'] = lambda: Mbox(D['user'])
b_loggedin.pack()

root.mainloop()
