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
int dt_micro;
int mydelay;
unsigned long prevt;
float dt_ms;
float dt_sec;
float t_ms;
float t_ms_prev;
float t_sec;

int tempbyte;
int inByte;
int ISR_Happened;


// serial stuff
int reassemblebytes(unsigned char msb, unsigned char lsb){
  int output;
  output = (int)(msb << 8);
  output += lsb;
  return output;
}


unsigned char getsecondbyte(int input){
    unsigned char output;
    output = (unsigned char)(input >> 8);
    return output;
}


int readtwobytes(void){
    unsigned char msb, lsb;
    int output;
    int iter = 0;
    while (Serial.available() <2){
      iter++;
      if (iter > 1e5){
    break;
      }
    }
    msb = Serial.read();
    lsb = Serial.read();
    output = reassemblebytes(msb, lsb);
    return output;
}

void SendTwoByteInt(int intin){
    unsigned char lsb, msb;
    lsb = (unsigned char)intin;
    msb = getsecondbyte(intin);
    Serial.write(msb);
    Serial.write(lsb);
}

char get_char(){
  char mybyte;
  while (Serial.available() == 0){
    delay(10);
  }
  mybyte = Serial.read();
  return(mybyte);
}

int get_int(){
  int out_int;
  out_int = 0;
  while (out_int == 0){
    while (Serial.available() == 0){
      delay(10);
    }
    out_int = Serial.parseInt();
  }
  return(out_int);
  
}

int get_positive_int(){
  int myint = get_int();
  if (myint < 0){
    myint = 0;
  }
  return(myint);
}

float get_float(){
  float out_float;

  out_float = 0;
  while (out_float == 0){
    while (Serial.available() == 0){
      delay(10);
    }
    out_float = Serial.parseFloat();
  }
  return(out_float);
  
}

float get_positive_float(){
  float myfloat = get_float();
  if (myfloat < 0){
    myfloat = 0;
  }
  return(myfloat);
}



// end serial stuff


DualMAX14870MotorShield motors;

void set_speeds(int v_right, int v_left){
  motors.setM1Speed(v_right);
  motors.setM2Speed(v_left);
}

QTRSensors qtr;

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

void setup()
{
  Wire.begin();        // join i2c bus (address optional for master)
  Serial.begin(115200);

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
  OCR3A = 156;// = (16*10^6) / (8000*8) - 1 (must be <356)
  // turn on CTC mode
  //TCCR3A |= (1 << WGM31);
  //TCCR3B = (TCCR3B & 0b11111000) | 0x07;// set prescaler to 1034
  // taken from here: https://playground.arduino.cc/Main/TimerPWMCheatsheet
  //        scroll down to "Pins 11 and 3: controlled by timer 3"
  //TCCR3B = (TCCR3B & 0b11111000) | 0x06;

  TCCR3B |= (1 << WGM12);

  // Set CS10 and CS12 bits for 1024 prescaler:
  TCCR3B |= (1 << CS10);
  TCCR3B |= (1 << CS12);

  TIMSK3 |= (1 << OCIE3A);
  sei();// re-enable global interrupts
  //=======================================================
  state = 0;
}

ISR(TIMER3_COMPA_vect)
{
  ISR_Happened = 1;
  if (ISR_state == 1){
    ISR_state = 0;
    digitalWrite(squarewave_pin, LOW);
  }
  else{
    ISR_state = 1;
    digitalWrite(squarewave_pin, HIGH);
  }
  //nISR++;
}

void loop()
{
  if ( ISR_Happened == 1){
    ISR_Happened = 0;
    if (nISR == 0){
      t0 = millis();
    }
    prevt = t;//moved from in between the two lines below 03/29/17 11:50AM
    //digitalWrite(timer1_pin, HIGH);
    //digitalWrite(other_pin, HIGH);
    t = millis()-t0;
    nISR++;
    //dt_ms = (t-prevt)/1000.0;
    dt_sec = dt_ms/1000.0;
    t_ms = t/1000.0;
    dt_ms = t_ms - t_ms_prev;
    t_sec = t_ms/1000.0;


    // Read Sensors
    position = qtr.readLineBlack(sensorValues);
    //read encoder from i2c (other Arduino)
    encoder_count = read_encoder_i2c();

    if (Serial.available() > 0) {
      inByte = Serial.read();
      if (inByte == 1){
        //main control case
        nIn = readtwobytes();
        v_left = readtwobytes();
        v_right = readtwobytes();
        if (nIn == 0){
          t0 = millis();
        }
      }
      else if (inByte == 2){
        //start new test
        send_ser = true;
        nISR = -1;
        delay(5);
        SendTwoByteInt(2);// make python wait until it recieves this
      }
      else if (inByte == 3){
        // end test
        send_ser = false;
        v_left = 0;
        v_right = 0;
        delay(5);
        SendTwoByteInt(3);// make python wait until it recieves this
      }
      else if (inByte == 4){
        // send calibration status
        SendTwoByteInt(calibrated);// make python wait until it recieves this
      }
      else if (inByte == 5){
        // calibrate the line sensor
        calibrate_line_sensor();// make python wait until it recieves this
        calibrated = 1;
      }
      else if (inByte == 6){
        // send version message
        delay(5);
        Serial.print("pendulum cart v. 1.2.2");
        Serial.print('\n');
      }
      else if (inByte == 7){
        // set stop_n
        stop_n = readtwobytes();
      }
      
    }

    if (nISR > stop_n+10){
      set_speeds(0,0);
      send_ser = false;
    }
    else{
      set_speeds(v_right, v_left);
    }
    //================================
    // Send Data
    //================================
    if (send_ser){
        SendTwoByteInt(nISR);
        SendTwoByteInt(v_left);
        SendTwoByteInt(v_right);
        SendTwoByteInt(position);
        SendTwoByteInt(encoder_count);
        Serial.write(10);//newline
      }    
    //================================
    // End Send Data
    //================================
  }
  
}
