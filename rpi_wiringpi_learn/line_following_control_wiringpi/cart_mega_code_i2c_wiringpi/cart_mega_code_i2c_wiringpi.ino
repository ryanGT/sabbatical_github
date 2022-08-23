#include <kraussserial.h>
#include <math.h>
#include <Wire.h>
#include <DualMAX14870MotorShield.h>
#include <QTRSensors.h>


volatile long encoder_count = 0;

volatile int v_left, v_right;

int test_case;

int state;
int ISR_state;
int squarewave_pin = A7;
int position;

bool print_data = false;

bool sent_data = false;
bool send_ser = false;
byte calibrated = 0;
int n, n_i2c;
int nISR=30000;
byte n_loop;
int amp;
float m=0.1;
int width;
int n_start = 10;
int v;
int stop_n = 200;// hard code this if you want to be lame

unsigned long t0;
unsigned long prev_t_micros;
unsigned long t;
unsigned long t1;
unsigned long cur_t;
float t_ms, t_sec, prev_t, dt;

bool new_data;

#define sendPin A8
#define receivePin A9
#define controlPin A10
#define isrPin A11


const uint8_t SensorCount = 7;//<---
uint16_t sensorValues[SensorCount];

byte mypause;

#define in_bytes 7
#define out_bytes 8
byte inArray[in_bytes];
byte outArray[out_bytes];


int v1, v2;
byte v1_msb, v1_lsb, v2_msb, v2_lsb, pos_msb, pos_lsb, n_msb, n_lsb;

int dt_micro;
byte dt_micro_msb, dt_micro_lsb;

int mydelay;
unsigned long prevt;
float dt_ms;
float dt_sec;
float t_ms_prev;

int tempbyte;
int inByte;
int ISR_Happened;

DualMAX14870MotorShield motors;

QTRSensors qtr;

void set_speeds(int v_right, int v_left){
  motors.setM1Speed(v_right);
  motors.setM2Speed(v_left);
}


void stop_motors(){
  motors.setM1Speed(0);
  motors.setM2Speed(0);
}


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
  calibrated = 1;
  outArray[0] = calibrated;
  delay(500);
}



void menu(){
  Serial.println("enter any character to start a test");
  char mychar = get_char();
  // reset encoders and t0 at the start of a test
  //enc.encoder_count = 0;
  //bdsysmenucode

  t0 = micros();
  ISR_Happened = 0;// clear flag and wait for next time step
  Serial.print("t0 =");
  Serial.println(t0);
}

void setup()
{
  Wire.begin(0x07);                // join i2c bus with address 9
  Wire.onRequest(sendEvent); // register event
  Wire.onReceive(receiveEvent);

  Serial.begin(115200);

  //bdsyswelcomecode
  Serial.println("Mega i2c code for RPI WiringPi C");

  pinMode(squarewave_pin, OUTPUT);

  pinMode(sendPin, OUTPUT);
  pinMode(receivePin, OUTPUT);
  pinMode(controlPin, OUTPUT);
  pinMode(isrPin, OUTPUT);  
    

  digitalWrite(receivePin, LOW);
  digitalWrite(sendPin, LOW);
  digitalWrite(controlPin, LOW);
  digitalWrite(isrPin, LOW);  


  //!// encoder pin on interrupt 0 (pin 2)

  //Serial.print("pendulum/cart v. 1.1.0 RT Serial");
  //Serial.print("\n");

  motors.enableDrivers();
  motors.flipM1(true);

  //attachInterrupt(digitalPinToInterrupt(18), pinISR, CHANGE);

  qtr.setTypeRC();
  qtr.setSensorPins((const uint8_t[]){29,31,33,35,37,39,41}, SensorCount);
  qtr.setEmitterPin(2);

  calibrated = 0;

  for(int i=0;i<out_bytes;i++){
    outArray[i] = i;
  }

  outArray[0] = calibrated;
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
}

unsigned char getsecondbyte(int input){
    unsigned char output;
    output = (unsigned char)(input >> 8);
    return output;
}


void sendEvent() {
  digitalWrite(sendPin, HIGH);  
  Wire.write(outArray,sizeof(outArray));
  //if (ISR_Happened == 1){
  //    digitalWrite(handshake_pin, HIGH);
  //}
  mypause = 0;
  sent_data = true;
  digitalWrite(sendPin, LOW);    
}

