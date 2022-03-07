import pyb, time
#from ulab import numpy as np

#def tick(timer):                # we will receive the timer object when being called
#    print(timer.counter())      # show current timer's counter value

#tim = pyb.Timer(4, freq=1)      # create a timer object using timer 4 - trigger at 1Hz
#tim.callback(tick)        

from pyb import Timer

nISR = 0

from pyb import Pin
pin_B4 = Pin('B4', Pin.OUT_PP)
pin_A15 = Pin('A15', Pin.OUT_PP)
pin_A14 = Pin('A14', Pin.OUT_PP)
pin_A13 = Pin('A13', Pin.OUT_PP)
pin_A0 = Pin('A0', Pin.OUT_PP)

isr_state = 0 
isr_happened = 0

def tick(timer):                # we will receive the timer object when being called
    #print(timer.counter())      # show current timer's counter value
    #pyb.LED(2).toggle()
    global isr_happened, nISR
    isr_happened = 1
    nISR += 1
    

def mysat(vin):
    if vin > 255:
        return 255
    elif vin < -255:
        return -255
    else:
        return vin

tim = Timer(1, freq=1000)
tim.counter() # get counter value
tim.freq(400) # 0.5 Hz
tim.callback(tick) 

from ulab import numpy as np

# set up i2c
from machine import I2C
i2c = I2C('X', freq=400000)                 # create hardware I2c object
MOTOR_ADDRESS = 0x04
i2c.writeto(MOTOR_ADDRESS, b'\x01')

N = 1000
print("N = %i" % N)
#data = np.zeros((N,3),dtype=np.int16)
data = np.zeros((N,6),dtype=np.int16)
nISR = 0

u = np.zeros(N, dtype=np.int16)
# change me to PD control for a step response
u[10:] = 300

Kp = 2
enc = 0
t0 = time.ticks_us()

i2c_send_array = bytearray([3,0,0,0,0])
twos_comp_offset = 2**16

for i in range(N):
    #pin_A15.on()
    while (isr_happened == 0):
        # wait for next interrupt
        time.sleep_us(10)
    #pin_A15.off()

    # square wave that toggles each time step
    if isr_state == 1:
        isr_state = 0
        pin_B4.off()
    else:
        isr_state = 1
        pin_B4.on()

    pin_A15.on()
    pin_A14.on()
    # clear flag
    isr_happened = 0
    #print("%i, %i" % (nISR, tim.counter()))
    #print(nISR)

    # generate square wave for timing verification (oscilloscope)
    cur_resp = i2c.readfrom(MOTOR_ADDRESS, 6)
    enc = int(cur_resp[0]*256+cur_resp[1])
    n_echo = cur_resp[2]*256+cur_resp[3]
        
    e = int(u[i] - enc)
    v_i = int(Kp*e)
    v_i = mysat(v_i)
    if v_i < 0:
        v_i += twos_comp_offset
    #v_i = u[i]

    v_i = int(v_i)

    msb = int(v_i/256)
    lsb = v_i % 256
    i_msb = int(i/256)
    i_lsb  = i % 256
    pin_A14.off()

    pin_A13.on()
    i2c_send_array[1] = msb
    i2c_send_array[2] = lsb
    i2c_send_array[3] = i_msb
    i2c_send_array[4] = i_lsb
    i2c.writeto(MOTOR_ADDRESS, i2c_send_array)
    #time.sleep_us(50)
    #i2c_recv_list.append(cur_resp)

    #data[i,:] = [nISR, enc_i, v_out]
    #data[i,0] = cur_resp[0]
    #data[i,1] = cur_resp[1]
    #pin_A0.on()
    ## data[i,0] = enc
    ## data[i,1] = v_i
    ## data[i,2] = n_echo
    data[i,:] = cur_resp
    #pin_A0.off()
    pin_A13.off()
    pin_A15.off()

t1 = time.ticks_us()
loop_time = t1 - t0
print("loop_time = %s" % loop_time)

# weird stop approach
final_send_array = bytearray([3,0,0,0,0])
i2c.writeto(MOTOR_ADDRESS, final_send_array)


i2c.writeto(MOTOR_ADDRESS, b'\x02')


for row in data:
    #print("%i, %i, %i" % (row[0],row[1],row[2]))
    row_str = ""
    for i, elem in enumerate(row):
        if i > 0:
            row_str += ","
        row_str += str(elem)
    print(row_str)

