#!/usr/bin/env python
import os, shutil
import argparse
parser = argparse.ArgumentParser()
#parser.add_argument('--example', nargs='?', const=1, type=int, default=3)
parser.add_argument('c_filename', type=str, \
                    help='name of C input file')

args = parser.parse_args()
in_name = args.c_filename
print(in_name)
fno, ext = os.path.splitext(in_name)
o_name = fno + '.o'

#g++ -o wiringpi_line_following_i2c_autogen1.o wiringpi_line_following_i2c_autogen1.c rpiblockdiagram/rpiblockdiagram.o -lwiringPi -li2c -lrt
cmd = "g++ -o %s %s rpiblockdiagram/rpiblockdiagram.o -lwiringPi -li2c -lrt" % (o_name, in_name)
print(cmd)
os.system(cmd)

