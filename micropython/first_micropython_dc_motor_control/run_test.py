import matplotlib.pyplot as plt
import numpy as np
import pyboard
portname = "/dev/tty.usbmodem207831A44E532"
output = pyboard.execfile("main.py", device=portname)
mystr = output.decode()
mylist = mystr.split('\r\n')
mylist.pop(-1)
mylist.pop(0)
mylist.pop(0)
mylist_delim = [row.split(',') for row in mylist]
mystrarray = np.array(mylist_delim)
data = mystrarray.astype(int)
enc = data[:,0]*256+data[:,1]
N = len(enc)
u = np.zeros(N, dtype=np.int16)
u[10:100] = 200

plt.figure(1)
plt.plot(u)
plt.plot(enc)

plt.show()
