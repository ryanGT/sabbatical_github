# WiringPi RPI Line Following Control

## High-Level Questions

- what will it take to make this work?
    - mostly rpi with real-time loop plus i2c with two Arduinos in the loop



## Detail Questions

- what are the addresses of each Arduino?
    - the pendulum reading Uno uses address 7
    - the Mega uses address 8
- how do I code up communicating with two different Arduinos as secondary devices?
    - I can start with just communicating with the mega, but I can't get too far without both Arduinos
