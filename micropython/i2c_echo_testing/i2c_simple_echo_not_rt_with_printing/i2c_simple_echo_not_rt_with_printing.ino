#include <Wire.h>
//int SLAVE_ADDRESS = 0x16;
int SLAVE_ADDRESS = 0x04;
int ledPin = 13;
int inByte;
boolean ledOn = false;
int i=0;
#define Nbytes 10
byte myArray[Nbytes];
byte outArray[Nbytes];
bool new_data;

int sendPin = 8;
int receivePin = 9;
int loopPin = 10;

void setup() 
{
    pinMode(ledPin, OUTPUT);
    Wire.begin(SLAVE_ADDRESS);
    Wire.onReceive(read_2_bytes);
    Wire.onRequest(echo_2_bytes);

    pinMode(sendPin, OUTPUT);
    pinMode(receivePin, OUTPUT);
    pinMode(loopPin, OUTPUT);    
    
    Serial.begin(115200);
    Serial.println("i2c arduino micropython simple echo with printing");

    for(int i=0;i<Nbytes;i++){
      outArray[i] = i;
    }

    for(int i=0;i<Nbytes;i++){
      Serial.print("i = ");
      Serial.print(i);
      Serial.print(", outArray[i] = ");
      Serial.print(outArray[i]);
      Serial.print('\n');
    }
}

void loop()
{
  //delay(10);
  if ( new_data ){
    digitalWrite(loopPin, HIGH);
    new_data = false;
    outArray[0] = myArray[0];
    outArray[1] = myArray[1];
    digitalWrite(loopPin, LOW);    

    Serial.print("first byte\n");
    Serial.print(myArray[0]);
    Serial.print("\n");
    Serial.print("second byte\n");
    Serial.print(myArray[1]);
    Serial.print("\n");
  }
    /* Serial.print("third byte\n"); */
    /* Serial.print(myArray[2]); */
    /* Serial.print("\n"); */
    //for(i=1;i<Nbytes;i++){
    //  outArray[i] = 254-i;
    //}
}


void read_2_bytes(int numBytes){
  digitalWrite(receivePin, HIGH);
  for(int i=0;i<numBytes;i++){
	  myArray[i] = Wire.read();
  }
  new_data = true;
  digitalWrite(receivePin, LOW);  
}

void echo_2_bytes(){
  digitalWrite(sendPin, HIGH);
  Wire.write(outArray,sizeof(outArray));
  digitalWrite(sendPin, LOW);  
}
