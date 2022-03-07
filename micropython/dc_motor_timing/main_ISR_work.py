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
    global isr_happened, nISR, isr_state
    isr_happened = 1
    nISR += 1

    if isr_state == 1:
        isr_state = 0
        pin_B4.off()
    else:
        isr_state = 1
        pin_B4.on()


    # how do I execute code here for N loops?
    if enabled and (0 <= nISR < N):
        cur_resp = i2c.readfrom(MOTOR_ADDRESS, 6)
        enc = int(cur_resp[0]*256+cur_resp[1])
        n_echo = cur_resp[2]*256+cur_resp[3]
        
        e = int(u[nISR] - enc)
        v_i = int(Kp*e)
        v_i = mysat(v_i)
        if v_i < 0:
            v_i += twos_comp_offset
        #v_i = u[i]

        v_i = int(v_i)

        msb = int(v_i/256)
        lsb = v_i % 256
        i_msb = int(nISR/256)
        i_lsb  = nISR % 256
        pin_A14.off()

        pin_A13.on()
        i2c_send_array[1] = msb
        i2c_send_array[2] = lsb
        i2c_send_array[3] = i_msb
        i2c_send_array[4] = i_lsb
        i2c.writeto(MOTOR_ADDRESS, i2c_send_array)

        data[nISR,:] = cur_resp

    

def mysat(vin):
    if vin > 255:
        return 255
    elif vin < -255:
        return -255
    else:
        return vin

tim = Timer(1, freq=1000)
tim.counter() # get counter value
tim.freq(500) # 0.5 Hz
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


u = np.zeros(N, dtype=np.int16)
# change me to PD control for a step response
u[10:] = 300

Kp = 2
enc = 0


i2c_send_array = bytearray([3,0,0,0,0])
twos_comp_offset = 2**16


# how do I allow the timer callback function to run 1000 times from here?

nISR = 0
enabled = False
t0 = time.ticks_us()
for i in range(N):
    if i > 0:
        enabled = True
    #pin_A15.on()
    while (isr_happened == 0):
        # wait for next interrupt
        time.sleep_us(50)
    #pin_A15.off()

    # reset the flag
    isr_happened = 0
    
enabled = False

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

