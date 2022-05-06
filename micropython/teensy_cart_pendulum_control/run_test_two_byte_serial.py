import subprocess, os
import numpy as np
import matplotlib.pyplot as plt

p = subprocess.run(['mpremote', 'run','main.py'], capture_output=True )
myout = p.stdout.decode()
print( 'exit status: %s' % p.returncode )
print( 'stdout: %s' % myout)
print( 'stderr: %s' % p.stderr.decode() )

#outname = "mpremote_loop_logging.csv"
#cmd = 'mpremote fs cp ":/sdcard/line_test_01.txt" "%s"' % outname
#os.system(cmd)




