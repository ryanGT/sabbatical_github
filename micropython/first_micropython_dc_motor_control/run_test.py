import matplotlib.pyplot as plt
import numpy as np
import pyboard
portname = "/dev/tty.usbmodem207831A44E532"
#fn = "main_PD_control.py"
#fn = "main.py"
fn = "main_P_control.py"
output = pyboard.execfile(fn, device=portname)
mystr = output.decode()
mylist = mystr.split('\r\n')
mylist.pop(-1)
mylist.pop(0)
mylist.pop(0)
mylist_delim = [row.split(',') for row in mylist]
mystrarray = np.array(mylist_delim)
data = mystrarray.astype(int)
#data[i,0] = enc
#data[i,1] = e
#data[i,2] = v_i
enc = data[:,0]
e = data[:,1]
v = data[:,2]

N = len(enc)
u = np.zeros(N, dtype=np.int16)
u[10:] = 200

plt.figure(1)
plt.plot(u)
plt.plot(enc)
plt.plot(e)
plt.plot(v)

plt.show()
