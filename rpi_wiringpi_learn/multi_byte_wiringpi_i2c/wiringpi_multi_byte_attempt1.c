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

#define in_bytes 8
#define out_bytes 8
char inArray[in_bytes];
char outArray[out_bytes];


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

    //FILE * fp;

    //fp = fopen ("data.txt", "w");
    //fprintf(fp, "%s %s %s %d", "We", "are", "in", 2012);

    wiringPiSetup();
    pinMode(0, OUTPUT);
    pinMode(1, OUTPUT);
    pinMode(3, OUTPUT);
    printf("sending data\n");
    for (int q=0; q<out_bytes; q++){
      outArray[q] = q;
    }
    // Send data to arduino
    write(fd, outArray, out_bytes);
    printf("data sent\n");
    //fclose(fp);
    return 0;
}
