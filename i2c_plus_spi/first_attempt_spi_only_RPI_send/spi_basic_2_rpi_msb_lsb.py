#!/usr/bin/env python3

# mini-spi.py
# 2016-03-18
# Public Domain

import time

import pigpio # http://abyz.me.uk/rpi/pigpio/python.html

pi = pigpio.pi()

if not pi.connected:
    exit(0)

h = pi.spi_open(0, 500000)

stop = time.time() + 10.0

n = 0

while time.time() < stop:
    n += 1
    print("n = " + str(n))
	#msg = "This is message number {}\n".format(n)
    msb = int(n/256)
    lsb = int(n % 256)
    msg = [msb,lsb]
    pi.spi_xfer(h, msg)
    time.sleep(0.01)
    print(msg)
    
pi.spi_close(h)

pi.stop()
