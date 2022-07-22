# Sabbatical Notes



## Teensyduino Cart/Pendulum Work

- main teensyduino folder:
    - [cart_pendulum/arduino_only/cart_pendulum_teensy_manual_edit](cart_pendulum/arduino_only/cart_pendulum_teensy_manual_edit)
- Mega code for i2c usage: 
    - [micropython/teensy_cart_pendulum_control/cart_mega_code_i2c](micropython/teensy_cart_pendulum_control/cart_mega_code_i2c)
- Pendulum reader code:
    - [micropython/teensy_cart_pendulum_control/pendulum_reader_i2c_minion](micropython/teensy_cart_pendulum_control/pendulum_reader_i2c_minion)
	
### Summary

- seems to work ok at 500 Hz
    - working on final verification of that


### Notes

- streaming the data over serial does not block the teensy for the entire transmission time
    - it puts the data in the serial buffer and only blocks if the buffer is full
	- so, as long as the data can stream in less than 2ms, the buffer shouldn't fill up
- there would still be benefit in converting from ascii test to two byte ints
    - is this a higher priority for me than Raspberry Pi real-time C
      execution to elimintate the teensy?
	
	


## Raspberry Pi C work

### Overview

- working on getting i2c working in C on the Raspberry Pi
- if this works, the RPi would control the timing and be the main
  device for control calculations and data logging
    - since the data would already be on the RPi, this eliminates the
      need to stream the data back to the RPi
	    - the RPi has plenty of RAM and would log the data to a csv file on the SD card
- using pigpio for now
    - some debate about pigpio vs. wiringpi
    - pigpio worked well in python
	- wiringpi is sort of not officially supported anymore
	- wiringpi does not seem to support block i2c writing
	
### pigpio i2c issues

- documentation does not seem to be great
- basically using my working python code as a roadmap:
    - use [i2cOpen](https://abyz.me.uk/rpi/pigpio/cif.html#i2cOpen) to open the connection
	    - which bus am I using on the RPi?
		- what addr is the mega i2c code listening on?
		    - `0x07`
		- what addr is the pendulum reader listening on?
	- will also need [i2cWriteByte](https://abyz.me.uk/rpi/pigpio/cif.html#i2cWriteByte)
	- will probably also need [i2cReadDevice](https://abyz.me.uk/rpi/pigpio/cif.html#i2cReadDevice) and [i2cWriteDevice](https://abyz.me.uk/rpi/pigpio/cif.html#i2cWriteDevice)
	- and finally [i2cClose](https://abyz.me.uk/rpi/pigpio/cif.html#i2cClose)
	- how do I set the baudrate?
	    - I believe this is handle as an RPi config option in `/boot/config.txt` or something
		
		
### code for pigpio i2c learn

- RPi code: [rpi_C_pigpio/i2c_learn/c_square_wave_pigpio_i2c_learn.c](rpi_C_pigpio/i2c_learn/c_square_wave_pigpio_i2c_learn.c)
- Mega code: [rpi_C_pigpio/i2c_learn/cart_mega_code_i2c_learn/cart_mega_code_i2c_learn.ino](rpi_C_pigpio/i2c_learn/cart_mega_code_i2c_learn/cart_mega_code_i2c_learn.ino)




## Working on i2c baudrate

### Clock check command:

`sudo cat /sys/kernel/debug/clk/clk_summary`

### Proof of concept articls



[https://raspberrypi.stackexchange.com/questions/108896/what-is-rpis-i2c-maximum-speed](https://raspberrypi.stackexchange.com/questions/108896/what-is-rpis-i2c-maximum-speed)



## Teensy Cart Pendulum Control

- getting close with autogen of open-loop
- do I care about the order of printing?
- does the teensy work with my tk serial gui?
    - and can I generate a plot order or label txt file or something so that we
      can auto-plot with labels?
