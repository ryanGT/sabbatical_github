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
N = 1000
num_read = np.zeros(N)


# blockinitcode
u = py_block_diagram.step_input(label="$U(s)$", on_time=0.1, amp=100)
sum1 = py_block_diagram.summing_junction()
PD = py_block_diagram.PD_controller(label="$D(s)$", Kp=3, Kd=0.1)
i2c_1 = py_block_diagram.i2c_read_block(i2c_connection=m_ino, pi_instance=pi, read_bytes=6, msb_index=2, lsb_index=3)
sat_block = py_block_diagram.saturation_block(label="sat", mymax=255)
spi_1 = py_block_diagram.spi_send_block(spi_connection=h_spi, pi_instance=pi, )



# make input connections here:
# blocksecondaryinitcode
sum1.input1 = u
sum1.input2 = i2c_1
PD.input = sum1
sat_block.input = PD




# start new test
pi.i2c_write_byte(t_ino, 1)
pi.i2c_write_byte(m_ino, 1)


time.sleep(0.01)


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
    u.find_output(i)
    i2c_1.read_data(i)
    sum1.find_output(i)
    PD.find_output(i)
    sat_block.find_output(i)
    spi_1.send_data(i)



    prev_check = check

t1 = time.time()
dt = t1-t0
print("dt = %f" % dt)


# In[169]:


ave_time_step = dt/N*1000

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

# plottingcode

pi.i2c_write_byte(m_ino, 2)#end test

pi.i2c_close(t_ino)
pi.i2c_close(m_ino)
pi.spi_close(h_spi)

pi.stop()


plt.show()
