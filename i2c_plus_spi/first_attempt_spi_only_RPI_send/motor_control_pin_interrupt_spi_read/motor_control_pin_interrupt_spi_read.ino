#include <Wire.h>
int SLAVE_ADDRESS = 0x04;
#include <SPI.h>

byte buf [100];
volatile byte pos;
volatile boolean process_it;

// Todo:
// - add command motor
// - add encoder
// - change communication scheme 
#define encoderPinA 2
#define encoderPinB 5

#define in_bytes 3
#define out_bytes 6
byte inArray[in_bytes];
byte outArray[out_bytes];
bool new_data;
int mypause = 1;

int pwn_pin = 9;
int in1 = 6;
int in2 = 4;

#define isrPin 8
#define sendPin 7
#define receivePin 10
#define triggerPin 12
#define LEDPin 13

int analogPin = 0;
int accel = 0;

int ISR_Happened;

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

  Serial.println("i2c plus spi read motor control two arduinos");
  Serial.println("pin interrupt");
  Serial.println("01/18/2022");
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


  pinMode(isrPin, OUTPUT);
  pinMode(sendPin, OUTPUT);
  pinMode(receivePin, OUTPUT);
  pinMode(triggerPin, OUTPUT);
  pinMode(LEDPin, OUTPUT);

  digitalWrite(isrPin, LOW);
  digitalWrite(receivePin, LOW);
  digitalWrite(triggerPin, LOW);
  digitalWrite(sendPin, LOW);
  digitalWrite(LEDPin, LOW);

  // encoder
  pinMode(encoderPinA, INPUT); 
  pinMode(encoderPinB, INPUT); 
  // turn on pullup resistors
  digitalWrite(encoderPinA, HIGH);
  digitalWrite(encoderPinB, HIGH);

  // encoder pin on interrupt 0 (pin 2)
  attachInterrupt(0, doEncoder, RISING);
  attachInterrupt(1, pinISR, CHANGE);

  SPCR |= bit (SPE);

  // have to send on master in, *slave out*
  pinMode(MISO, OUTPUT);

  // get ready for an interrupt 
  pos = 0;   // buffer empty
  process_it = false;

  // now turn on interrupts
  SPI.attachInterrupt();

  
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
  unsigned char lsb, msb;

  if ( new_data ){
    new_data = false;
    Serial.println("new data");
    if (inArray[0] == 1){
      Serial.print("#start new test");
      nISR = 0;
      ISR_Happened = 0;
      encoder_count = 0;
      mypause = 1;//wait until first ISR read from RPi to increment the ISR n counter
      TCNT2  = 0;//reset timer count to sync both Arduinos
    }
    else if (inArray[0] == 2){
      // test over
      v1 = 0;
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
  }

  if (process_it){
    v1 = reassemblebytes(buf[0],buf[1]);
    pos = 0;
    buf[0] = 0;
    buf[1] = 0;
    process_it = false;
    command_motor(v1);
  }
  
  unsigned char n_lsb, n_msb;
  unsigned char e_lsb, e_msb;  
  
  if (ISR_Happened > 0){
    ISR_Happened = 0;

    n_lsb = (unsigned char)nISR;
    n_msb = getsecondbyte(nISR);

    outArray[0] = n_msb;
    outArray[1] = n_lsb;

    e_lsb = (unsigned char)encoder_count;
    e_msb = getsecondbyte(encoder_count);
    
    outArray[2] = e_msb;
    outArray[3] = e_lsb;

    //if (mypause == 0){
    if (false){
      print_int_with_comma(n_msb);
      print_int_with_comma(n_lsb);
      print_int_with_comma(e_msb);
      print_int_with_newline(e_lsb);    
    }
      
    //digitalWrite(sendPin, LOW);
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
  //digitalWrite(receivePin, HIGH);  
  for(int i=0;i<numBytes;i++){
    inArray[i] = Wire.read();
  }
  new_data = true;
  //digitalWrite(receivePin, LOW);
}

void sendData(){
  //digitalWrite(sendPin, HIGH);  
  Wire.write(outArray,sizeof(outArray));
  //if (ISR_Happened == 1){
  //    digitalWrite(handshake_pin, HIGH);
  //}
  mypause = 0;
  //digitalWrite(sendPin, LOW);    
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
  //accel = analogRead(analogPin);
  digitalWrite(isrPin, LOW);
}

ISR (SPI_STC_vect)
{
byte c = SPDR;  // grab byte from SPI Data Register

  // add to buffer if room
  if (pos < sizeof buf)
    {
    buf [pos++] = c;

    // example: newline means time to process buffer
    if (pos > 1)
      process_it = true;

    }  // end of room available
}  // end of interrupt routine SPI_STC_vect

