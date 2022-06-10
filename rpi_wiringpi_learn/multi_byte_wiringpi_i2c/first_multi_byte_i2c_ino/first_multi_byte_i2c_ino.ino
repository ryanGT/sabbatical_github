#include <Wire.h>

#define SLAVE_ADDRESS 0x08

byte data_to_echo = 0;

#define in_bytes 8
#define out_bytes 8
byte inArray[in_bytes];
byte outArray[out_bytes];

bool new_data;

void setup() 
{
  Wire.begin(SLAVE_ADDRESS);
  Wire.setClock(400000);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);
  Serial.begin(115200);
}

void loop() {
  if ( new_data ){
    new_data = false;
    Serial.println("new data:");
    for (int q=0; q<in_bytes; q++){
      if (q > 0){
	Serial.print(", ");
      }
      Serial.print(inArray[q]);
    }
  }

}

void receiveData(int numBytes){
  //digitalWrite(receivePin, HIGH);  
  for(int i=0;i<numBytes;i++){
    inArray[i] = Wire.read();
  }
  new_data = true;
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
  Wire.write(data_to_echo);
}
