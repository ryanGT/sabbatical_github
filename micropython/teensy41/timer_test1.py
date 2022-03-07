from machine import Timer
from machine import Pin
tim = Timer(1, mode=Timer.PERIODIC, width=32)
tim_a = tim.channel(Timer.A | Timer.B, freq=1)   # 1 Hz frequency requires a 32 bit timer

led = Pin(13, mode=Pin.OUT) # enable GP16 as output to drive the LED

def tick(timer):                # we will receive the timer object when being called
    global led
    led.toggle()                # toggle the LED

tim_a.irq(handler=tick, trigger=Timer.TIMEOUT)         # create the interrupt
