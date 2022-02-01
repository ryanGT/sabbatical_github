# main.py -- put your code here!
print("Hello DKP.")

import pyb, time

led1 = pyb.LED(1)
led1.on()

from pyb import Timer, Pin
#from machine import Timer
#from machine import Pin

tim = Timer(1, freq=1000)
tim.counter() # get counter value
tim.freq(500) # 0.5 Hz
sw_pin = Pin('B4', Pin.OUT_PP)
nISR = 0

def tick(timer):                # we will receive the timer object when being called
    global sw_pin, nISR
    sw_pin.toggle()                # toggle the LED
    nISR += 1

#tim.callback(tick)
tim.callback(lambda t: sw_pin.toggle())

print("starting loop")

for i in range(10):
    print(nISR)
    time.sleep_ms(500)


print("after loop")
led1.off()
