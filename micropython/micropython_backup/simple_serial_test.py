import pyb, time

#def tick(timer):                # we will receive the timer object when being called
#    print(timer.counter())      # show current timer's counter value

#tim = pyb.Timer(4, freq=1)      # create a timer object using timer 4 - trigger at 1Hz
#tim.callback(tick)        

t0  = time.time()
print("hello world")
time.sleep(0.5)
t1 = time.time()
dt = t1-t0
print("dt = %0.4g" % dt)
print("goodbye Ryan, you are a decent fellow")

