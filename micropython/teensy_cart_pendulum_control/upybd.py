"""
This module implements the python block diagram real-time control
approach on a Teensy running micropython.  It is assume the ulab, the
micropython version of numpy, is available.

Assumed usage:

- on a laptop or raspberry pi, a block diagram model is developed and
  a real-time Python file is generated

- after that file is generated, it will be copied to /flash on the
  teensy along with this library file
  
- the real-time file will import this library and run a loop of code
  in real-time

- at the top of the real-time file, a timer function will be setup and
  an i2c connection will be estabilished

- each instance block will be created

- each block will have a section of secondary init code where inputs
  are estabilished and where data vectors (1d arrays) will be created

- each block will have code that is run in the loop at each time step

- after the test is over, data will be transmited back to the host
  computer or raspberry pi or something for graphing and analysis

- each block will need to support the following methods:
    - `find_output(self, i)`
        - this is the main output calculation function
    - `init_vectors(self, N=1000)`
        - this method creates the 1d array for storing the
          block's output data over the course of the test
    - `read_output(self, i)`
        - when doing the Arduino development work, it was
          helpful to have a means to always read the output
          without redoing any calculations
              - this was especially important for things like
                digital compensator blocks, where constantly
                recalculating potentially moves the block ahead
                one time step everytime the function is called
"""

from ulab import numpy as np
import time

max_signed = 2**15-1
two_16 = 2**16

def signed_int_to_two_bytes(myint):
    if myint > max_signed:
        raise ValueError("myint too large: %i" % myint)
    elif myint < -max_signed:
        raise ValueError("myint too small: %i" % myint)

    # Two's compliment
    if myint < 0:
        myint += two_16

    msb = int(myint/256)
    lsb = int(myint) % 256
    return msb, lsb


def create_zeros_int16(N):
    myarray = np.zeros(N, dtype=np.int16)
    return myarray


class block(object):
    def init_vectors(self, N=1000):
        # assuming that the default for most blocks will be to read
        # the inputs from their input_block1's and find their output
        self.output_vector = np.zeros(N, dtype=np.int16)


    def set_input_block1(self, block):
        self.input_block1 = block
        

    def find_output(self, i):
        """This is just making the loop counter act like a block"""
        self.output_vector[i] = i
        return self.output_vector[i] 


    def read_output(self, i):
        return self.output_vector[i] 



class i2c_sensor(block):
    """This is a helper class for plants who read from i2c and
    possibly have more than one sensor.  This class exists to allow
    whatever block(s) needs access to the sensor to be able to use
    output_vector and read_output.  The class will basically hold an
    output_vector that will have its values set in the plant's
    find_output method."""
    def find_output(self, i):
        raise NotImplmentedError()



class int_constant_block(block):
    """In order to save memory, a constan in micropython will not have
    an ouput vector."""
    def __init__(self, value=100):
        self.value = value



    def init_vectors(self, N=1000):
        """Do nothing; create no vectors"""
        pass


    def find_output(self, i):
        """There is nothing to do, we already know the output"""
        return self.value


    def read_output(self, i):
        return self.value
    
    
class pulse_input(block):
    def __init__(self, amp=100, on_ind=10, off_ind=200):
        self.amp = amp
        self.on_ind = on_ind
        self.off_ind = off_ind


    def find_output(self, i):
        if self.on_ind <= i < self.off_ind:
            out = self.amp
        else:
            out = 0
        self.output_vector[i] = out
        return out



class saturation_block(block):
    def __init__(self, mymax=255):
        self.mymax = mymax


    def find_output(self, i):
        raw_in = self.input_block1.read_output(i)
        if raw_in > self.mymax:
            cur_out = self.mymax
        elif raw_in < -self.mymax:
            cur_out = -self.mymax
        else:
            cur_out = raw_in
        self.output_vector[i] = cur_out
        return self.output_vector[i]
        

class block_with_two_inputs(block):
    def set_input_block2(self, block):
        self.input_block2 = block



class addition_block(block_with_two_inputs):
    def find_output(self, i):
        output_i = self.input_block1.read_output(i) + self.input_block2.read_output(i)
        self.output_vector[i] = output_i
        return self.output_vector[i]


class subtraction_block(block_with_two_inputs):
    def find_output(self, i):
        output_i = self.input_block1.read_output(i) - self.input_block2.read_output(i)
        self.output_vector[i] = output_i        
        return self.output_vector[i]


class summing_junction(subtraction_block):
    """The only real differences between an subtraction block and a
    summing_junction is that they look different on the block diagram.
    A summing junction generally has a feedback wire and an subtraction
    block has both inputs coming from the left.  So, since he
    micropython version of this libray doesn't worry about drawing the
    block diagram, there is no difference here."""
    pass


class plant(block):
    pass



