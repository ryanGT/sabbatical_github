#import smbus
import pigpio
import time
import numpy as np
import copy
import matplotlib.pyplot as plt
plt.close('all')

import serial_utils

import control
from control import TransferFunction as TF

import sys
import zmq
import time

# user timer arduino flag
TA = 0

if not TA:
    #  Socket to talk to server
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.CONFLATE,1)
    socket.setsockopt_string(zmq.SUBSCRIBE,'')
    print("Connectiong to zeroMQ timing server...")
    socket.connect("tcp://localhost:5556")


# Subscribe to zipcode, default is NYC, 10001
#zip_filter = sys.argv[1] if len(sys.argv) > 1 else "10001"
#socket.setsockopt_string(zmq.SUBSCRIBE, zip_filter)



import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
LED = 17
ledState = False
GPIO.setup(LED,GPIO.OUT)

ledState = 0




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

    
MOTOR_ADDRESS = 0x04

if TA:
    TIMER_ADDRESS = 0x05
    t_ino = pi.i2c_open(1, TIMER_ADDRESS)

m_ino = pi.i2c_open(1, MOTOR_ADDRESS)
h_spi = pi.spi_open(0, 200000)

#c, d = pi.i2c_read_device(h,8)




# In[168]:


N = 500

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
pi.i2c_write_byte(m_ino, 1)

if TA:
    pi.i2c_write_byte(t_ino, 1)

#time.sleep(0.001)

kp = 3
kd = 1

spi_list = []

t0 = time.time()

def get_int_zeroMQ():
    string = socket.recv_string()
    check = int(string)
    return check


def get_int_timer_ino():
    check = pi.i2c_read_byte(t_ino)
    return check


if TA:
    myfunc = get_int_timer_ino
else:
    myfunc = get_int_zeroMQ
    prev_check = myfunc()
    prev_check = myfunc()



for i in range(N):
    check = myfunc()
    while (check == prev_check):
        check = myfunc()
        
    GPIO.output(LED, GPIO.HIGH)
    num_read[i] = check
    #num_checks[i] = n
    #time.sleep(0.0001)

    #bus.write_byte(TIMING_ADDRESS, 7)
    #time.sleep(0.00001)
    e, cur_resp = pi.i2c_read_device(m_ino,6)
    #cur_resp = bus.read_i2c_block_data(MOTOR_ADDRESS,99,read_bytes)
    responses[i,:]= cur_resp[0:read_bytes]
    enc_i = cur_resp[3] + cur_resp[2]*256
    if enc_i > 30000:
        enc_i -= 2**16
    enc_vect[i] = enc_i
    # send pulse input to motor control Arduino
    e_i = u_vect[i] - enc_i
    error_vect[i] = e_i
    e_diff = e_i - error_vect[i-1]
    v_out = kp*e_i +kd*e_diff
    v_out = mysat(v_out)
    v_sent[i] = v_out

    if v_out < 0:
        v_out = 2**16+v_out
    
    msb = int(v_out/256)
    lsb = int(v_out % 256)
    #senddata = [30,msb,lsb]
    #senddata = [17,81]
    spi_data = [msb, lsb, 10]
    
    time.sleep(0.0001)

    spi_resp = pi.spi_xfer(h_spi, spi_data)
    spi_list.append(spi_resp)
    #pi.i2c_write_byte(m_ino, msb)
    #pi.i2c_write_byte(m_ino, lsb)
	#pi.i2c_write_device(m_ino,senddata)
    #bus.write_i2c_block_data(MOTOR_ADDRESS,33,senddata)
    

    #time.sleep(0.000001)
    #for i in range(100):
    #    a = 2*i
    prev_check = check
    GPIO.output(LED, GPIO.LOW)    

t1 = time.time()
loop_time = t1-t0
print("loop_time = %f" % loop_time)


# In[169]:


ave_time_step = loop_time/N*1000

print("ave_time_step = %0.4g" % ave_time_step)
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
n_unw -= n_unw[0]

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

n_motor = responses[:,1] + responses[:,0]*256
if np.abs(n_motor[0]) > 10:
    n_motor[0] = 0
#n_diff_motor = n_motor[1:] - n_motor[0:-1]
n_diff_motor_v_expected = n_expected - n_motor
enc = responses[:,3] + responses[:,2]*256
n_diff_motor_self = n_motor[1:] - n_motor[0:-1]

data = np.column_stack([n_motor, u_vect, error_vect, v_sent, enc])
labels = ['n_motor','u','e','v_sent','enc']

plt.figure(1)
plt.plot(n_motor, u_vect)
plt.plot(n_motor, v_sent)
plt.plot(n_motor, enc_vect)


plt.figure(2)
plt.plot(ndiff)
plt.plot(n_diff_motor_self)
plt.plot(n_diff_motor_v_expected)

pi.i2c_write_byte(m_ino, 2)#end test

if TA:
    pi.i2c_close(t_ino)    

pi.i2c_close(m_ino)
pi.spi_close(h_spi)

pi.stop()


plt.show()
