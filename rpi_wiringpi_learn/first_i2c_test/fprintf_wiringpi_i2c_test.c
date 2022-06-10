#include <iostream>
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <stdio.h>

#define DEVICE_ID 0x08

uint32_t t0 = micros();
uint32_t t, t1, t2, t3, prev_t;
uint16_t dt, dt_send, dt_receive;
uint32_t send_total=0;
float ave_send;
int N=100;

int main (int argc, char **argv)
{
  printf("at top of main\n");
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

    printf("file open\n");
    wiringPiSetup();
    pinMode(0, OUTPUT);
    pinMode(1, OUTPUT);
    pinMode(3, OUTPUT);
    // Send data to arduino
    uint8_t data_to_send = 17;
    printf("before for loop\n");
    for (uint8_t i=0; i<N; i++){
      printf("inside for loop\n");
      digitalWrite(3, HIGH);
      t = micros() - t0;
      dt = t - prev_t;
      printf("i = %i, ", i);
      //printf("t = %i, ", t);
      //printf("dt = %i, ", dt);      
      data_to_send = 15+i;
      digitalWrite(3, LOW );

      t1 = micros();
      digitalWrite(0, HIGH);
      wiringPiI2CWrite(fd, data_to_send);
      //std::cout << "Sent data: " << (int)data_to_send << ", ";
      t2 = micros();
      // Read data from arduino
      int received_data = wiringPiI2CRead(fd);
      digitalWrite(0, LOW);
      t3 = micros();
      
      //std::cout << "Data received: " << received_data << ", ";

      //if (received_data == data_to_send) {
      //  std::cout << "Success!\n";
      //}

      dt_send = t2-t1;
      dt_receive = t3-t2;
      digitalWrite(1, HIGH);
      send_total += dt_send;
      fprintf(fp, "i = %i, dt = %i, dt_send = %i, dt_receive = %i, sent = %i, received = %i\n", i, dt, dt_send, dt_receive,
	      data_to_send, received_data);
      prev_t = t;
      digitalWrite(1, LOW);
      delayMicroseconds(100);
    }
    printf("after for loop\n");
    fclose(fp);
    ave_send = send_total/N;
    printf("ave_send = %f\n", ave_send);
    //pclose(fd);
    return 0;
}
