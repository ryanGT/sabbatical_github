#include <kraussserial.h>
#include <rtblockdiagram.h>
#include <math.h>
#include <Wire.h>


IntervalTimer myTimer;

volatile long encoder_count = 0;

volatile int v_left, v_right;

int test_case;

int state;
int ISR_state;
int squarewave_pin = 40;
int serial_pin = 33;
int loop_pin = 34;
int loop_pin2 = 35;
int loop_pin3 = 36;
int loop_pin4 = 37;
int loop_pin5 = 38;

int position;

bool send_ser = false;
int calibrated = 0;
int n, nIn;
int nISR=30000;
int amp;
float m=0.1;
int width;
int n_start = 10;
int v;
int stop_n = 200;// hard code this if you want to be lame

unsigned long t0;
unsigned long t;
unsigned long t1;
unsigned long cur_t;
float t_ms, t_sec, prev_t, dt;
float t_stop = 5;

int dt_micro;
int mydelay;
unsigned long prevt;
float dt_ms;
float dt_sec;
float t_ms_prev;

int tempbyte;
int inByte;
int ISR_Happened;


int read_encoder_i2c(){
  int out;

  Wire2.requestFrom(8, 2);    // request 2 bytes from slave device #8
  unsigned char lsb, msb;
  while (Wire2.available()<2){
    delayMicroseconds(5);
  }
  msb = Wire2.read();
  lsb = Wire2.read();
  out = reassemblebytes(msb,lsb);
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
byte line_sensor_buf[line_bytes];
int line_sense_addr=7;

void read_line_sensor_i2c_buf(){
  Wire2.requestFrom(line_sense_addr, line_bytes);    // request 2 bytes from slave device #8
  while (Wire2.available()<line_bytes){
    delayMicroseconds(5);
  }
  for (int k=0; k<line_bytes; k++){
    line_sensor_buf[k] = Wire2.read();
  }
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
plant_with_i2c_double_actuator_and_two_sensors G_cart = plant_with_i2c_double_actuator_and_two_sensors(7, &line_sense, &pend_enc);
addition_block add = addition_block();
subtraction_block subtract = subtraction_block();
int_constant_block U_line = int_constant_block(3500);
summing_junction sum_junct = summing_junction();
P_control_block D = P_control_block(0.01);
saturation_block sat = saturation_block();
step_input U_forward_step = step_input(0.1, 200);



byte check_cal(){
  read_line_sensor_i2c_buf();
  return line_sensor_buf[0];
}


void send_cal_command(){
  Serial.println("sending cal command");
  G_cart.send_cal_cmd();
  delay(2000);
  for (int k=0; k<20; k++){
    delay(500);
    calibrated = check_cal();
    Serial.print("k = ");
    Serial.print(k);
    Serial.print(", calibrated = ");
    Serial.println(calibrated);
    if (calibrated == 1){
      break;
    }
  }
}


void menu(){
  digitalWrite(serial_pin, LOW);
  Serial.println("top of menu");
  char mychar;
  calibrated = check_cal();
  Serial.print("in menu, calibrated = ");
  Serial.println(calibrated);

  if (calibrated == 0){
    Serial.println("enter any character to calibrate");
    mychar = get_char();
    send_cal_command();
  };
  /*   // reset encoders and t0 at the start of a test */
  /*   //enc.encoder_count = 0; */
  /*   //bdsysmenucode */

  //  PD_block.Kp = get_float_with_message_no_pointer("PD_block.Kp");
  //  PD_block.Kd = get_float_with_message_no_pointer("PD_block.Kd");
  //  v_nom_block.value = get_int_with_message_no_pointer("v_nom_block.value");
  t_stop = get_float_with_message_no_pointer("t_stop");

  Serial.println("enter any character to start a test");
  mychar = get_char();
  myTimer.begin(timerISR, 2000);
  digitalWrite(serial_pin, HIGH);
  t0 = micros();
  nISR = 0;
  ISR_Happened = 0;// clear flag and wait for next time step
  Serial.print("t0 =");
  Serial.println(t0);
}

void setup()
{
  Wire2.begin();        // join i2c bus (address optional for master)
  Wire2.setClock(400000);
  //Serial.begin(115200);
  Serial.begin(230400);
  while(!Serial){
     delay(5);
  }

  //bdsyswelcomecode
   Serial.println("auto-generated Arduino code");



  Serial.println("using rtblockdiagram library");
  pinMode(squarewave_pin, OUTPUT);
  pinMode(serial_pin, OUTPUT);
  pinMode(loop_pin, OUTPUT);
  pinMode(loop_pin2, OUTPUT);
  pinMode(loop_pin3, OUTPUT);
  pinMode(loop_pin4, OUTPUT);
  pinMode(loop_pin5, OUTPUT);

  //!// encoder pin on interrupt 0 (pin 2)

  //bdsyssetupcode
   G_cart.set_input_blocks(&add, &subtract);
   add.set_input_blocks(&U_forward_step, &sat);
   subtract.set_input_blocks(&U_forward_step, &sat);
   sum_junct.set_inputs(&U_line, &line_sense);
   D.set_input_block1(&sum_junct);
   sat.set_input_block1(&D);



  //Serial.print("pendulum/cart v. 1.1.0 RT Serial");
  //Serial.print("\n");
  //myTimer.begin(timerISR, 2000);
  pinMode(squarewave_pin, OUTPUT);

  calibrated = 0;

  /* delay(500); */

  /* Serial.println("press c to begin calibration (s to skip)"); */
  /* tempbyte = get_char(); */
  /* if (tempbyte == 'c'){ */
  /*   calibrate_line_sensor(); */
  /* } */

  Serial.println("heading to menu");
  menu();
}

void timerISR()
{
  ISR_Happened = 1;
  nISR++;
  if (ISR_state == 1){
    ISR_state = 0;
    digitalWrite(squarewave_pin, LOW);
  }
  else{
    ISR_state = 1;
    digitalWrite(squarewave_pin, HIGH);
  }
  //
}

void loop()
{
  if (ISR_Happened == 1){
    digitalWrite(loop_pin, HIGH);
    ISR_Happened = 0;
    cur_t = micros();
    //Serial.println(cur_t);
    t = cur_t-t0;
    if (t < 0){
      t += 65536;
    }
    t_ms = t/1000.0;
    t_sec = t_ms/1000.0;
    dt = t_sec - prev_t;
    if (t_sec > t_stop){
      G_cart.stop_motors();
      delay(100);
      G_cart.stop_motors();
      Serial.print("#end test, stopping motors");
      digitalWrite(serial_pin, LOW);
      myTimer.end();
      delay(2000);
      menu();
    }

    //Serial.println(nISR);

    //bdsysloopcode
   U_line.find_output();
   U_forward_step.find_output(t_sec);
   G_cart.find_output();
   sum_junct.find_output(t_sec);
   D.find_output(t_sec);
   sat.find_output(t_sec);
   add.find_output();
   subtract.find_output();
   G_cart.send_commands(nISR);


   //HB.send_command(motor_speed);
   // print data
   /* digitalWrite(serial_pin, HIGH); */
   Serial.print(t_ms);
   //bdsysprintcode
   print_comma_then_int(add.read_output());
   print_comma_then_int(subtract.read_output());
   print_comma_then_int(U_forward_step.read_output());
   print_comma_then_int(line_sense.read_output());
   print_comma_then_int(pend_enc.read_output());


   mynewline();
   /* digitalWrite(serial_pin, LOW); */

   prev_t = t_sec;
   digitalWrite(loop_pin5, LOW);
  }

}
