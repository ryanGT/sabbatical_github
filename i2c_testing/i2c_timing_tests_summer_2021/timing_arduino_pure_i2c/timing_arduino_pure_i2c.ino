#include <Wire.h>
int SLAVE_ADDRESS = 0x05;

#include <math.h>
#include <avr/interrupt.h>
#define twopi 6.28318531

int i=0;
#define Nbytes 10
byte myArray[Nbytes];
bool new_data;
byte n_check;
int handshake_pin = 9;
int timing_pin_1 = 3;
int square_wave_pin=A0;
int ISRstate=0;
int nISR;
int stop_n = 250;
unsigned long t0;
unsigned long t;
unsigned long t1;
int dt_micro;
unsigned long prevt;
float dt_ms;
float dt_sec;
float t_ms;
float t_sec;
float y;
int inByte;
int ISR_Happened;
int state;
int mypause=1;
#define out_bytes 3
//byte inArray[in_bytes];
byte outArray[out_bytes];

unsigned char n_lsb, t_lsb, t_msb;

void setup()
{
  Serial.begin(115200);
  Serial.println("timing arduino i2c v 1.0.2");
  Serial.println("with timer interrupt");
  Serial.print("\n");
  Serial.println("07/20/21 11:30AM");
  
  Wire.begin(SLAVE_ADDRESS);
  Wire.setClock(400000);
  Wire.onReceive(read_all_bytes);
  Wire.onRequest(sendData);
  
  pinMode(timing_pin_1, OUTPUT);
  pinMode(handshake_pin, OUTPUT);  
  pinMode(square_wave_pin, OUTPUT);
  
  ISR_Happened = 0;
  
  //=======================================================
  // set up the Timer2 interrupt
  //=======================================================
  cli();// disable global interrupts temporarily
  //set timer2 interrupt at 8kHz
  TCCR2A = 0;// set entire TCCR2A register to 0
  TCCR2B = 0;// same for TCCR2B
  TCNT2  = 0;//initialize counter value to 0
  // set compare match register for 8khz increments
  OCR2A = 124;// 500 Hz at 16 MHz
  //OCR2A = 62;// 500 Hz at 8 MHz
  //OCR2A = 249;// challenge solution
  // turn on CTC mode
  TCCR2A |= (1 << WGM21);
  // from starter code:
  // TCCR2B = (TCCR2B & 0b11111000) | 0x07;// set prescaler to 1024
  // modified:
  TCCR2B = (TCCR2B & 0b11111000) | 0x06;// set prescaler to 1024
  // taken from here: https://playground.arduino.cc/Main/TimerPWMCheatsheet
  //        scroll down to "Pins 11 and 3: controlled by timer 2"
  //TCCR2B = (TCCR2B & 0b11111000) | 0x06;
  // enable timer compare interrupt
  TIMSK2 |= (1 << OCIE2A);
  Serial.print("OCR2A = ");
  Serial.println(OCR2A);
  Serial.print("square_wave_pin = ");
  Serial.println(square_wave_pin);
  sei();// re-enable global interrupts
  //=======================================================
}

void mynewline(){
  Serial.print('\n');
}

/* void menu(){ */
/*   Serial.println("enter s to start a new test"); */
/*   mynewline(); */
/*   state = 0;// If something goes wrong, set code to return to menu */

/*   while ( state == 0){ */
/*     while (Serial.available() == 0){ */
/*       delay(10); */
/*     } */
/*     inByte = Serial.read(); */
/*     if ( inByte == 's' ){ */
/*       nISR = 0; */
/*       state = 1; */
/*       Serial.print("#start"); */
/*       mynewline(); */
/*       Serial.print("#n, t (ms), y(t)"); */
/*       mynewline(); */
/*       delay(50); */
/*       //t0 = micros(); */
/*       t0 = 0;//challenge solution */
/*       ISR_Happened = 0; */
/*     } */
/*     else{ */
/*       Serial.print("input not regonzided: "); */
/*       Serial.print(inByte); */
/*       mynewline(); */
/*     } */
/*   } */
/* } */


void loop()
{
  if (ISR_Happened == 1){
    ISR_Happened = 0;

    n_lsb = (unsigned char)n_check;
    outArray[0] = n_lsb;

    t = micros()-t0;
    t_lsb = (unsigned char)t;
    t_msb = getsecondbyte(t);

    outArray[1] = t_lsb;
    outArray[2] = t_msb;
  }
  
  if ( new_data ){
    new_data = false;
    /* for(i=0;i<Nbytes;i++){ */
    /*   if (i>0){ */
    /* 	Serial.print(", "); */
    /*   } */
    /*   Serial.print(myArray[i]); */
    /* } */
    /* Serial.print('\n'); */

    if (myArray[0] == 1){
      n_check = 0;
      ISR_Happened = 0;
      mypause = 1;//wait until first ISR read from RPi to increment the ISR n counter
      TCNT2  = 0;//deliberately stagger the Arduinos timers
      if (mypause == 1){
          t0 = micros();
      }
    }
    else if (myArray[0] == 7){
      ISR_Happened = 0;
      digitalWrite(handshake_pin, LOW);
    }
  }
  //delayMicroseconds(5);
  /* if ( state == 0){ */
  /*   menu(); */
  /* } */
    
  /* else if (state == 1){ */
  /*   if (( ISR_Happened == 1) && (nISR < stop_n)){ */
  /*     ISR_Happened = 0; */
  /*     if ((t0 == 0) && (nISR < 3)){ */
  /* 	t0 = micros(); */
  /*     } */
  /*     t = micros()-t0; */
  /*     nISR++; */
  /*     t_ms = t/1000.0; */
  /*     t_sec = t_ms/1000.0; */
  
  /*     // do other stuff here */
      
  /*     Serial.print(nISR); */
  /*     Serial.print(","); */
  /*     Serial.print(t_ms); */
  /*     Serial.print(","); */
  
  /*     // print more data here */
  
  /*     mynewline(); */
  /*   } */
 
  /*   else if (nISR >= stop_n){ */
  /*     Serial.println("#end"); */
  /*     Serial.println("#===================="); */
  /*     Serial.println(""); */
  /*     state = 0; */
  /*   } */
  /* } */
}

void read_all_bytes(int numBytes){
  digitalWrite(timing_pin_1, LOW);
  for(int i=0;i<numBytes;i++){
    myArray[i] = Wire.read();
  }
  new_data = true;
}

void sendData(){
  //Wire.write(ISR_Happened);
  //while( ISR_Happened == 0){};//wait
  //Wire.write(n_check);
  Wire.write(outArray,sizeof(outArray));
  if (ISR_Happened == 1){
      digitalWrite(handshake_pin, HIGH);
  }
  mypause = 0;
}

unsigned char getsecondbyte(int input){
    unsigned char output;
    output = (unsigned char)(input >> 8);
    return output;
}


ISR(TIMER2_COMPA_vect)
{
  ISR_Happened = 1;
  if (mypause == 0){
    n_check++;
  }

  // send pin high, will be sent low in i2c receive ISR
  digitalWrite(timing_pin_1, HIGH);
  
  // generate square wave to verify timing
  if (ISRstate == 1){
    ISRstate = 0;
    digitalWrite(square_wave_pin, LOW);
  }
  else{
    ISRstate = 1;
    digitalWrite(square_wave_pin, HIGH);
  }
}
