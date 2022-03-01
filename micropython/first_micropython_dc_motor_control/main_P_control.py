import pyb, time
#from ulab import numpy as np

#def tick(timer):                # we will receive the timer object when being called
#    print(timer.counter())      # show current timer's counter value

#tim = pyb.Timer(4, freq=1)      # create a timer object using timer 4 - trigger at 1Hz
#tim.callback(tick)        

from pyb import Timer

nISR = 0

from pyb import Pin
p_out = Pin('B4', Pin.OUT_PP)
isr_state = 0 
isr_happened = 0

def tick(timer):                # we will receive the timer object when being called
    #print(timer.counter())      # show current timer's counter value
    #pyb.LED(2).toggle()
    global isr_state, p_out, isr_happened
    isr_happened = 1
    global nISR
    nISR += 1
    

def mysat(vin):
    if vin > 255:
        return 255
    elif vin < -255:
        return -255
    else:
        return vin

tim = Timer(1, freq=5000)
tim.counter() # get counter value
tim.freq(500) # 0.5 Hz
tim.callback(tick) 

from ulab import numpy as np

# set up i2c
from machine import I2C
i2c = I2C('X', freq=400000)                 # create hardware I2c object
MOTOR_ADDRESS = 0x04
i2c.writeto(MOTOR_ADDRESS, b'\x01')

N = 500
print("N = %i" % N)
data = np.zeros((N,3),dtype=np.int16)
nISR = 0

u = np.zeros(N, dtype=np.int16)
# change me to PD control for a step response
u[10:] = 200

Kp = 2
enc = 0
t0 = time.ticks_us()

for i in range(N):
    while (isr_happened == 0):
        # wait for next interrupt
        time.sleep_us(10)
    # clear flag
    isr_happened = 0
    #print("%i, %i" % (nISR, tim.counter()))
    #print(nISR)

    # generate square wave for timing verification (oscilloscope)
    if isr_state == 1:
        isr_state = 0
        p_out.off()
    else:
        isr_state = 1
        p_out.on()

    e = u[i] - enc
    v_i = int(Kp*e)
    v_i = mysat(v_i)
    if v_i < 0:
        v_i += 2**16
    #v_i = u[i]
    
    msb = int(v_i/256)
    lsb = v_i % 256

    i2c.writeto(MOTOR_ADDRESS, bytearray([3,msb,lsb])) 
    time.sleep_us(100)
    cur_resp = i2c.readfrom(MOTOR_ADDRESS, 3)
    enc = cur_resp[0]*256+cur_resp[1]
    #i2c_recv_list.append(cur_resp)

    #data[i,:] = [nISR, enc_i, v_out]
    #data[i,0] = cur_resp[0]
    #data[i,1] = cur_resp[1]
    data[i,0] = enc
    data[i,1] = e
    data[i,2] = v_i

t1 = time.ticks_us()
loop_time = t1 - t0
print("loop_time = %s" % loop_time)


i2c.writeto(MOTOR_ADDRESS, b'\x02')


for row in data:
    print("%i, %i, %i" % (row[0],row[1],row[2]))