void receiveEvent(int numBytes){
  digitalWrite(receivePin, HIGH);  
  for(int i=0;i<numBytes;i++){
    inArray[i] = Wire.read();
  }
  new_data = true;
  //small delays here shouldn't be terrible because the data is already read
  // - measuring the time between receive events to detect glitches on the
  //   micropython side
  //     - as long as the Arduino receives data before the next time step,
  //       everything is assumed to be working correctly
  prev_t_micros = t;
  t = micros();
  dt_micro = t-prev_t_micros;
  digitalWrite(receivePin, LOW);
}

void pinISR()
{     
  digitalWrite(isrPin, HIGH);
  ISR_Happened = 1;
    
  if (inArray[0] == 3){
    // - process the data if it is there
    // - probably need to send [3,0,0,0,0] to keep the motors stopped, just to be safe
    digitalWrite(controlPin, HIGH);
    n_msb = inArray[1];
    n_lsb = inArray[2];
    n_i2c = 256*n_msb + n_lsb;
    v1_msb = inArray[3];
    v1_lsb = inArray[4];
    v1 = reassemblebytes(v1_msb,v1_lsb);
    v2_msb = inArray[5];
    v2_lsb = inArray[6];
    v2 = reassemblebytes(v2_msb,v2_lsb);
    // load up outArray to acknowledge what we have received
    outArray[4] = n_msb;
    outArray[5] = n_lsb;
    dt_micro_lsb = (byte)dt_micro;
    dt_micro_msb = getsecondbyte(dt_micro);
    outArray[6] = dt_micro_msb;
    outArray[7] = dt_micro_lsb;
    digitalWrite(controlPin, LOW);
  }
  set_speeds(v1, v2);
  //analogWrite(pwmA, v1);
  //v_out = v1*v1;
  //accel = analogRead(analogPin);
  digitalWrite(isrPin, LOW);
}


void loop()
{
  /* if (ISR_Happened > 0 ){ */
  /*   ISR_Happened = 0; */
  /*   Serial.print(1); */
  /*   Serial.print(","); */
  /*   Serial.print(v1); */
  /*   Serial.print(","); */
  /*   Serial.print(v2); */
  /*   mynewline(); */
  /* } */
  if ( sent_data ){
    sent_data = false;
    //Serial.println("I sent data");
  }
  if ( new_data ){
    /* Serial.print("new data, inArray = "); */
    /* for (int k=0; k<7; k++){ */
    /*   Serial.print(inArray[k]); */
    /*   if (k<6){ */
    /* 	Serial.print(","); */
    /*   } */
    /*   else{ */
    /* 	Serial.print('\n'); */
    /*   } */
    /* } */

    new_data = false;
    //digitalWrite(i2cprocessPin, HIGH);  

    //Serial.println("new data");
    if (inArray[0] == 1){
      // start new test
      // - what needs to happen here?
      nISR = 0;
      n_loop = 0;
      // - anything else?
    }
    else if (inArray[0] == 2){
      // end test
      stop_motors();
      v1 = 0;
      v2 = 0;
    }

    else if (inArray[0] == 3){
      pinISR();
      if (print_data){
	//n_i2c, v1, v2, position, dt_micro
      	Serial.print(n_i2c);
      	print_comma_then_int(v1);
      	print_comma_then_int(v2);
      	print_comma_then_int(position);
      	print_comma_then_int(dt_micro);
      	mynewline();
      }
    }
    else if (inArray[0] == 4){
      Serial.println("received cal command");
      calibrate_line_sensor();
    }
    /* else if (inArray[0] == 3){ */
    /*   // main control case */
    /*   digitalWrite(controlPin, HIGH);   */
    /*   v1_msb = inArray[1]; */
    /*   v1_lsb = inArray[2]; */
    /*   v1 = reassemblebytes(v1_msb,v1_lsb); */
    /*   v2_msb = inArray[3]; */
    /*   v2_lsb = inArray[4]; */
    /*   v2 = reassemblebytes(v2_msb,v2_lsb); */
    /*   digitalWrite(controlPin, LOW);   */
    /* } */
  }
  position = qtr.readLineBlack(sensorValues);//<--- this will block the reading of new data
  n_loop++;
  // load data into array to send to upy
  outArray[0] = calibrated;
  outArray[1] = n_loop;
  pos_lsb = (byte)position;
  pos_msb = getsecondbyte(position);
  outArray[2] = pos_msb;
  outArray[3] = pos_lsb;
}
  
