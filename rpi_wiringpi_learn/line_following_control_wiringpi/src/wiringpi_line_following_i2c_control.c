#include <iostream>
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <i2c/smbus.h>
#include <unistd.h>
#include "rpiblockdiagram/rpiblockdiagram.h"


#define MEGA_ID 0x07
#define UNO_ID 0x08

uint32_t t0 = micros();
uint32_t t, t1, t2, t3, prev_t;
uint16_t dt, dt_send, dt_receive;
uint32_t send_total=0;
float ave_send;
const int N=1000;
int i_echo[N];
int two_byte_response[N];
int enc_fd, mega_fd;
int position;
#define in_bytes 8
#define out_bytes 8
uint8_t inArray[in_bytes];
uint8_t outArray[out_bytes];
#define enc_bytes 2
uint8_t enc_array[enc_bytes];

uint8_t ilsb, imsb;
uint8_t calibrated;

// compile cmd (old):
// compile cmd (old):
// g++ -o wiringpi_multi_byte_attempt1.o wiringpi_multi_byte_attempt1.c -lwiringPi -li2c

// performance cpu comand:
// echo performance | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

// compiling and linking command with rpi library:
//g++ -o wiringpi_line_following_i2c_control.o wiringpi_line_following_i2c_control.c rpiblockdiagram/rpiblockdiagram.o -lwiringPi -li2c


//uint8_t getsecondbyte(int input){
//  uint8_t output;
//  output = (uint8_t)(input >> 8);
//  return output;
//}
//

int reassemblebytes(uint8_t msb, uint8_t lsb){
  int output;
  output = (int)(msb << 8);
  output += lsb;
  return output;
}

// it feels like the file descriptors need to get assigned
// when main runs; this means that these i2c functions need
// an fd int that isn't constant and doesn't exist until main
// runs
//
// - or can they be global ints that default to zero and then get 
//   set inside main before they are used?
//   - is that better? 

int read_encoder_i2c(){
  int out;

  read(enc_fd, enc_array, enc_bytes);
  out = reassemblebytes(enc_array[0],enc_array[1]);
  return(out);
}

class pendulum_encoder: public sensor{
  // a valid sensor class must have a get_reading method with no
  // inputs that returns an int (the sensor reading)
 public:
  int output;

  pendulum_encoder(){};

  int get_reading(){
    // this will cause the value to be re-read over i2c whenever it is
    // needed.....
    output = read_encoder_i2c();
    return(output);
  };
};


// mega i2c
// - addr is 0x07
// - byte 0 is always calibrated variable:
//    outArray[0] = calibrated;
//    outArray[1] = n_loop;
//    pos_lsb = (byte)position;
//    pos_msb = getsecondbyte(position);
//    outArray[2] = pos_msb;
//    outArray[3] = pos_lsb;
//    outArray[4] = n_msb;
//    outArray[5] = n_lsb;
//    dt_micro_lsb = (byte)dt_micro;
//    dt_micro_msb = getsecondbyte(dt_micro);
//    outArray[6] = dt_micro_msb;
//    outArray[7] = dt_micro_msb;
// # Approach:
//   - I need a buffer of 8 bytes
//   - a function that reads the sensor value should read to fill the buffer
//     and then use bytes 2 and 3
//   - a check_cal function should read the buffer and return byte 0

#define line_bytes 8
uint8_t line_sensor_buf[line_bytes];
int line_sense_addr=7;

void read_line_sensor_i2c_buf(){

  read(mega_fd, line_sensor_buf, line_bytes);
}



int read_line_position(){
  read_line_sensor_i2c_buf();
  position = line_sensor_buf[2]*256 + line_sensor_buf[1];
  return(position);
}


class line_sense_i2c: public sensor{
  // a valid sensor class must have a get_reading method with no
  // inputs that returns an int (the sensor reading)
 public:
  int output;

  line_sense_i2c(){};

  int get_reading(){
    // this will cause the value to be re-read over i2c whenever it is
    // needed.....
    output = read_line_position();
    return(output);
  };
};

//bdsysinitcode
line_sense_i2c line_sense = line_sense_i2c();
pendulum_encoder pend_enc = pendulum_encoder();
// note: in rpi wiringPi land, the first int input needs to be the file descriptor, 
// which is not know yet
// - it should be set to mega_fd later on in the main function (after it is opened)
plant_with_i2c_double_actuator_and_two_sensors G_cart = plant_with_i2c_double_actuator_and_two_sensors(7, &line_sense, &pend_enc);
addition_block add = addition_block();
subtraction_block subtract = subtraction_block();
pulse_input U_forward_pulse = pulse_input(0.1, 0.5, 200);
pulse_input U_turn = pulse_input(0.1, 0.5, 150);



uint8_t check_cal(){
  read_line_sensor_i2c_buf();
  return line_sensor_buf[0];
}


void send_cal_command(){
  printf("sending cal command\n");
  G_cart.send_cal_cmd();
  delay(2000);
  for (int k=0; k<20; k++){
    delay(500);
    calibrated = check_cal();
    printf("k = %i, calibrated = %i\n", k, calibrated);
    if (calibrated == 1){
      break;
    }
  }
}


//uint32_t t1, t2, dt;

int main (int argc, char **argv)
{
  printf("at top of main\n");
  // Setup I2C communication
    mega_fd = wiringPiI2CSetup(MEGA_ID);
    if (mega_fd == -1) {
        std::cout << "Mega failed to init I2C communication.\n";
        return -1;
    }
    std::cout << "Mega I2C communication successfully setup.\n";
    G_cart.set_fd(mega_fd);

    enc_fd = wiringPiI2CSetup(UNO_ID);
    if (enc_fd == -1) {
        std::cout << "Encoder Uno failed to init I2C communication.\n";
        return -1;
    }
    std::cout << "Encoder Uno I2C communication successfully setup.\n";


    //FILE * fp;

    //fp = fopen ("data.txt", "w");
    //fprintf(fp, "%s %s %s %d", "We", "are", "in", 2012);

    wiringPiSetup();
    pinMode(0, OUTPUT);
    pinMode(1, OUTPUT);
    pinMode(3, OUTPUT);
    printf("sending data\n");


  //bdsyssetupcode
   printf("doing block setup\n");
   G_cart.set_input_blocks(&add, &subtract);
   add.set_input_blocks(&U_forward_pulse, &U_turn);
   subtract.set_input_blocks(&U_forward_pulse, &U_turn);


  //menu
  calibrated = check_cal();
  printf("in menu, calibrated = %i\n", calibrated);

  char mychar;
  	
  if (calibrated == 0){
    printf("press any character to calibrate\n");

    mychar = getchar();
    printf("you pressed: %c", mychar);
    send_cal_command();
  };
  /*   // reset encoders and t0 at the start of a test */

  printf("done with menu and/or calibration\n");

  return 0;
}