## if (inArray[0] == 3){
##   // - process the data if it is there
##   // - probably need to send [3,0,0,0,0] to keep the motors stopped, just to be safe
##   n_msb = inArray[1];
##   n_lsb = inArray[2];
##   v1_msb = inArray[3];
##   v1_lsb = inArray[4];
##   v1 = reassemblebytes(v1_msb,v1_lsb);
##   v2_msb = inArray[5];
##   v2_lsb = inArray[6];
##   v2 = reassemblebytes(v2_msb,v2_lsb);
##   // load up outArray to acknowledge what we have received


class plant_with_two_i2c_inputs_and_two_i2c_sensors(plant, \
                                                    block_with_two_inputs):
    """Note: this may not be a truly general plant model.  It includes
    extra i2c data for my research purposes for now.  I may remove
    these later, or I may ask my students to ignore them.


    Other note: When I worked with the cart/pendulum in C, I cheated
    on the two output plant by just accessing the sensors directly.
    So, other blocks had the sensors as inputs as I printed the sensor
    output directly.  This allows the sensors to be treated as SISO
    blocks.

    sensor1 and sensor2 are sensor blocks whose output_vectors get set
    by the plant after data is read over i2c.  The sensor blocks are
    used so that whatever blocks have the sensors as inputs can use
    the read_output method correctly."""
    def __init__(self, sensor1, sensor2, i2c, send_address, \
                 read_address1, read_address2):
        self.sensor1 = sensor1
        self.sensor2 = sensor2
        self.i2c = i2c
        self.send_address = send_address
        self.read_address1 = read_address1
        self.read_address2 = read_address2
        self.read1_bytyes = 8
        
        
    def init_vectors(self, N=1000):
        """The plant does not have an output_vector.  Instead, the
        sensors each have their own output_vector."""
        self.sensor1.init_vectors(N)
        self.sensor2.init_vectors(N)
        self.send_array = bytearray([3,0,0,0,0,0,0])
        self.read_array1 = bytearray(self.read1_bytyes)
        self.n_echo = create_zeros_int16(N)
        self.dt_micros = create_zeros_int16(N)
        self.n_loop = create_zeros_int16(N)

        
    def _transmit(self):
        self.i2c.writeto(self.send_address, self.send_array)


    def _read(self):
        # what will the line reader do if we try to read too often?
        # - how do we find out?
        self.read_array1 = self.i2c.readfrom(self.read_address1, \
                                                 self.read1_bytyes)
        # add read_array2 here later


        
    def send_commands(self, i):
        in1 = self.input_block1.read_output(i)
        in2 = self.input_block2.read_output(i)
        # send in1 and in2 as two byte ints over i2c
        msb1, lsb1 = signed_int_to_two_bytes(in1)
        msb2, lsb2 = signed_int_to_two_bytes(in2)
        imsb, ilsb = signed_int_to_two_bytes(i)
        # transmit:
        # - 3 is the command to send voltages to the motors
        self.send_array[0] = 3
        self.send_array[1] = imsb
        self.send_array[2] = ilsb
        self.send_array[3] = msb1
        self.send_array[4] = lsb1
        self.send_array[5] = msb2
        self.send_array[6] = lsb2
        self._transmit()
        

    def find_output(self, i):
        """What does the plant need to do to find its outputs?"""
        self._read()
        self.process_data(i)
        


class cart_pendulum_upy(plant_with_two_i2c_inputs_and_two_i2c_sensors):
    def check_cal(self):
        self._read()
        return int(self.read_array1[0])


    def process_data(self, i):
        ## From the Arduino:
        ##
        ## outArray[0] = calibrated;
        ## outArray[1] = n_loop;
        ## pos_lsb = (byte)position;
        ## pos_msb = getsecondbyte(position);
        ## outArray[2] = pos_msb;
        ## outArray[3] = pos_lsb;

        ##   outArray[4] = n_msb;
        ##   outArray[5] = n_lsb;
        ##   dt_micro_lsb = (byte)dt_micro;
        ##   dt_micro_msb = getsecondbyte(dt_micro);
        ##   outArray[6] = dt_micro_msb;
        ##   outArray[7] = dt_micro_msb;
        self.n_loop[i] = self.read_array1[1]
        self.sensor1.output_vector[i] = 256*self.read_array1[2] + self.read_array1[3]# not worried about sign here
        self.n_echo[i] = 256*self.read_array1[4] + self.read_array1[5]
        self.dt_micros[i] = 256*self.read_array1[6] + self.read_array1[7]
        # process sensor2 data here next


    def send_byte_and_zeros(self, cmd_byte):
        self.send_array[0] = cmd_byte
        for i in range(1,7):
            self.send_array[i] = 0

        self._transmit()
        

    def send_cal_command(self):
        self.send_byte_and_zeros(4)


    def start_test(self):
        self.send_byte_and_zeros(1)


    def stop_test(self):
        self.send_byte_and_zeros(2)
        time.sleep_ms(100)
        self.send_byte_and_zeros(3)
        time.sleep_ms(100)
        self.send_byte_and_zeros(2)
