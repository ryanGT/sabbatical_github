// Wire Slave Sender
// by Nicholas Zambetti <http://www.zambetti.com>

// Demonstrates use of the Wire library
// Sends data as an I2C/TWI slave device
// Refer to the "Wire Master Reader" example for use with this

// Created 29 March 2006

// This example code is in the public domain.

#define encoderPinB 2
#define encoderPinA 3

//  encoder
volatile bool _EncoderBSet;
volatile bool _EncoderASet;
volatile long encoder_count = 0;

bool sent_data = false;
int n_sent = 0;

#include <Wire.h>

void setup() {
  Wire.begin(8);                // join i2c bus with address #8
  Wire.onRequest(requestEvent); // register event
  Wire.onReceive(receiveEvent);

  Serial.begin(115200);

  //bdsyswelcomecode
  Serial.println("pendulum encoder minion i2c");

 //Serial.begin(230400);

  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);
  // encoder
  pinMode(encoderPinA, INPUT); 
  pinMode(encoderPinB, INPUT); 
  // turn on pullup resistors
  digitalWrite(encoderPinA, HIGH);
  digitalWrite(encoderPinB, HIGH);

  // encoder pin on interrupt 0 (pin 2)
  attachInterrupt(0, doEncoderB, CHANGE);
  attachInterrupt(1, doEncoderA, CHANGE);  

}

void loop() {
  delay(5);
  digitalWrite(13, LOW);
  if (sent_data){ 
      sent_data = false;
      Serial.print(n_sent);
      Serial.print(",");
      Serial.print(encoder_count);
      Serial.print('\n');
  }
  //Serial.println(encoder_count);
}


unsigned char getsecondbyte(int input){
    unsigned char output;
    output = (unsigned char)(input >> 8);
    return output;
}


// function that executes whenever data is requested by master
// this function is registered as an event, see setup()
void requestEvent() {
  unsigned char lsb, msb;
  lsb = (unsigned char)encoder_count;
  msb = getsecondbyte(encoder_count);
  Wire.write(msb); // respond with message of 6 bytes
  Wire.write(lsb); // respond with message of 6 bytes
  n_sent++;
  sent_data = true;
}

void receiveEvent(int howMany)
{
  digitalWrite(13, HIGH);
  while(Wire.available() > 0) // loop through all but the last
  {
    char c = Wire.read(); // receive byte as a character
    //Serial.print(c);         // print the character
  }
  encoder_count = 0;
  n_sent = 0;
}


void doEncoderA()
{
  // Test transition; since the interrupt will only fire on 'rising' we don't need to read pin A
  //n++;
  _EncoderASet = digitalRead(encoderPinA);   // read the input pin
  _EncoderBSet = digitalRead(encoderPinB);   // read the input pin
  
  // and adjust counter + if A leads B
  if (_EncoderBSet != _EncoderASet){
    encoder_count ++;
  }
  else {
    encoder_count --;
  }
}

void doEncoderB()
{
  // Test transition; since the interrupt will only fire on 'rising' we don't need to read pin A
  //n++;
  _EncoderASet = digitalRead(encoderPinA);   // read the input pin
  _EncoderBSet = digitalRead(encoderPinB);   // read the input pin
  
  // and adjust counter + if A leads B
  if (_EncoderBSet == _EncoderASet){
    encoder_count ++;
  }
  else {
    encoder_count --;
  }
}



