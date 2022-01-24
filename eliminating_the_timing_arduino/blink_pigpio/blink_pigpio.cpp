#include <pigpio.h>

using namespace std;

int main()
{
  int pin = 25;
  gpioInitialise();
  gpioSetMode(pin, PI_OUTPUT);
  gpioWrite(pin, 1);
  gpioSleep(PI_TIME_RELATIVE, 1, 0);
  gpioWrite(pin,0);
  gpioTerminate();
  return 0;
}
