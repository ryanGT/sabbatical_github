#import smbus
import pigpio
import time
import numpy as np
import copy
import matplotlib.pyplot as plt
plt.close('all')

#import serial_utils

pi = pigpio.pi()
if not pi.connected:
    print("not connected")
    exit()

    
TIMING_ADDRESS = 0x05
#MOTOR_ADDRESS = 0x04


# setup the initial i2c connection:
t_ino = pi.i2c_open(1, TIMING_ADDRESS)#t_ino is the timing arduino
#m_ino = pi.i2c_open(1, MOTOR_ADDRESS)

# setup the variables and arrays for running a test
# and storig the data
N = 5000

t0 = time.time()
check_array = np.zeros(1000)
j = 0
n = 0
num_checks = np.zeros(N)
prev_check = 0

read_bytes = 3
responses = np.zeros((N,read_bytes))
t = np.zeros(N)
num_read = np.zeros(N)

# start new test by sending the number 1 to the Arduino(s)
pi.i2c_write_byte(t_ino, 1)
##!##pi.i2c_write_byte(m_ino, 1)


time.sleep(0.01)

# iterate for N time steps
for i in range(N):
    # read one byte from the timing Arduino to see if the
    # time step counter has changed
    check = pi.i2c_read_byte(t_ino)
    while (check == prev_check):
        # if the time step counter has not changed,
        # keeping asking for one byte until it does
        check = pi.i2c_read_byte(t_ino)
    # acknowledge that the RPi has received the "go" signal
    # that the next time step has arrived
    #pi.i2c_write_byte(t_ino, 7)#<-- i2c write error occurs here
	#                           # - is it possible that one Arduino cannot
	#   switch from writing to reading fast enough
	#   sometimes?
	#     - in my ACC paper, this write went to
	#       the other Arduino
    num_read[i] = check# log the time step counter to see if we
    #                   # get them all
    #e, cur_resp = pi.i2c_read_device(t_ino, 3)# read the micros t value from the
    #                                          # timing Arduino to see how we are doing
    #                                          # on consistently having 2000 microseconds
    #                                          # per time step
    #t_i = cur_resp[1] + cur_resp[2]*256# convert the two bytes for t to a 16-bit integer
    #t[i] = t_i

    # save the time step counter for the next loop
    prev_check = check


# tell the Arduino that the test is over
pi.i2c_write_byte(t_ino, 9)

# verify how long N time steps took
t1 = time.time()
dt = t1-t0
print("dt = %f" % dt)

dt/N*1000

# close the i2c connection
pi.i2c_close(t_ino)
###pi.i2c_close(m_ino)
pi.stop()



def n_unwrap(n_in):
    nvect = copy.copy(n_in)
    ndiff = nvect[1:]-nvect[0:-1]
    ind_array = np.where(ndiff<-250)[0]
    for switch_ind in ind_array:
        nvect[switch_ind+1:] +=256
    return nvect


# The time step counter was read as single bytes.
# So, every time it goes back to zero, we need to add
# 256 to it:
n_unw = n_unwrap(num_read)
print("n_unw.max = %i " % n_unw.max())
n_expected = np.arange(1,N+1,1)# the time step counter should go from 1 to N+1 in steps of 1
                               # if we read it correctly at every time step
ndiff = n_unw-n_expected
print("max diff = " + str(np.abs(ndiff).max()))


#dt_vect = t[1:] - t[0:-1]
#inds = np.where(dt_vect<0)
#dt_vect[inds[0]] += 2**16

plt.figure(1)
plt.plot(n_unw)
plt.title("n unwrapped")

plt.figure(2)
plt.plot(ndiff)
plt.title("ndiff")

#plt.figure(3)
#plt.plot(dt_vect)
#plt.title("dt")

plt.show()
