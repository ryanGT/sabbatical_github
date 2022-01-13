#include <Wire.h>
#include <math.h>
// Todo:
// - add command motor
// - add encoder
// - change communication scheme 
#define encoderPinA 2
#define encoderPinB 11

int pwn_pin = 9;
int in1 = 6;
int in2 = 4;

//  encoder
volatile bool _EncoderBSet;
volatile long encoder_count = 0;


const int MPU_addr=0x68;
double AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ; //These will be the raw data from the MPU6050.

const byte mask = B11111000;
int prescale = 1;

int state;

int n;
int nISR;
int amp;
int width;
int n_start = 10;
int v;
int stop_n = 5000;
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

int inByte;
int ISR_Happened;

int u;
float kp;
float kd;
int e;
int e_prev;
float e_dot;
int v_out;
float freq;
float twopi=6.28318531;

void setup()
{
  Wire.begin();
  #if ARDUINO >= 157
  Wire.setClock(400000UL); // Set I2C frequency to 400kHz
  #else
    TWBR = ((F_CPU / 400000UL) - 16) / 2; // Set I2C frequency to 400kHz
  #endif

  Serial.begin(115200);

  Serial.print("flex beam 1: swept sine");
  Serial.print("\n");
  

  // encoder
  pinMode(encoderPinA, INPUT); 
  pinMode(encoderPinB, INPUT); 
  // turn on pullup resistors
  digitalWrite(encoderPinA, HIGH);
  digitalWrite(encoderPinB, HIGH);

  // encoder pin on interrupt 0 (pin 2)
  attachInterrupt(0, doEncoder, RISING);

  Wire.beginTransmission(MPU_addr);
  Wire.write(0x6B);  // PWR_MGMT_1 register
  Wire.write(0);     // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);

  //set sensitivity @ address 1C
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x1C);
  //Wire.write(B00010000);   //here is the byte for sensitivity (8g here) check datasheet for the one u want
  Wire.write(B00011000);//16g (verified)
  Wire.endTransmission(true);

  Wire.beginTransmission(MPU_addr);
  Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr,14,true);  // request a total of 14 registers
  AcX=Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)     
  AcY=Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  AcZ=Wire.read()<<8|Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  Tmp=Wire.read()<<8|Wire.read();  // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
  GyX=Wire.read()<<8|Wire.read();  // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  GyY=Wire.read()<<8|Wire.read();  // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
  GyZ=Wire.read()<<8|Wire.read();  // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)

  //=======================================================
  // set up the Timer2 interrupt
  //=======================================================
  cli();// disable global interrupts temporarily
  //set timer2 interrupt at 8kHz
  TCCR2A = 0;// set entire TCCR2A register to 0
  TCCR2B = 0;// same for TCCR2B
  TCNT2  = 0;//initialize counter value to 0
  // set compare match register for 8khz increments
  OCR2A = 61;// = (16*10^6) / (8000*8) - 1 (must be <256)
  // turn on CTC mode
  TCCR2A |= (1 << WGM21);
  TCCR2B = (TCCR2B & 0b11111000) | 0x07;// set prescaler to 1024
  // taken from here: https://playground.arduino.cc/Main/TimerPWMCheatsheet
  //        scroll down to "Pins 11 and 3: controlled by timer 2"
  //TCCR2B = (TCCR2B & 0b11111000) | 0x06;
  // enable timer compare interrupt
  TIMSK2 |= (1 << OCIE2A);
  sei();// re-enable global interrupts
  //=======================================================
  state = 0;
}


void command_motor(int speed){
  if (speed > 0){
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
    analogWrite(pwn_pin, speed);
  }
  else if (speed < 0){
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
    analogWrite(pwn_pin, abs(speed));
  }
  else {
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
    analogWrite(pwn_pin, 0);
  }
}



