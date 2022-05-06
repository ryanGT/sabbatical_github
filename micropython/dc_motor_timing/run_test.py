import matplotlib.pyplot as plt
import numpy as np
import pyboard
portname = "/dev/tty.usbmodem207831A44E532"
#fn = "main_PD_control.py"
#fn = "main.py"
fn = "main.py"
# how do I do this using mpremote?
output = pyboard.execfile(fn, device=portname)
mystr = output.decode()
mylist = mystr.split('\r\n')
mylist.pop(-1)
mylist.pop(0)
mylist.pop(0)
mylist_delim = [row.split(',') for row in mylist]
mystrarray = np.array(mylist_delim)
data = mystrarray.astype(int)
enc = data[:,0]*256+data[:,1]
n_echo = data[:,2]*256+data[:,3]
delta_n = n_echo[1:] - n_echo[0:-1]
dt_micros = data[:,4]*256+data[:,5]

plt.figure(1)
plt.clf()
plt.plot(n_echo)

plt.figure(2)
plt.clf()
plt.plot(delta_n)

plt.figure(3)
#plt.clf()
plt.plot(dt_micros[2:])


print("dt_max: %0.4g" % dt_micros.max())
print("dt_min: %0.4g" % (dt_micros[2:]).min())

#data[i,0] = enc
#data[i,1] = e
#data[i,2] = v_i
#enc = data[:,0]
#e = data[:,1]
#v = data[:,2]

## N = len(enc)
## u = np.zeros(N, dtype=np.int16)
## u[10:] = 200

## plt.figure(1)
## plt.clf()
## plt.plot(u)
## plt.plot(enc)
## plt.plot(e)
## plt.plot(v)

plt.show()
