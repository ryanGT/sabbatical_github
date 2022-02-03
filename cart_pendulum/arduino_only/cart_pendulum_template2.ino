#include <kraussserial.h>
#include <rtblockdiagram.h>
#include <QTRSensors.h>
#include <math.h>
#include <Wire.h>
#include <DualMAX14870MotorShield.h>


volatile long encoder_count = 0;

volatile int v_left, v_right;

int test_case;

int state;
int ISR_state;
int squarewave_pin = A7;
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


int dt_micro;
int mydelay;
unsigned long prevt;
float dt_ms;
float dt_sec;
float t_ms_prev;

int tempbyte;
int inByte;
int ISR_Happened;

DualMAX14870MotorShield motors;

void set_speeds(int v_right, int v_left){
  motors.setM1Speed(v_right);
  motors.setM2Speed(v_left);
}

QTRSensors qtr;

void stop_motors(){
  motors.setM1Speed(0);
  motors.setM2Speed(0);
}


const uint8_t SensorCount = 7;//<---
uint16_t sensorValues[SensorCount];

void calibrate_line_sensor(){
  Serial.println("calibrating 200 times");
  int j = 10;//counter to change rotation direction
  int sign = 1;
  for (uint16_t i = 0; i < 200; i++)
  {
    // using j to alternate the rotation of the sensor over the line
    // for autocalibration
    set_speeds(sign*150,-150*sign);
    j++;
    if ( j >= 20 ){
      sign *= -1;
      j = 0;
    }
    qtr.calibrate();
    Serial.println(i);
  }
    set_speeds(0,0);

  Serial.println("calibration results:");
  // print the calibration minimum values measured when emitters were on
  for (uint8_t i = 0; i < SensorCount; i++)
  {
    Serial.print(qtr.calibrationOn.minimum[i]);
    Serial.print(' ');
  }
  Serial.println();

  for (uint8_t i = 0; i < SensorCount; i++)
  {
    Serial.print(qtr.calibrationOn.maximum[i]);
    Serial.print(' ');
  }
  Serial.println();
  Serial.println();
  delay(500);
}


// this will not be auto-generated
class two_motors_dbl_actuator: public double_actuator{
  // a valid sensor class must have a get_reading method with no
  // inputs that returns an int (the sensor reading)
 public:
  DualMAX14870MotorShield* _motors;

  two_motors_actuator(DualMAX14870MotorShield* mymotors){
    _motors = mymotors;
  }

  void send_commands(int speed1, int speed2){
    _motors->setM1Speed(speed1);
    _motors->setM2Speed(speed2);
  }
};


int read_encoder_i2c(){
  int out;

  Wire.requestFrom(8, 2);    // request 2 bytes from slave device #8
  unsigned char lsb, msb;
  while (Wire.available()<2){
    delayMicroseconds(5);
  }
  msb = Wire.read();
  lsb = Wire.read();
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
  }
};


class qtr_line_sensor: public sensor{
 public:
  int output;
  QTRSensors* qtr;

  qtr_line_sensor(QTRSensors* myqtr){
    qtr = myqtr;
  };

  int get_reading(){
    // this will cause the value to be re-read over i2c whenever it is
    // needed.....
    output = qtr->readLineBlack(sensorValues);
    return(output);
  }
}

//bdsysinitcode



void menu(){
  Serial.println("enter any character to start a test");
  char mychar = get_char();
  // reset encoders and t0 at the start of a test
  //enc.encoder_count = 0;
  //bdsysmenucode
  t0 = micros();
  nISR = 0;
  ISR_Happened = 0;// clear flag and wait for next time step
  Serial.print("t0 =");
  Serial.println(t0);
}

void setup()
{
  Wire.begin();        // join i2c bus (address optional for master)
  Serial.begin(115200);

  //bdsyswelcomecode
  Serial.println("using rtblockdiagram library");
  pinMode(squarewave_pin, OUTPUT);

   
  //!// encoder pin on interrupt 0 (pin 2)

  //bdsyssetupcode

  //Serial.print("pendulum/cart v. 1.1.0 RT Serial");
  //Serial.print("\n");

  motors.enableDrivers();
  motors.flipM1(true);

  pinMode(squarewave_pin, OUTPUT);
  
  qtr.setTypeRC();
  qtr.setSensorPins((const uint8_t[]){29,31,33,35,37,39,41}, SensorCount);
  qtr.setEmitterPin(2);

  calibrated = 0;
  
  /* delay(500); */

  /* Serial.println("press c to begin calibration (s to skip)"); */
  /* tempbyte = get_char(); */
  /* if (tempbyte == 'c'){ */
  /*   calibrate_line_sensor(); */
  /* } */

  //calibrate_line_sensor();

  /* // encoder */
  /* pinMode(encoderPinA, INPUT);  */
  /* pinMode(encoderPinB, INPUT);  */
  /* // turn on pullup resistors */
  /* digitalWrite(encoderPinA, HIGH); */
  /* digitalWrite(encoderPinB, HIGH); */

  /* // encoder pin on interrupt 0 (pin 2) */
  /* attachInterrupt(0, doEncoderB, CHANGE); */
  /* attachInterrupt(1, doEncoderA, CHANGE);   */

  // need to switch to Timer3 for Arduino Mega
  //=======================================================
  // set up the Timer2 interrupt
  //=======================================================
  cli();// disable global interrupts temporarily
  TCCR3A = 0;// set entire TCCR3A register to 0
  TCCR3B = 0;// same for TCCR3B
  //TCNT3  = 0;//initialize counter value to 0
  // set compare match register for 8khz increments
  //OCR3A = 156;// = (16*10^6) / (8000*8) - 1 (must be <356)
  OCR3A = 124;// = (16*10^6) / (8000*8) - 1 (must be <356)
  // turn on CTC mode
  //TCCR3A |= (1 << WGM31);
  //TCCR3B = (TCCR3B & 0b11111000) | 0x07;// set prescaler to 1024
  // taken from here: https://playground.arduino.cc/Main/TimerPWMCheatsheet
  //        scroll down to "Pins 11 and 3: controlled by timer 3"
  //TCCR3B = (TCCR3B & 0b11111000) | 0x06;

  TCCR3B |= (1 << WGM12);

  // Set CS10 and CS12 bits for 1024 prescaler:
  //TCCR3B |= (1 << CS10);
  TCCR3B |= (1 << CS12);

  TIMSK3 |= (1 << OCIE3A);
  sei();// re-enable global interrupts
  //=======================================================
  state = 0;
  menu();
}

ISR(TIMER3_COMPA_vect)
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
    ISR_Happened = 0;
    cur_t = micros();
    t = cur_t-t0;
    if (t < 0){
      t += 65536;
    }
    t_ms = t/1000.0;

    if (t_ms > 3000){
      stop_motors();
      menu();
    }
    t_sec = t_ms/1000.0;
    dt = t_sec - prev_t;



    // Read Sensors
    position = qtr.readLineBlack(sensorValues);
    //read encoder from i2c (other Arduino)
    encoder_count = read_encoder_i2c();

    //bdsysloopcode


    //HB.send_command(motor_speed);
    // print data
    Serial.print(t_ms);

    //bdsysprintcode


    mynewline();

    prev_t = t_sec;
  }
  
}
