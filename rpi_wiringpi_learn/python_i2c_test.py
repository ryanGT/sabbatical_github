#import smbus
import pigpio
import time
import numpy as np
import copy
import matplotlib.pyplot as plt
plt.close('all')

import serial_utils


def mysat(vin):
    if vin > 255:
        return 255
    elif vin < -255:
        return -255
    else:
        return vin

    

pi = pigpio.pi()
if not pi.connected:
    print("not connected")
    exit()

    
MEGA_ADDRESS = 0x08


m_ino = pi.i2c_open(1, MEGA_ADDRESS)

N = 100

t0 = time.time()
check_array = np.zeros(1000)
j = 0
n = 0
num_checks = np.zeros(N)
prev_check = 0
num_read = np.zeros(N)
v_sent = np.zeros(N)
enc_vect = np.zeros(N)
error_vect = np.zeros(N)
u_vect = np.zeros(N)
u_vect[10:] = 300
read_bytes = 6
responses = np.zeros((N,read_bytes))

# start new test
#pi.i2c_write_byte(t_ino, 1)
#pi.i2c_write_byte(m_ino, 1)


time.sleep(0.01)

kp = 3
kd = 1

spi_list = []

for i in range(N):
    # start new test
    pi.i2c_write_byte(m_ino, i+15)

    time.sleep(0.01)
    
    response = pi.i2c_read_byte(m_ino)
    #n = 0
    num_read[i] = response

    time.sleep(0.01)
    
t1 = time.time()
dt = t1-t0
print("dt = %f" % dt)


# In[169]:


ave_time_step = dt/N*1000

print("ave_time_step = %0.4g" % ave_time_step)
# In[170]:

pi.i2c_close(m_ino)

pi.stop()

