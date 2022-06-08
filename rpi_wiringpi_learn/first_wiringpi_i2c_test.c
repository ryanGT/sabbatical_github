#include <iostream>
#include <wiringPi.h>
#include <wiringPiI2C.h>

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

    // Send data to arduino
    uint8_t data_to_send = 17;
    for (uint8_t i=0; i<100; i++){
      t = micros() - t0;
      dt = t - prev_t;
      printf("i = %i, ", i);
      printf("t = %i, ", t);
      printf("dt = %i, ", dt);      
      data_to_send = 15+i;
      wiringPiI2CWrite(fd, data_to_send);
      std::cout << "Sent data: " << (int)data_to_send << ", ";

      // Read data from arduino
      int received_data = wiringPiI2CRead(fd);
      std::cout << "Data received: " << received_data << ", ";

      if (received_data == data_to_send) {
        std::cout << "Success!\n";
      }
      prev_t = t;
      delayMicroseconds(1000);
    }
    return 0;
}
