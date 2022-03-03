#include <Wire.h>
int SLAVE_ADDRESS = 0x04;

byte buf [100];
byte out_buf [100];
volatile byte pos;
volatile boolean process_it;

byte n_lsb, n_msb, enc_lsb, enc_msb, v_lsb, v_msb;

// Todo:
// - add command motor
// - add encoder
// - change communication scheme 
#define encoderPinA 2
#define encoderPinB 11

#define in_bytes 5
#define out_bytes 6
byte inArray[in_bytes];
byte outArray[out_bytes];
bool new_data;
int mypause = 1;

int pwn_pin = 9;
int in1 = 6;
int in2 = 4;

#define sendPin A0
#define receivePin A1
#define controlPin A2
#define isrPin A3

int analogPin = 0;
int accel = 0;

int ISR_Happened;
int ISR_state = 0;
//  encoder
volatile bool _EncoderBSet;
volatile long encoder_count = 0;


const byte mask = B11111000;
int prescale = 1;

int n;
int nIn;
int nISR;
int v1;
int v_out;

int inByte;
int fresh;
bool send_ser;

byte num_received;

int prevenc;
int posbreak;
int negbreak;

void command_motor(int speed){

  speed = mysat(speed);

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


void setup()
{
  Serial.begin(115200);

  Serial.println("i2c read flag micropython motor control");
  Serial.println("with pinISR interrupt");
  Serial.println("03/03/2022");
  Serial.print("\n");
  
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(read_all_bytes);
  Wire.onRequest(sendData);
  Wire.setClock(400000);//<-- is this actually bad for a secondary device?
 
  //Serial1.begin(115200);

  send_ser = false;


  for(int i=0;i<out_bytes;i++){
    outArray[i] = i;
  }


  pinMode(sendPin, OUTPUT);
  pinMode(receivePin, OUTPUT);
  pinMode(controlPin, OUTPUT);
  pinMode(isrPin, OUTPUT);  
    

  digitalWrite(receivePin, LOW);
  digitalWrite(sendPin, LOW);
  digitalWrite(controlPin, LOW);
  digitalWrite(isrPin, LOW);  
// encoder
  pinMode(encoderPinA, INPUT); 
  pinMode(encoderPinB, INPUT); 
  // turn on pullup resistors
  digitalWrite(encoderPinA, HIGH);
  digitalWrite(encoderPinB, HIGH);

  // encoder pin on interrupt 0 (pin 2)
  attachInterrupt(0, doEncoder, RISING);
  attachInterrupt(1, pinISR, CHANGE);
  
  Serial.println("motor test begin");
  command_motor(255);
  delay(500);
  command_motor(0);
  Serial.println("motor test over");
}

unsigned char getsecondbyte(int input){
    unsigned char output;
    output = (unsigned char)(input >> 8);
    return output;
}

 

int reassemblebytes(unsigned char msb, unsigned char lsb){
    int output;
    output = (int)(msb << 8);
    output += lsb;
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

void mynewline(){
  Serial.print('\n');
}

void print_int_with_label(char * label, int val){
  Serial.print(label);
  Serial.print(val);
}

void print_int_with_comma(int val){
  Serial.print(val);
  Serial.print(",");
}

void print_int_with_newline(int val){
  Serial.print(val);
  mynewline();
}


void loop()
{
  if ( new_data ){
    new_data = false;
    //digitalWrite(i2cprocessPin, HIGH);  

    //Serial.println("new data");
    if (inArray[0] == 1){
      //Serial.print("#start new test");
      //Serial.print("#==");
      encoder_count = 0;
      outArray[0] = 0;
      outArray[1] = 0;
      outArray[2] = 0;
      outArray[3] = 0;
      
      mypause = 1;//wait until first ISR read from RPi to increment the ISR n counter
      TCNT2  = 0;//reset timer count to sync both Arduinos
    }
    else if (inArray[0] == 2){
      // test over
      v1 = 0;
      command_motor(v1);
      Serial.println("#end");
    }
    else if (inArray[0] == 3){
      // main control case
      digitalWrite(controlPin, HIGH);  
      v_msb = inArray[1];
      v_lsb = inArray[2];
      n_msb = inArray[3];
      n_lsb = inArray[4];
      v1 = reassemblebytes(v_msb,v_lsb);
      //command_motor(v1);
      enc_lsb = (byte)encoder_count;
      enc_msb = getsecondbyte(encoder_count);
      outArray[0] = enc_msb;
      outArray[1] = enc_lsb;
      digitalWrite(controlPin, LOW);  
    }
    else if (inArray[0] == 7){
      ISR_Happened = 0;
      //digitalWrite(handshake_pin, LOW);
    }
    /* else if (inArray[0] == 30){ */
    /*   v1 = reassemblebytes(inArray[1],inArray[2]); */
    /*   Serial.println(v1); */
    /*   command_motor(v1); */
    /* } */
    //Serial.print(inArray[0]);
    //Serial.print(",");    
    //Serial.print(inArray[1]);
    //Serial.print(",");
    //Serial.print(inArray[2]);
    //Serial.print('\n');
    //Serial.print(nISR);
    //Serial.print(",");
    //Serial.println(v1);
    //digitalWrite(i2cprocessPin, LOW);  
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

void read_all_bytes(int numBytes){
  digitalWrite(receivePin, HIGH);  
  for(int i=0;i<numBytes;i++){
    inArray[i] = Wire.read();
  }
  new_data = true;
  digitalWrite(receivePin, LOW);
}

void sendData(){
  digitalWrite(sendPin, HIGH);  
  Wire.write(outArray,sizeof(outArray));
  //if (ISR_Happened == 1){
  //    digitalWrite(handshake_pin, HIGH);
  //}
  mypause = 0;
  digitalWrite(sendPin, LOW);    
}

/* void sendData(){ */
/*   //Wire.write(ISR_Happened); */
/*   //while( ISR_Happened == 0){};//wait */
/*   Wire.write(nISR); */
/*   if (ISR_Happened == 1){ */
/*       digitalWrite(handshake_pin, HIGH); */
/*   } */
/*   mypause = 0; */
/* } */


// need pin ISR


void pinISR()
{     
  digitalWrite(isrPin, HIGH);
  //Serial.println("pinISR");
  ISR_Happened = 1;
  if (mypause == 0){
    nISR++;
  }
  //analogWrite(pwmA, v1);
  //v_out = v1*v1;
  command_motor(v1);
  outArray[2] = n_msb;
  outArray[3] = n_lsb;
  //accel = analogRead(analogPin);
  digitalWrite(isrPin, LOW);
}

