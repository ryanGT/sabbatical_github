
#from ulab import numpy as np

#def tick(timer):                # we will receive the timer object when being called
#    print(timer.counter())      # show current timer's counter value

#tim = pyb.Timer(4, freq=1)      # create a timer object using timer 4 - trigger at 1Hz
#tim.callback(tick)

# 0 = pyboard, 1 = teensy41
nISR = 0
N = 1000#<-- probably longer
print("N = %i" % N)

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

# sysprecode
N = 1000
num_read = np.zeros(N)
prev_check = -1


# blockinitcode
line_sense = pybd.i2c_sensor()
encoder = pybd.i2c_sensor()
U_line_center = pybd.int_constant_block(value=3500)
sum1_block = pybd.summing_junction()
P_block = pybd.P_controller(Kp=0.1)
sat_block = pybd.saturation_block(mymax=200)
G = pybd.cart_pendulum_upy(sensor1=line_sense, sensor2=encoder, send_address=7, read_address1=7, read_address2=8 ,i2c=i2c)
v_nom_block = pybd.int_constant_block(value=200)
add_block1 = pybd.addition_block()
subtract_block1 = pybd.subtraction_block()
satP = pybd.saturation_block(mymax=400)
satN = pybd.saturation_block(mymax=400)



# make input connections here:
# blocksecondaryinitcode
U_line_center.init_vectors(N)
sum1_block.input_block1 = U_line_center
sum1_block.input_block2 = line_sense
sum1_block.init_vectors(N)
P_block.set_input_block1(sum1_block)
P_block.init_vectors(N)
sat_block.set_input_block1(P_block)
sat_block.init_vectors(N)
G.set_input_block1(satP)
G.set_input_block2(satN)
G.init_vectors(N)
v_nom_block.init_vectors(N)
add_block1.set_input_block1(v_nom_block)
add_block1.set_input_block2(sat_block)
add_block1.init_vectors(N)
subtract_block1.set_input_block1(v_nom_block)
subtract_block1.set_input_block2(sat_block)
subtract_block1.init_vectors(N)
satP.set_input_block1(add_block1)
satP.init_vectors(N)
satN.set_input_block1(subtract_block1)
satN.init_vectors(N)




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

tim = Timer(1, mode=Timer.PERIODIC, callback=tick, freq=500)


t0 = time.ticks_us()

# start test command here
G.start_test()


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

    # pythonloopcode
    G.find_output(i)
    U_line_center.find_output(i)
    sum1_block.find_output(i)
    P_block.find_output(i)
    sat_block.find_output(i)
    v_nom_block.find_output(i)
    add_block1.find_output(i)
    subtract_block1.find_output(i)
    satP.find_output(i)
    satN.find_output(i)


    p4.on()
    # pythonsecondaryloopcode
    G.send_commands(i)



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
print_blocks = [U_line_center, P_block, sat_block, satP, satN, line_sense]
for i in range(N):
    rowstr = str(i)
    for block in print_blocks:
        if rowstr:
            rowstr += ', '
        rowstr += str(block.output_vector[i])
    print(rowstr)


## for row in data:
##     #print("%i, %i, %i" % (row[0],row[1],row[2]))
##     row_str = ""
##     for i, elem in enumerate(row):
##         if i > 0:
##             row_str += ","
##         row_str += str(elem)
##     print(row_str)


## n_echo = data[:,2]*256 + data[:,3]
## dn = n_echo[1:] - n_echo[0:-1]
## print("dn max = %i" % np.max(dn))

## for i, ent in enumerate(dn):
##     if ent != 1:
##         print("bad dn: %i, %i" % (i, ent))