void mynewline(){
  Serial.print('\n');
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

int mysat(int vin){
  int mymax = 255;
  int mymin = -255;
  int vout;
  
  if ( vin > mymax ){
    vout = mymax;
  }
  else if ( vin < mymin ){
    vout = mymin;
  }
  else{
    vout = vin;
  }

  return(vout);
}

void menu(){
  Serial.print("swept sine testing");
  mynewline();
  Serial.print("input amplitude, kp, and kd");
  mynewline();
  Serial.print("desired amplitude:");
  mynewline();
  
  state = 0;// If something goes wrong, set code to return to menu

  while (Serial.available() == 0){
      delay(10);
  }

  amp = get_int();

  Serial.print("you entered an amplitude of ");
  Serial.print(amp);
  mynewline();

  Serial.print("enter kp:");
  mynewline();
  
  while (Serial.available() == 0){
      delay(10);
  }

  kp = get_float();
  Serial.print("you entered a kp of ");
  Serial.print(kp);
  mynewline();
  
  Serial.print("enter kd:");
  mynewline();
  
  while (Serial.available() == 0){
      delay(10);
  }

  kd = get_float();
  Serial.print("you entered a kd of ");
  Serial.print(kd);

  mynewline();
  delay(200);

  nISR = 0;
  encoder_count = 0;
  ISR_Happened = 0;
  state = 1;
}


void loop()
{
  if ( state == 0){
    menu();
  }
    
  else if (state == 1){
   if ( ISR_Happened == 1){
    ISR_Happened = 0;
    if (nISR < (stop_n)){
      if (nISR == 0){
	t0 = micros();
      }
      prevt = t;//moved from in between the two lines below 03/29/17 11:50AM
      //digitalWrite(timer1_pin, HIGH);
      //digitalWrite(other_pin, HIGH);
      t = micros()-t0;
      nISR++;
      dt_ms = (t-prevt)/1000.0;
      dt_sec = dt_ms/1000.0;
      t_ms = t/1000.0;
      t_sec = t_ms/1000.0;

      //---------------------------
      // Read Accel
      //---------------------------
      Wire.beginTransmission(MPU_addr);
      Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
      Wire.endTransmission(false);
      Wire.requestFrom(MPU_addr,14,true);  // request a total of 14 registers
      AcX=Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)     
      AcY=Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
      AcZ=Wire.read()<<8|Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
      Tmp=Wire.read()<<8|Wire.read();  // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
      GyX=Wire.read()<<8|Wire.read();  // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
      GyY=Wire.read()<<8|Wire.read();  // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
      GyZ=Wire.read()<<8|Wire.read();  // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)

      // step response
      if (nISR < n_start){
	u = 0;
      }
      else{
	//swept sine
	float m = 0.2;
	freq = m*t_sec;
	u = amp*sin(twopi*freq*t_sec);
      }
      e = u-encoder_count;
      e_dot = (e-e_prev)/(t_ms-t_ms_prev);
      v = kp*e + kd*e_dot;
      v_out = mysat(v);
      command_motor(v_out);

      Serial.print(nISR);
      Serial.print(",");
      Serial.print(t_ms);
      Serial.print(",");
      Serial.print(u);
      Serial.print(",");
      Serial.print(v);
      Serial.print(",");
      Serial.print(v_out);
      Serial.print(",");
      Serial.print(encoder_count);
      //Serial.print(",");
      //Serial.print(AcX);
      //Serial.print(",");
      //Serial.print(AcY);
      Serial.print(",");
      Serial.print(AcZ);
      mynewline();
      //t1 = micros();
      //dt_micro = t1-t;
      //mydelay = 3900-dt_micro;
      //digitalWrite(other_pin, LOW);
      //delayMicroseconds(mydelay);

      // save values for next time step
      e_prev = e;
      t_ms_prev = t_ms;
    }
 
    else {
      Serial.println("#end");
      Serial.println("#====================");
      Serial.println("");
      command_motor(0);
      state = 0;
    }
   }
  }
}



// Interrupt service routines for the right motor's quadrature encoder
void doEncoder()
{
  // Test transition; since the interrupt will only fire on 'rising' we don't need to read pin A
  //n++;

  _EncoderBSet = digitalRead(encoderPinB);   // read the input pin
  
  // and adjust counter + if A leads B
  if (_EncoderBSet){
    encoder_count ++;
  }
  else {
    encoder_count --;
  }
}



ISR(TIMER2_COMPA_vect)
{
  ISR_Happened = 1;
  /* if (ISRstate == 1){ */
  /*   ISRstate = 0; */
  /*   digitalWrite(sw_pin, LOW); */
  /* } */
  /* else{ */
  /*   ISRstate = 1; */
  /*   digitalWrite(sw_pin, HIGH); */
  /* } */
}
