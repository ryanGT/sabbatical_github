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
    
    
tim = Timer(1, freq=5000)
tim.counter() # get counter value
tim.freq(500) # 0.5 Hz
tim.callback(tick) 

prev_n = -1
N = 1000
t0 = time.ticks_us()
for i in range(N):
    while (isr_happened == 0):
        # wait for next interrupt
        time.sleep_us(10)
    # clear flag
    isr_happened = 0
    #print("%i, %i" % (nISR, tim.counter()))
    print(nISR)

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

t1 = time.ticks_us()
loop_time = t1 - t0
print("loop_time = %s" % loop_time)
