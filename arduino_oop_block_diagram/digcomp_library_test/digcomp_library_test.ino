#include <kraussserial.h>
#include <rtblockdiagram.h>

#define encoderPinA 2
#define squarewave_pin 12
byte inByte;


step_input u = step_input(0.5, 150);

float b_vect[2] = {0.00196503, 0.00195682};
float a_vect[3] = {1.0, -1.98359041, 0.98751226};

digcomp_block Gz = digcomp_block(b_vect, a_vect, 2, 3, &u);

//attachInterrupt(0, isr, FALLING);
int nISR;
int nIn;
int ISR_Happened;
int mypause = 1;
int ISRstate = 0;
int motor_speed, raw_motor_speed, vOut,error;
bool send_ser;
int u_int, y_int;

unsigned long t0;
unsigned long t;
unsigned long t1;
unsigned long cur_t;
float t_ms, t_sec, prev_t, dt;

void setup(){
   Serial.begin(115200);
   Serial.println("digcomp library test rtbd v.1.1");
   Serial.println("using rtblockdiagram library");
   pinMode(squarewave_pin, OUTPUT);

   Serial.print("_len_in = ");
   Serial.println(Gz._len_in);
   Serial.print("_len_out = ");
   Serial.println(Gz._len_out);
   
   //=======================================================
   // set up the Timer2 interrupt
   //=======================================================
   cli();// disable global interrupts temporarily
   TCCR2A = 0;// set entire TCCR3A register to 0
   TCCR2B = 0;// same for TCCR3B
   //TCNT3  = 0;//initialize counter value to 0
   // set compare match register for 8khz increments
   OCR2A = 57;// = (16*10^6) / (8000*8) - 1 (must be <255)
   //OCR2A = 148;// = (16*10^6) / (8000*8) - 1 (must be <255)
   // turn on CTC mode
   //TCCR3A |= (1 << WGM31);
   //TCCR3B = (TCCR3B & 0b11111000) | 0x07;// set prescaler to 1034
   // taken from here: https://playground.arduino.cc/Main/TimerPWMCheatsheet
   //        scroll down to "Pins 11 and 3: controlled by timer 3"
   //TCCR3B = (TCCR3B & 0b11111000) | 0x06;

   TCCR2B |= (1 << WGM12);

   // Set CS10 and CS12 bits for 1024 prescaler:
   TCCR2B |= (1 << CS10);
   TCCR2B |= (1 << CS12);

   TIMSK2 |= (1 << OCIE2A);
   sei();// re-enable global interrupts
   //=======================================================
   menu();
}


void menu(){
  Serial.println("enter any character to start a test");
  char mychar = get_char();
  // reset encoders and t0 at the start of a test
  t0 = micros();
  ISR_Happened = 0;// clear flag and wait for next time step
  Serial.print("t0 =");
  Serial.println(t0);
}


void loop(){
  if (ISR_Happened == 1){
    ISR_Happened = 0;
    cur_t = micros();
    t = cur_t-t0;
    if (t < 0){
      t += 65536;
    }
    t_ms = t/1000.0;

    if (t_ms > 5000){
      menu();
    }
    t_sec = t_ms/1000.0;
    dt = t_sec - prev_t;

    u_int = u.get_output(t_sec);
    y_int = Gz.get_output(t_sec);
    // print data
    Serial.print(t_ms);
    print_comma_then_int(u_int);
    print_comma_then_int(y_int);
    print_comma_then_float(Gz._out_vect[0]);
    mynewline();

    prev_t = t_sec;
  }
}


ISR(TIMER2_COMPA_vect)
{
  ISR_Happened = 1;
  nISR++;
  
  //G.send_command(motor_speed);
  
  if (ISRstate == 1){
    ISRstate = 0;
    digitalWrite(squarewave_pin, LOW);
  }
  else{
    ISRstate = 1;
    digitalWrite(squarewave_pin, HIGH);
  }
}
