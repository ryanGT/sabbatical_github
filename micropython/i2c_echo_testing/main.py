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
#i2c.writeto(MOTOR_ADDRESS, b'\x01')

N = 500
print("N = %i" % N)
data = np.zeros((N,3),dtype=np.int16)
nISR = 0

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


    msb = int(i/256)
    lsb = i % 256

    i2c.writeto(MOTOR_ADDRESS, bytearray([msb,lsb])) 
    time.sleep_us(100)
    cur_resp = i2c.readfrom(MOTOR_ADDRESS, 3)
    #i2c_recv_list.append(cur_resp)

    #data[i,:] = [nISR, enc_i, v_out]
    data[i,:] = cur_resp

t1 = time.ticks_us()
loop_time = t1 - t0
print("loop_time = %s" % loop_time)

# need pin ISRs to cause Arduino to truly stop the motor
p_out.on()
p_out.off()
p_out.on()
p_out.off()

#i2c.writeto(MOTOR_ADDRESS, b'\x02')


for row in data:
    print("%i, %i, %i" % (row[0],row[1],row[2]))

