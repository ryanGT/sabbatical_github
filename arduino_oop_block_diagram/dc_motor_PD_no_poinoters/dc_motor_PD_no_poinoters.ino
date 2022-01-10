#include <kraussserial.h>

#define encoderPinA 2
#define squarewave_pin 12
byte inByte;


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

class block{
 public:
  // pure virtual function
  virtual int get_output(float t) = 0;
};


class step_input: public block{
 public:
  float on_time;
  float off_time;
  int amp;
  step_input(float switch_on_time, int Amp){
    on_time = switch_on_time;
    amp = Amp;
  }

  int get_output(float t){
    int output=0;
    if (t > on_time){
      output = amp;
    }
    else{
      output = 0;
    }
    return(output);
  }

};

class actuator{
 public:
  // pure virtual function
  virtual void send_command(int speed) = 0;
};


class h_bridge_actuator: public actuator{
 public:
  int in1, in2, pwm_pin;
  h_bridge_actuator(int IN1_PIN, int IN2_PIN, int PWM_PIN){
    in1 = IN1_PIN;
    in2 = IN2_PIN;
    pwm_pin = PWM_PIN;
  }

  void setup(){
    pinMode(pwm_pin, OUTPUT);
    pinMode(in1, OUTPUT);
    pinMode(in2, OUTPUT);
  }
			 
  void send_command(int speed){
    speed = mysat(speed);

    if (speed > 0){
      digitalWrite(in1, LOW);
      digitalWrite(in2, HIGH);
      analogWrite(pwm_pin, speed);
    }
    else if (speed < 0){
      digitalWrite(in1, HIGH);
      digitalWrite(in2, LOW);
      analogWrite(pwm_pin, abs(speed));
    }
    else {
      digitalWrite(in1, LOW);
      digitalWrite(in2, LOW);
      analogWrite(pwm_pin, 0);
    }
  }
};


class sensor{
 public:
  // pure virtual function
  virtual int get_reading() = 0;
};



class encoder: public sensor{
 public:
  volatile bool _EncoderBSet;
  volatile long encoder_count = 0;
  int encoderPinB;

  encoder(int ENCODER_PIN_B){
    encoderPinB = ENCODER_PIN_B;
  }

  void encoderISR()
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

  int get_reading(){
    return(encoder_count);
  }
};


class summing_junction{
 public:
  
  summing_junction(){
  }

  int get_output(int input1, int input2){
    int output;
    output = input1 - input2;
    return(output);
  }

};


class PD_control_block{
 public:
  float Kp;
  float Kd;
  float prev_t, cur_t;
  int prev_in;
  float dt, din_dt;
  int din;
  int output;
  
  PD_control_block(float KP, float KD){
    Kp = KP;
    Kd = KD;
    prev_t = -1.0;
  }

  int get_output(float t, int input_value){
    dt = t - prev_t;
    din = input_value-prev_in;
    din_dt = din/dt;
    output = (int)(Kp*input_value + Kd*din_dt);
    /* if (prev_t < 0){ */
    /*   output = (int)(Kp*input_value); */
    /* } */
    /* else{ */
    /*   
    /*   
    /*   output = (int)(Kp*input_value + Kd*din_dt); */
    /* } */
    /* prev_in = input_value; */
    //prev_t = cur_t;
    return(output);
  }

  void save_values(float t, int input_value){
     prev_t = t;
     prev_in = input_value;
  }

};


class saturation_block{
 public:
  int output;
  
  saturation_block(){
  }

  int get_output(int input_value){
    output = mysat(input_value);
    return(output);
  }

};

  
step_input u = step_input(0.5, 150);

//int pwm_pin = 9;
//int in1 = 6;
//int in2 = 4;


h_bridge_actuator HB = h_bridge_actuator(6, 4, 9);//in1, in2, pwm_pin
encoder enc = encoder(11);

void enc_isr_wrapper() {
  enc.encoderISR();
}

//plant G = plant(&HB, &enc);

summing_junction sum1 = summing_junction();
//P_control_block P = P_control_block(3, &sum1);
PD_control_block PD = PD_control_block(3, 0.1);
saturation_block sat_block = saturation_block();

//attachInterrupt(0, isr, FALLING);
int nISR;
int nIn;
int ISR_Happened;
int mypause = 1;
int ISRstate = 0;
int motor_speed, raw_motor_speed, vOut,error;
bool send_ser;
int prev_enc, u_in;

unsigned long t0;
unsigned long t;
unsigned long t1;
unsigned long cur_t;
float t_ms, t_sec, prev_t, dt;

void setup(){
   Serial.begin(115200);
   Serial.println("OOP for DC motor PD Control v.1.1");
   Serial.println("NO POINTERS!");
   pinMode(squarewave_pin, OUTPUT);

   Serial.print("kp = ");
   Serial.println(PD.Kp);
   Serial.print("kd = ");
   Serial.println(PD.Kd);
   
   // encoder pin on interrupt 0 (pin 2)
   attachInterrupt(0, enc_isr_wrapper, RISING);

   HB.setup();
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
  enc.encoder_count = 0;
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
      HB.send_command(0);
      menu();
    }
    t_sec = t_ms/1000.0;
    dt = t_sec - prev_t;

    u_in = u.get_output(t_sec);
    prev_enc = enc.get_reading();
    error = sum1.get_output(u_in, prev_enc);
    raw_motor_speed = PD.get_output(t_sec, error);
    motor_speed = sat_block.get_output(raw_motor_speed);
    //G.send_command(motor_speed);
    HB.send_command(motor_speed);
    // print data
    Serial.print(t_ms);
    //Serial.print(",");
    //Serial.print(dt,8);
    //print_comma_then_int(u.get_output(t_sec));
    //print_comma_then_int(G.get_output(t_sec));
    print_comma_then_int(motor_speed);
    print_comma_then_int(raw_motor_speed);
    //print_comma_then_int(PD.input_value);
    print_comma_then_float(PD.din_dt);
    //Serial.print(",");
    //Serial.print(PD.prev_t,8);
    //Serial.print(",");
    //Serial.print(PD.dt,8);
    //print_comma_then_int(G.get_reading());
    print_comma_then_int(enc.get_reading());
    mynewline();

    prev_t = t_sec;
    PD.save_values(t_sec, error);
    
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
