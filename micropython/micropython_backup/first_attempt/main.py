import pyb, time

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


# set up i2c
from machine import I2C
i2c = I2C('X', freq=400000)                 # create hardware I2c object
MOTOR_ADDRESS = 0x04
i2c.writeto(MOTOR_ADDRESS, b'\x01')

# set up spi
from pyb import SPI
#spi = SPI(2, SPI.MASTER, baudrate=200000, polarity=1, phase=0)
spi = SPI(2, SPI.MASTER, baudrate=200000, polarity=0, phase=1)


kp = 3
kd = 0.1

prev_n = -1
prev_e = 0
N = 500
t0 = time.ticks_us()
i2c_recv_list = []

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


    # do control stuff
    # - read encoder over ISR
    # - do PD calcs
    # - send H-bridge speed command over SPI
    # !!!! Don't forget to level shift !!!!
    cur_resp = i2c.readfrom(MOTOR_ADDRESS, 6)
    #i2c_recv_list.append(cur_resp)
    enc_i = cur_resp[3] + cur_resp[2]*256
    if enc_i > 30000:
        enc_i -= 2**16

    # step input
    if i > 50:
        u = 100
    else:
        u = 0
    # send pulse input to motor control Arduino
    e_i = u - enc_i
    e_diff = e_i - prev_e
    v_out = kp*e_i +kd*e_diff
    v_out = mysat(v_out)
    if v_out < 0:
        v_send = 2**16+v_out
    else:
        v_send = v_out

    msb = int(v_send/256)
    lsb = int(v_send % 256)
    #senddata = [30,msb,lsb]
    #senddata = [17,81]
    spi_data = bytearray([msb, lsb, 10])
    spi.send(spi_data)

    prev_e = e_i
    #print("%i, %i, %i, %i, %i, %i" % (nISR, enc_i, e_i, v_out, msb, lsb))
    #i2c_recv_list.append([nISR, v_out, msb, lsb])

t1 = time.ticks_us()
loop_time = t1 - t0
print("loop_time = %s" % loop_time)

spi.send(bytearray([0,0,10]))

# need pin ISRs to cause Arduino to truly stop the motor
p_out.on()
p_out.off()
p_out.on()
p_out.off()

i2c.writeto(MOTOR_ADDRESS, b'\x02')
