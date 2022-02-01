#import smbus
import pigpio
import time
import numpy as np
import copy
import matplotlib.pyplot as plt
plt.close('all')

import serial_utils

import control
from control import TransferFunction as TF

import sys
import time


import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
LED = 17
ledState = False
GPIO.setup(LED,GPIO.OUT)

ledState = 0

N = 500

check_array = np.zeros(1000)
j = 0
n = 0
num_checks = np.zeros(N)
prev_check = 0
num_read = np.zeros(N)
v_sent = np.zeros(N)
enc_vect = np.zeros(N)
error_vect = np.zeros(N)
u_vect = np.zeros(N)
u_vect[10:] = 300
read_bytes = 6
responses = np.zeros((N,read_bytes))


t0 = time.time()

for i in range(N):
    ledState = not ledState
    GPIO.output(LED, ledState)
    time.sleep(0.002)


t1 = time.time()
loop_time = t1-t0
print("loop_time = %f" % loop_time)


# In[169]:


ave_time_step = loop_time/N*1000

print("ave_time_step = %0.4g" % ave_time_step)
# In[170]:

