import smbus
import numpy as np
import copy

import time
import serial_utils

bus = smbus.SMBus(1)
TIMING_ADDRESS = 0x05
MOTOR_ADDRESS = 0x16

bus.write_byte(TIMING_ADDRESS, 7)
bus.write_byte(MOTOR_ADDRESS, 7)


# In[168]:


N = 1000
t0 = time.time()
check_array = np.zeros(1000)
j = 0
n = 0
num_checks = np.zeros(N)
prev_check = 0
num_read = np.zeros(N)
v_sent = np.zeros(N)
read_bytes = 6
responses = np.zeros((N,read_bytes))

# start new test
bus.write_byte(TIMING_ADDRESS, 1)
bus.write_byte(MOTOR_ADDRESS, 1)

time.sleep(0.01)

for i in range(N):
    check = bus.read_byte(TIMING_ADDRESS)
    #n = 0
    while (check == prev_check):
        check = bus.read_byte(TIMING_ADDRESS)
        #n += 1
        #j += 1
        #check_array[j] = check
        #time.sleep(0.00001)
    num_read[i] = check
    #num_checks[i] = n
    #time.sleep(0.0001)
    
    #bus.write_byte(TIMING_ADDRESS, 7)
    #time.sleep(0.00001)
    cur_resp = bus.read_i2c_block_data(MOTOR_ADDRESS,99,read_bytes)
    responses[i,:]= cur_resp[0:read_bytes]
    # send pulse input to motor control Arduino
    if ((i > 10) and (i<100)):
      v_sent[i] = 100
    else:
        v_sent[i] = 0

    msb = int(v_sent[i]/256)
    lsb = int(v_sent[i] % 256)
    senddata = [msb,lsb]
    
    #time.sleep(0.00001)
    #bus.write_i2c_block_data(MOTOR_ADDRESS,33,senddata)
    

    #time.sleep(0.000001)
    #for i in range(100):
    #    a = 2*i
    prev_check = check
t1 = time.time()
dt = t1-t0
print("dt = %f" % dt)


# In[169]:


dt/N*1000


# In[170]:


def n_unwrap(n_in):
    nvect = copy.copy(n_in)
    ndiff = nvect[1:]-nvect[0:-1]
    ind_array = np.where(ndiff<-250)[0]
    for switch_ind in ind_array:
        nvect[switch_ind+1:] +=256
    return nvect


# In[171]:


n_unw = n_unwrap(num_read)


# In[172]:


print("n_unw.max = %i " % n_unw.max())


# In[173]:


n_expected = np.arange(1,N+1,1)


# In[174]:


ndiff = n_unw-n_expected


# In[175]:


print("max diff = " + str(np.abs(ndiff).max()))


# In[176]:


ndiff


# In[177]:


i


# In[8]:


check


# In[ ]:




