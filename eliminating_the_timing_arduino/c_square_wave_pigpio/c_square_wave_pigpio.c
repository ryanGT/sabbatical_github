#include <stdlib.h>

#include <signal.h>
#include <unistd.h>


#include <pigpio.h>


void alarmWakeup(int sig_num);


int main(int argc, char *argv[])
{
  unsigned int j;

  int pin = 25;
  int pin2 = 23;//look up a good choice here
  
  gpioInitialise();
  gpioSetMode(pin, PI_OUTPUT);
  gpioSetMode(pin2, PI_OUTPUT);

  signal(SIGALRM, alarmWakeup);   
  ualarm(5000, 5000);


  while(1)// change to for loop so terminate happens
    {
      gpioWrite(pin, 1);
      gpioSleep(PI_TIME_RELATIVE, 0, 2000);
      gpioWrite(pin, 1);
      gpioSleep(PI_TIME_RELATIVE, 0, 2000);
    }


  gpioTerminate();

  return 0;

}//int main(int argc, char *argv[])


void alarmWakeup(int sig_num)
{
  unsigned int i;

  if(sig_num == SIGALRM)
    {
      gpioWrite(pin, 1);
      //for(i=0; i<65535; i++); //do something
      gpioSleep(PI_TIME_RELATIVE, 0, 100);
      gpioWrite(pin,0);
    }

}
