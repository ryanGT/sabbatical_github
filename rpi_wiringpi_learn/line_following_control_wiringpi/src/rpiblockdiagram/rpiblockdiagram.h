#ifndef rpiblockdiagram_h
#define rpiblockdiagram_h

#include <iostream>
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <i2c/smbus.h>
#include <unistd.h>


#define MAXLEN 10

int mysat_rtbd(int vin);

uint8_t getsecondbyte(int input);
 
void shift_array_rtbd(float new_in, float vect_in[], int len_vect);
  
class block{
 public:
  int output;
  int read_output();//reading the output of a block can be done
                           //as often as needed by subsequent blocks;
                           //read_output just returns the variable
                           //output, set in the find_output method
  // pure virtual function
  
  // every valid block class must have a find_output method, but some
  // have inputs and some do not
  // - punting for now and not requiring anything using a virtual funtion

  //virtual int find_output();//find_output should only be called
                            //once per time step, but must be
                            //called for each block in the
                            //system
};


class loop_count_block: public block{
public:
  loop_count_block();
  int find_output(int n);
};


class int_constant_block: public block{
public:
  int value;
  int_constant_block(int myvalue);
  int find_output();
};


class block_with_one_input: public block{
 public:
  block* input;
  void set_input_block1(block* new_input){
    input = new_input;
  }
};

class block_with_two_inputs: public block{
public:
  block* input1;
  block* input2;
  int value1, value2;
  void set_input_blocks(block* IN1, block* IN2){
    input1 = IN1;
    input2 = IN2;
  }
};


class step_input: public block{
 public:
  float on_time;
  float off_time;
  int amp;
  step_input(float switch_on_time, int Amp);

  int find_output(float t);
};

class pulse_input: public block{
public:
  float on_time;
  float off_time;
  int amp;
  pulse_input(float switch_on_time, float switch_off_time, int Amp);

  int find_output(float t);
};


class actuator{
 public:
  // pure virtual function
  virtual void send_command(int speed) = 0;
};


class double_actuator{
  //an actuator that has two inputs, such as an h-bridge with two motors
public:
  // pure virtual function
  virtual void send_commands(int speed1, int speed2) = 0;
};


class h_bridge_actuator: public actuator{
 public:
  int in1, in2, pwm_pin;
  h_bridge_actuator(int IN1_PIN, int IN2_PIN, int PWM_PIN);

  void setup();
  void send_command(int speed);
};


class pwm_output: public actuator{
public:
  int pwm_pin;
  pwm_output(int PWM_PIN);

  void setup();
  void send_command(int speed);
};


class sensor: public block{
  // - a sensor is a block with no input
  // - it will often be part of a plant
 public:
  // pure virtual function
  virtual int get_reading() = 0;//get_reading should probably set output to be safe

  int find_output(){
    output = get_reading();
    return(output);
  };
};



class encoder: public sensor{
 public:
  volatile bool _EncoderBSet;
  volatile long encoder_count = 0;
  int encoderPinB;

  encoder(int ENCODER_PIN_B);
  
  void encoderISR();
  int get_reading();
};


class analog_sensor: public sensor{
 public:
  int analog_pin;
  int output;

  analog_sensor(int ANALOG_pin);
  
  int get_reading();
};


class plant: public block_with_one_input{
 public:
  actuator* Actuator;
  sensor* Sensor;
  // a plant block should still have an input block pointer  
  plant(actuator *myact, sensor *mysense);

  int get_reading();
  void send_command();
  void send_command(int speed);
  //int read_output(float t);
  int find_output(float t);
};


class plant_no_actuator: public block_with_one_input{
  // used to model a plant that has a sensor, but no actuator
  // - for example, the flexible beam used in EGR 345 lab
  //   vibrates because of the motion of the DC motor and
  //   its output is measured with an accelerometer
  //     - as far as the Arduino is concerned, nothing needs to
  //       be done to cause the beam to vibrate
  //          - there is not explicit actuator
public:
  sensor* Sensor;
  // a plant block should still have an input block pointer  
  plant_no_actuator(sensor *mysense);

  int get_reading();
  void send_command();//keeping these for consitency
  void send_command(int speed);
  //int read_output(float t);
  int find_output(float t);
};


class plant_with_double_actuator: public block_with_two_inputs{
  //a plant that has a double actuator, such as a differential drive robot
public:
  double_actuator* dblActuator;
  sensor* Sensor;
  // a plant block should still have an input block pointer  
  plant_with_double_actuator(double_actuator *myact, sensor *mysense);

