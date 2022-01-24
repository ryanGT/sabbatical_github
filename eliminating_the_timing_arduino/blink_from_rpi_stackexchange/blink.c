#include <stdio.h>
#include <wiringPi.h>

#define LED     0

int main (void)
{

  wiringPiSetup() ; 

  pinMode (LED, OUTPUT) ;

  while(1)
    {
      digitalWrite (LED, 1) ;     // On
      delay (500) ;               // mS
      digitalWrite (LED, 0) ;     // Off
      delay (500) ;
      printf("Blink \n");
    }
  return 0 ;
}
