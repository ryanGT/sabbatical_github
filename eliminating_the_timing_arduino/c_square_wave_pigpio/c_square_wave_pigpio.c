#include <stdlib.h>

#include <signal.h>
#include <unistd.h>

#include <pigpio.h>


void alarmWakeup(int sig_num);

int pin = 21;
int pin2 = 20;//look up a good choice here


int main(int argc, char *argv[])
{
  unsigned int j;
  
  gpioInitialise();
  gpioSetMode(pin, PI_OUTPUT);
  gpioSetMode(pin2, PI_OUTPUT);

  signal(SIGALRM, alarmWakeup);   
  ualarm(2000, 2000);


  for (j=0;j<1000;j++)// change to for loop so terminate happens
    {
      gpioWrite(pin2, 1);
      gpioSleep(PI_TIME_RELATIVE, 0, 2000);
      gpioWrite(pin2, 0);
      gpioSleep(PI_TIME_RELATIVE, 0, 2000);
    }


  gpioTerminate();

  return 0;

}//int main(int argc, char *argv[])


void alarmWakeup(int sig_num)
{
  if(sig_num == SIGALRM)
    {
      gpioWrite(pin, 1);
      //for(i=0; i<65535; i++); //do something
      gpioSleep(PI_TIME_RELATIVE, 0, 100);
      gpioWrite(pin,0);
    }
}
