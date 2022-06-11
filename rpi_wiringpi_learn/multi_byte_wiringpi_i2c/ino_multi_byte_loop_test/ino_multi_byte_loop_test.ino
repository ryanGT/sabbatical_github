#include <Wire.h>

#define SLAVE_ADDRESS 0x08

byte data_to_echo = 0;

#define in_bytes 8
#define out_bytes 8
byte inArray[in_bytes];
byte outArray[out_bytes];

unsigned long t1, t2;
int dt_read;
int i_received;

bool new_data;

void setup() 
{
  Wire.begin(SLAVE_ADDRESS);
  Wire.setClock(400000);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
  Serial.begin(115200);
  Serial.println("i2c stuff");
}

void loop() {
  if ( new_data ){
    new_data = false;
    //Serial.println("new data:");
    //Serial.print("dt_read = ");
    /* Serial.println(dt_read); */
    /* for (int q=0; q<in_bytes; q++){ */
    /*   if (q > 0){ */
    /* 	Serial.print(", "); */
    /*   } */
    /*   outArray[q] = inArray[q] + 9; */
    /*   Serial.print(inArray[q]); */
    /* } */
    i_received = 256*inArray[0] + inArray[1];
    Serial.print("i = ");
    Serial.print(i_received);
    Serial.print('\n');
  }

}

void receiveData(int numBytes){
  //digitalWrite(receivePin, HIGH);  
  t1 = micros();
  for(int i=0;i<numBytes;i++){
    inArray[i] = Wire.read();
  }
  t2 = micros();
  new_data = true;
  dt_read = t2-t1;
  //small delays here shouldn't be terrible because the data is already read
  // - measuring the time between receive events to detect glitches on the
  //   micropython side
  //     - as long as the Arduino receives data before the next time step,
  //       everything is assumed to be working correctly
  //prev_t_micros = t;
  //t = micros();
  //dt_micro = t-prev_t_micros;
  //digitalWrite(receivePin, LOW);
}

/* void receiveData(int bytecount) */
/* { */
/*   for (int i = 0; i < bytecount; i++) { */
/*     data_to_echo = Wire.read(); */
/*   } */
/* } */

void sendData()
{
  //Wire.write(data_to_echo);
  Wire.write(outArray,sizeof(outArray));
}
