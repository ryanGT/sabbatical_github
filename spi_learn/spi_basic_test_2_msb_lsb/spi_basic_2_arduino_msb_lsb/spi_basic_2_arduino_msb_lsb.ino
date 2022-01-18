// Written by Nick Gammon
// February 2011


#include <SPI.h>

byte buf [100];
volatile byte pos;
volatile boolean process_it;
int msb, lsb, n;

void setup (void)
{
  Serial.begin (115200);   // debugging
  Serial.println("basic spi test 2, msb and lsb");
  // turn on SPI in slave mode
  SPCR |= bit (SPE);

  // have to send on master in, *slave out*
  pinMode(MISO, OUTPUT);

  // get ready for an interrupt 
  pos = 0;   // buffer empty
  process_it = false;

  // now turn on interrupts
  SPI.attachInterrupt();

}  // end of setup


// SPI interrupt routine
ISR (SPI_STC_vect)
{
byte c = SPDR;  // grab byte from SPI Data Register

  // add to buffer if room
  if (pos < sizeof buf)
    {
    buf [pos++] = c;

    // example: newline means time to process buffer
    if (pos > 1)
      process_it = true;

    }  // end of room available
}  // end of interrupt routine SPI_STC_vect

// main loop - wait for flag set in interrupt routine
void loop (void)
{
  int i, c;
  //delay(5);
  if (process_it)
    { msb = buf[0];
      lsb = buf[1];
      n = 256*msb+lsb;
      Serial.print(msb);
      Serial.print(',');
      Serial.print(lsb);
      Serial.print(',');
    Serial.println(n);
    pos = 0;
    buf[0] = 0;
    buf[1] = 0;
    process_it = false;
  }  // end of flag set
}  // end of loop