  int get_reading();
  void send_commands();
  //int read_output(float t);
  int find_output(float t);
  int find_output();  
};



class plant_with_double_actuator_two_sensors: public plant_with_double_actuator{
  //a plant that has a double actuator, such as a differential drive robot
public:
  double_actuator* dblActuator;
  sensor* Sensor1;
  sensor* Sensor2;
  int output1, output2;
  // a plant block should still have an input block pointer  
  plant_with_double_actuator_two_sensors(double_actuator *myact, sensor *mysense1, sensor *mysense2);
  //int get_reading();
  //void send_commands();
  //int read_output(float t);
  int find_output(float t);
  int find_output();  
};


class plant_with_i2c_double_actuator_and_two_sensors: public plant_with_double_actuator_two_sensors{
  //a plant that has a double actuator, such as a differential drive robot
public:
  sensor* Sensor1;
  sensor* Sensor2;
  int fd;//file descriptor #
  int output1, output2;
  // a plant block should still have an input block pointer  
  plant_with_i2c_double_actuator_and_two_sensors(int myfd, sensor *mysense1, sensor *mysense2);
  //int get_reading();
  //void send_commands();
  //int read_output(float t);
  void send_commands(int i);
  void stop_motors();
  void send_cal_cmd();  
  void set_fd(int myfd);
  //int find_output(float t);//<-- just inherit these
  //int find_output();//<-- just inherit these
};




class summing_junction: public block{
 public:
  block* input1;
  block* input2;
  int value1, value2;
  
  summing_junction(block *in1=NULL, block *in2=NULL);

  void set_inputs(block *IN1, block *IN2);
  //int read_output(float t);
  int find_output(float t);
};


class greater_than_block: public block_with_two_inputs{
public:
  greater_than_block(block *in1=NULL, block *in2=NULL);
  int find_output();
  int find_output(float t);
};

class addition_block: public greater_than_block{
public:
  //addition_block(block *in1=NULL, block *in2=NULL);
  int find_output();
  int find_output(float t);
};


class subtraction_block: public greater_than_block{
public:
  //subtraction_block(block *in1=NULL, block *in2=NULL);
  int find_output();
  int find_output(float t);
};



class if_block: public greater_than_block{
public:
  block *bool_block;
  int bool_value;
  if_block(block *bool_in=NULL, block *in1=NULL, block *in2=NULL);
  void set_inputs(block *BOOLIN, block *IN1, block *IN2);
  int find_output();
};


class P_control_block: public block_with_one_input{
 public:
  float Kp;
  //block* input;
  int input_value;
  //int output;
  
  P_control_block(float KP, block *in=NULL);

  //int read_output(float t);
  int find_output(float t);
};



class PD_control_block: public block_with_one_input{
 public:
  float Kp;
  float Kd;
  float prev_t, cur_t;
  int prev_in;
  float dt, din_dt;
  int din;
  //block* input;
  int input_value;
  //int output;
  
  PD_control_block(float KP, float KD, block *in=NULL);

  //int read_output(float t);
  int find_output(float t);
  void save_values(float t);
};


class digcomp_block: public block_with_one_input{
 public:
  //block* input;
  int _len_out;
  int _len_in;
  float *_b_vect;
  float *_a_vect;
  float _in_vect[MAXLEN];
  float _out_vect[MAXLEN];
  int input_value;
  //int output;
  digcomp_block(float *b_vect, float *a_vect, int len_in, int len_out, block *in=NULL);
  //digcomp_block(float *b_vect, float *a_vect, block *in);
  //float calc_out(float new_in);
  //int read_output(float t);
  int find_output(float t);
};
  

class saturation_block: public block_with_one_input{
 public:
  //block* input;
  int input_value;
  //int output;
  
  saturation_block(block *in=NULL);

  //int read_output(float t);
  int find_output(float t);
};


class sat2_adjustable_block: public saturation_block{
  //a class for a saturation block whose max and min values can be set
  //by the code.  I used to have functions called mysat2 that provided
  //this functionality (hence the name).
  //
  // if the minimum is not specified, it is set to -mymax
public:
  int input_value;
  int mymax, mymin;
  //int output;
  
  sat2_adjustable_block(int max_in, block *in=NULL);
  sat2_adjustable_block(int max_in, int min_in, block *in=NULL);

  //int read_output(float t);
  int find_output(float t);
};
  

#endif
