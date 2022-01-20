#import smbus
import pigpio
import time
import numpy as np
import copy
import matplotlib.pyplot as plt
plt.close('all')
import py_block_diagram
import serial_utils


pi = pigpio.pi()
if not pi.connected:
    print("not connected")
    exit()


# leave this as manual for now
TIMING_ADDRESS = 0x05
MOTOR_ADDRESS = 0x04


t_ino = pi.i2c_open(1, TIMING_ADDRESS)
m_ino = pi.i2c_open(1, MOTOR_ADDRESS)
h_spi = pi.spi_open(0, 400000)

#c, d = pi.i2c_read_device(h,8)




# In[168]:

# sysprecode

# blockinitcode


# make input connections here:
# blocksecondaryinitcode



# start new test
pi.i2c_write_byte(t_ino, 1)
pi.i2c_write_byte(m_ino, 1)


time.sleep(0.01)

t0 = time.time()

for i in range(N):
    check = pi.i2c_read_byte(t_ino)
    #n = 0
    while (check == prev_check):
        check = pi.i2c_read_byte(t_ino)
        #n += 1
        #j += 1
        #check_array[j] = check
        #time.sleep(0.00001)
    num_read[i] = check
    #num_checks[i] = n
    #time.sleep(0.0001)

    #bus.write_byte(TIMING_ADDRESS, 7)
    #time.sleep(0.00001)

    # pythonloopcode


    prev_check = check
    
t1 = time.time()
loop_dt = t1-t0
print("loop_dt = %f" % loop_dt)


# In[169]:


ave_time_step = loop_dt/N*1000

print("ave_time_step = %0.4g" % ave_time_step)
# In[170]:


# system post loop code:

def n_unwrap(n_in):
    nvect = copy.copy(n_in)
    ndiff = nvect[1:]-nvect[0:-1]
    ind_array = np.where(ndiff<-250)[0]
    for switch_ind in ind_array:
        nvect[switch_ind+1:] +=256
    return nvect


n_unw = n_unwrap(num_read)

print("n_unw.max = %i " % n_unw.max())

n_expected = np.arange(1,N+1,1)
ndiff = n_unw-n_expected
print("max diff = " + str(np.abs(ndiff).max()))

pi.i2c_write_byte(m_ino, 2)#end test

pi.i2c_close(t_ino)
pi.i2c_close(m_ino)
pi.spi_close(h_spi)

pi.stop()


# plottingcode

plt.show()
