from subprocess import run
import numpy as np
import matplotlib.pyplot as plt

p = run(['mpremote', 'run','main.py'], capture_output=True )
myout = p.stdout.decode()
print( 'exit status: %s' % p.returncode )
print( 'stdout: %s' % myout)
print( 'stderr: %s' % p.stderr.decode() )

raw_list = myout.split('\r\n')

pats = ['loop_num: 1', \
        'loop_num: 2', \
        'dn max = 1', \
        ]

#mylist.index("loop_num: 1")
#mylist.index("loop_num: 2")
#mylist.index("dn max = 1")

inds = []

for pat in pats:
    ind = raw_list.index(pat)
    inds.append(ind)

chunk1 = raw_list[inds[0]+1:inds[1]]
chunk2 = raw_list[inds[1]+1:inds[2]]

def chunk_to_array(chunk):
    nested_list = [row.split(",") for row in chunk]
    str_array = np.array(nested_list)
    float_array = str_array.astype(np.float64)
    return float_array

farray1 = chunk_to_array(chunk1)
farray2 = chunk_to_array(chunk2)

#print_blocks = [satP, satN, line_sense, pend_enc]
#print_blocks = [sum_junct_line, D_line, sat]

legend1 = ["satP", "satN", "line_sense", "pend_enc"]
ratio = int(len(farray1)/len(farray2))

i = farray1[:,0]
j = farray2[:,0]
fake_j = j*ratio


plt.figure(1)
plt.clf()
plt.plot(i, farray1[:,1:])
plt.legend(legend1)


legend2 = ["sum_junct_line", "D_line", "sat"]
plt.figure(2)
plt.clf()
plt.plot(fake_j, farray2[:,1:])
plt.legend(legend2)

plt.show()





