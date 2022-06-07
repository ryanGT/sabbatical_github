#include <iostream>
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <stdio.h>

#define DEVICE_ID 0x08

uint32_t t0 = micros();
uint32_t t, prev_t;
uint16_t dt;


int main (int argc, char **argv)
{
    // Setup I2C communication
    int fd = wiringPiI2CSetup(DEVICE_ID);
    if (fd == -1) {
        std::cout << "Failed to init I2C communication.\n";
        return -1;
    }
    std::cout << "I2C communication successfully setup.\n";

    FILE * fp;

    fp = fopen ("data.txt", "w");
    //fprintf(fp, "%s %s %s %d", "We", "are", "in", 2012);
   
    wiringPiSetup();
    pinMode(0, OUTPUT);
    pinMode(1, OUTPUT);
    pinMode(3, OUTPUT);
    // Send data to arduino
    uint8_t data_to_send = 17;
    for (uint8_t i=0; i<100; i++){
      digitalWrite(3, HIGH);
      t = micros() - t0;
      dt = t - prev_t;
      //printf("i = %i, ", i);
      //printf("t = %i, ", t);
      //printf("dt = %i, ", dt);      
      data_to_send = 15+i;
      digitalWrite(3, LOW );

      digitalWrite(0, HIGH);
      wiringPiI2CWrite(fd, data_to_send);
      //std::cout << "Sent data: " << (int)data_to_send << ", ";

      // Read data from arduino
      int received_data = wiringPiI2CRead(fd);
      digitalWrite(0, LOW);
      
      //std::cout << "Data received: " << received_data << ", ";

      //if (received_data == data_to_send) {
      //  std::cout << "Success!\n";
      //}

      digitalWrite(1, HIGH);
      fprintf(fp, "i = %i, t = %i, dt = %i, sent = %i, received = %i\n", i, t, dt, data_to_send, received_data);
      prev_t = t;
      digitalWrite(1, LOW);
      delayMicroseconds(100);
    }
    fclose(fp);
    return 0;
}
