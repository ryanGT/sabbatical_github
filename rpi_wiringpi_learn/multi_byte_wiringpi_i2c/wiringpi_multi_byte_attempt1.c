#include <iostream>
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <stdio.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <linux/i2c-dev.h>
#include <i2c/smbus.h>
#include <unistd.h>

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

// compile cmd:
// g++ -o wiringpi_multi_byte_attempt1.o wiringpi_multi_byte_attempt1.c -lwiringPi -li2c

// performance cpu comand:
// echo performance | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor


//uint32_t t1, t2, dt;

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

    int q;
    
    for (q=0; q<out_bytes; q++){
      outArray[q] = (q+1)*2;
    }
    // Send data to arduino
    t1 = micros();
    write(fd, outArray, out_bytes);
    t2 = micros();
    dt_send = t2-t1;
    printf("data sent\n");
    printf("dt_send (micros): %i\n", dt_send);
    delay(500);

    read(fd, inArray, in_bytes);

    printf("received:\n");
    for (q=0; q<in_bytes; q++){
       if ( q > 0){
        printf(", ");
      }
      printf("%d",inArray[q]);
    }
    printf("\n");
    //fclose(fp);
    return 0;
}
