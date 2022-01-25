#
#   Weather update client
#   Connects SUB socket to tcp://localhost:5556
#   Collects weather updates and finds avg temp in zipcode
#

import sys
import zmq
import time
import numpy as np

#  Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

print("Collecting updates from weather server...")
socket.connect("tcp://localhost:5556")

# Subscribe to zipcode, default is NYC, 10001
#zip_filter = sys.argv[1] if len(sys.argv) > 1 else "10001"
#socket.setsockopt_string(zmq.SUBSCRIBE, zip_filter)
socket.setsockopt_string(zmq.SUBSCRIBE,"")

# Process 5 updates
total_temp = 0
t0 = time.time()
N = 1000
n_check = np.zeros(N)
for i in range(N):
    string = socket.recv_string()
    print(string)
    n_check[i] = int(string)
    
t1 = time.time()
loop_time = t1-t0
print("loop time = %0.6g" % loop_time)
dt = loop_time/N
print("dt = %0.6g" % dt)
dn = n_check[-1]-n_check[0]
if dn < 0:
    dn += 2**16
print("dn = %i" % dn)
