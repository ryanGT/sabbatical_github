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
const int N=1000;
int i_echo[N];
int two_byte_response[N];

#define in_bytes 8
#define out_bytes 8
char inArray[in_bytes];
char outArray[out_bytes];

unsigned char ilsb, imsb;

// compile cmd:
// g++ -o wiringpi_multi_byte_attempt1.o wiringpi_multi_byte_attempt1.c -lwiringPi -li2c

// performance cpu comand:
// echo performance | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

unsigned char getsecondbyte(int input){
  unsigned char output;
  output = (unsigned char)(input >> 8);
  return output;
}

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
    // load the outArray
    for (q=0; q<out_bytes; q++){
      outArray[q] = (q+1)*2;
    }
    // Send data to arduino
    //t1 = micros();
    t1 = millis();

    // transmit data in a loop
    int i;

    for (i=0; i<N; i++){
      // break i into two bytes
      ilsb = (unsigned char)i;
      imsb = getsecondbyte(i);
      outArray[0] = imsb;
      outArray[1] = ilsb;
      write(fd, outArray, out_bytes);
      delayMicroseconds(500);
      read(fd, inArray, in_bytes);
      i_echo[i] = 256*inArray[0] + inArray[1];
      two_byte_response[i] = 256*inArray[2] + inArray[3];
      delayMicroseconds(500);
    }
    
    //t2 = micros();
    t2 = millis();
    dt_send = t2-t1;
    printf("data sent\n");
    //delay(500);



    printf("received:\n");
    for (i=0; i<N; i++){
      printf("%i, %i, %i\n", i, i_echo[i], two_byte_response[i]); 
    }
    printf("\n");
    printf("loop time: %i milliseconds\n", dt_send);
    float ave_loop_time;
    ave_loop_time = ((float)dt_send)/N;
    printf("ave_loop_time: %0.6g milliseconds\n", ave_loop_time);
    //fclose(fp);
    return 0;
}
