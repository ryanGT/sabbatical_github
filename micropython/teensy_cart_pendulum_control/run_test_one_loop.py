from subprocess import run
import numpy as np
import matplotlib.pyplot as plt

p = run(['mpremote', 'run','main.py'], capture_output=True )
myout = p.stdout.decode()
print( 'exit status: %s' % p.returncode )
print( 'stdout: %s' % myout)
print( 'stderr: %s' % p.stderr.decode() )

raw_list = myout.split('\r\n')

pats = ['#begin test', \
        '#end test', \
        ]

#mylist.index("loop_num: 1")
#mylist.index("loop_num: 2")
#mylist.index("dn max = 1")

inds = []

for pat in pats:
    ind = raw_list.index(pat)
    inds.append(ind)

chunk1 = raw_list[inds[0]+1:inds[1]]

def chunk_to_array(chunk):
    nested_list = [row.split(",") for row in chunk]
    str_array = np.array(nested_list)
    float_array = str_array.astype(np.float64)
    return float_array

farray1 = chunk_to_array(chunk1)

#print_blocks = [satP, satN, line_sense, pend_enc]
#print_blocks = [sum_junct_line, D_line, sat]

legend1 = ["sum_junct_line", "D_line", "sat", "satP", "satN", "line_sense", "pend_enc"]

i = farray1[:,0]

plt.figure(1)
plt.clf()
plt.plot(i, farray1[:,1:])
plt.legend(legend1)


plt.show()





