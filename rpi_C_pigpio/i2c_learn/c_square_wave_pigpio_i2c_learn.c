#include <stdlib.h>
#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <math.h>

#include <pigpio.h>

//compile command:
//gcc -Wall -pthread -o c_square_wave_pigpio_i2c_learn.o c_square_wave_pigpio_i2c_learn.c -lpigpio -lrt


void alarmWakeup(int sig_num);

int pin = 21;
int pin2 = 20;//look up a good choice here

int ISRHappened = 0;
int ISRstate = 0;
int nISR = 0;

int i2c_mega;
int mega_addr = 7;

int speed1, speed2;

#define mega_in_bytes 8
char mega_in_buf[mega_in_bytes];
int bytes_read;
#define mega_out_bytes 7
char mega_out_buf[mega_out_bytes];

char ilsb, imsb, lsb1, msb1, lsb2, msb2;

char getsecondbyte(int input){
  char output;
  output = (char)(input >> 8);
  return output;
}


int main(int argc, char *argv[])
{
  //unsigned int j;
  int mymax = pow(2, 16);
  printf("mymax = %i\n", mymax);
  
  gpioInitialise();
  gpioSetMode(pin, PI_OUTPUT);
  gpioSetMode(pin2, PI_OUTPUT);

  signal(SIGALRM, alarmWakeup);   
  ualarm(2000, 2000);//500 Hz (2ms)
  //ualarm(4000, 4000);//250 Hz (4ms)

  i2c_mega = i2cOpen(1, mega_addr, 0);// bus #, addr, flags=0

  //python: pi.i2c_write_byte(m_ino, 1)
  i2cWriteByte(i2c_mega, 1);


  /* if (inArray[0] == 3){ */
  /*   // - process the data if it is there */
  /*   // - probably need to send [3,0,0,0,0] to keep the motors stopped, just to be safe */
  /*   digitalWrite(controlPin, HIGH); */
  /*   n_msb = inArray[1]; */
  /*   n_lsb = inArray[2]; */
  /*   v1_msb = inArray[3]; */
  /*   v1_lsb = inArray[4]; */
  /*   v1 = reassemblebytes(v1_msb,v1_lsb); */
  /*   v2_msb = inArray[5]; */
  /*   v2_lsb = inArray[6]; */
  /*   v2 = reassemblebytes(v2_msb,v2_lsb); */

  mega_out_buf[0] = 3;

  for (int i=0; i<100; i++){
    printf("i = %i\n", i);
    
    /* while (ISRHappened == 0){ */
    /*   //sleep */
    /*   usleep(10); */
    /* } */
    /* ISRHappened = 0; */
    
    /*       ISRHappened = 0; */
    /*       gpioWrite(pin2, 1); */
    /*       if (nISR >= mymax){ */
    /*         nISR = 0; */
    /*       } */
    /*       gpioWrite(pin2, 0); */
    /*     } */

    
    /* speed1 = 5*i; */
    /* speed2 = -speed1; */
    
    /* ilsb = (char)i; */
    /* imsb = getsecondbyte(i); */
    /* lsb1 = (char)speed1; */
    /* msb1 = getsecondbyte(speed1); */
    /* lsb2 = (char)speed2; */
    /* msb2 = getsecondbyte(speed2); */

    /* mega_out_buf[0] = 3; */
    /* mega_out_buf[1] = imsb; */
    /* mega_out_buf[2] = ilsb; */
    /* mega_out_buf[3] = msb1; */
    /* mega_out_buf[4] = lsb1; */
    /* mega_out_buf[5] = msb2; */
    /* mega_out_buf[6] = lsb2; */

    //i2cWriteDevice(i2c_mega, mega_out_buf, mega_out_bytes);

    // python: e, cur_resp = pi.i2c_read_device(m_ino,6)
    //int i2cReadDevice(unsigned handle, char *buf, unsigned count)
    //  This reads count bytes from the raw device into buf.

    //bytes_read = i2cReadDevice(i2c_mega, mega_in_buf, mega_in_bytes);

    /* for (int k=0; k<7; k++){ */
    /*   if (k>0){ */
    /*     printf(", "); */
    /*   } */
    /*   printf("%i", mega_in_buf[k]); */
    /* } */
    /* printf("\n"); */
    printf("end of loop, i=%i\n", i);
  }

  i2cClose(i2c_mega);

  /* while(1)// change to for loop so terminate happens */
  /*   { */
  /*     if (ISRHappened == 1){ */
  /*       ISRHappened = 0; */
  /*       gpioWrite(pin2, 1); */
  /*       if (nISR >= mymax){ */
  /*         nISR = 0; */
  /*       } */
  /*       gpioWrite(pin2, 0); */
  /*     } */
  /*   } */

  

  gpioTerminate();

  return 0;

}//int main(int argc, char *argv[])


void alarmWakeup(int sig_num)
{
  if(sig_num == SIGALRM)
    {
      ISRHappened = 1;
      nISR++;
      if (ISRstate == 1){
        ISRstate = 0;
      }
      else if (ISRstate == 0){
        ISRstate = 1;
      }
      gpioWrite(pin, ISRstate);
      //for(i=0; i<65535; i++); //do something
    }
  exit(sig_num);
}
