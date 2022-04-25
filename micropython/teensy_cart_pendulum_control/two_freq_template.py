
#from ulab import numpy as np

#def tick(timer):                # we will receive the timer object when being called
#    print(timer.counter())      # show current timer's counter value

#tim = pyb.Timer(4, freq=1)      # create a timer object using timer 4 - trigger at 1Hz
#tim.callback(tick)        

# 0 = pyboard, 1 = teensy41
nISR = 0

import time

from machine import Timer
from machine import Pin

sw_pin = Pin(40, mode=Pin.OUT)
p2 = Pin(33, mode=Pin.OUT)
p3 = Pin(34, mode=Pin.OUT)
p4 = Pin(35, mode=Pin.OUT)


isr_state = 0 
isr_happened = 0

def tick(timer):                # we will receive the timer object when being called
    #print(timer.counter())      # show current timer's counter value
    #pyb.LED(2).toggle()
    global sw_pin, isr_happened, nISR
    if sw_pin.value():
        sw_pin.off()
    else:
        sw_pin.on()

    isr_happened = 1
    nISR += 1
    

def mysat(vin):
    if vin > 255:
        return 255
    elif vin < -255:
        return -255
    else:
        return vin

# set up i2c
from machine import I2C

i2c = I2C(2, 400_000)

# - pend uno address
# - mega address
mega_address = 0x07
uno_address = 0x08

from ulab import numpy as np

import upybd as pybd


# I will need N1 and N2 for the two loop init code

# sysprecode

# blockinitcode


# make input connections here:
# blocksecondaryinitcode



i2c_send_array = bytearray([3,0,0,0,0])
twos_comp_offset = 2**16

# check line calibration status and calibrate if necessary
cal = G.check_cal()
print("cal: %i" % cal)

if cal == 0:
    # send calibration command over i2c
    G.send_cal_command()
    for i in range(20):
        time.sleep_ms(500)
        cal = G.check_cal()
        print("i = %i, cal = %i" % (i, cal))
        if cal == 1:
            break


#data = np.zeros((N,3),dtype=np.int16)
#data = np.zeros((N,6),dtype=np.int16)


Kp = 2
enc = 0

nISR = 0

myfreq = 250
#myfreq = 500
tim = Timer(1, mode=Timer.PERIODIC, callback=tick, freq=myfreq)


t0 = time.ticks_us()

# start test command here
G.start_test()

freq_ratio = 5


for i in range(N):
    #pin_A15.on()
    while (isr_happened == 0):
        # wait for next interrupt
        time.sleep_us(10)
    #pin_A15.off()

    # square wave that toggles each time step
    if isr_state == 1:
        isr_state = 0
        p2.off()
    else:
        isr_state = 1
        p2.on()

    p3.on()
    # clear flag
    isr_happened = 0

    # execute slower loop at freq_ratio intervals
    # - if fast loop is running at 500 Hz, slow loop executes at
    #   500/freq_ratio
    # - to achieve this, only do things when the remainder of i/freq_ratio is zeros
    remainder = i % freq_ratio
    j = int(i/freq_ratio)
    if remainder == 0:
        # execute slower loop
        # pythonloop2code

    # pythonloop1code

    p4.on()
    # pythonsecondaryloop1code

    
    p4.off()
    p3.off()



# system post loop code:

t1 = time.ticks_us()
loop_time = t1 - t0
print("loop_time = %s" % loop_time)

# weird stop approach

# stop test command here
G.stop_test()

tim.deinit()


# plottingcode

# printingcode

dn = G.n_echo[1:] - G.n_echo[0:-1]
print("dn max = %i" % np.max(dn))
print("dn[1:] min = %i" % np.min(dn[1:]))

## for i, ent in enumerate(dn):
##     if ent != 1:
##         print("bad dn: %i, %i" % (i, ent))

