#include <stdlib.h>

#include <signal.h>
#include <unistd.h>
#include <zhelpers.h>
#include <math.h>

#include <pigpio.h>


void alarmWakeup(int sig_num);

int pin = 21;
int pin2 = 20;//look up a good choice here

int ISRHappened = 0;
int ISRstate = 0;
int nISR = 0;

int main(int argc, char *argv[])
{
  //unsigned int j;
  int mymax = pow(2, 16);
  printf("mymax = %i\n", mymax);
  char update [20];

  void *context = zmq_ctx_new ();
  void *publisher = zmq_socket (context, ZMQ_PUB);
  int rc = zmq_bind (publisher, "tcp://*:5556");
  assert (rc == 0);
  
  gpioInitialise();
  gpioSetMode(pin, PI_OUTPUT);
  gpioSetMode(pin2, PI_OUTPUT);

  signal(SIGALRM, alarmWakeup);   
  ualarm(2000, 2000);


  while(1)// change to for loop so terminate happens
    {
      if (ISRHappened == 1){
        ISRHappened = 0;
        gpioWrite(pin2, 1);
        if (nISR >= mymax){
          nISR = 0;
        }
        sprintf (update, "%i",nISR);
        s_send (publisher, update);
        gpioWrite(pin2, 0);
      }
    }

  zmq_close (publisher);
  zmq_ctx_destroy (context);
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
}
