//#include <iostream>
#include <pigpio.h>
#include <stdio.h>

#define DEVICE_ID 0x08

uint32_t t, t1, t2, t3, prev_t;
uint16_t dt, dt_send, dt_receive;

int i2c_mega;

int pin = 17;
int pin2 = 18;//look up a good choice here

int LOW=0;
int HIGH=1;


int main (int argc, char **argv)
{
    // Setup I2C communication
  gpioInitialise();
  gpioSetMode(pin, PI_OUTPUT);
  gpioSetMode(pin2, PI_OUTPUT);

  uint32_t t0 = gpioTick();
  
  //signal(SIGALRM, alarmWakeup);   
  //ualarm(2000, 2000);//500 Hz (2ms)
  //ualarm(4000, 4000);//250 Hz (4ms)

  i2c_mega = i2cOpen(1, DEVICE_ID, 0);// bus #, addr, flags=0

  //python: pi.i2c_write_byte(m_ino, 1)
  

    FILE * fp;

    fp = fopen ("data.txt", "w");
    //fprintf(fp, "%s %s %s %d", "We", "are", "in", 2012);
   
    // Send data to arduino
    uint8_t data_to_send = 17;
    for (uint8_t i=0; i<100; i++){
      gpioWrite(3, HIGH);
      t = gpioTick() - t0;
      dt = t - prev_t;
      printf("i = %i, ", i);
      //printf("t = %i, ", t);
      //printf("dt = %i, ", dt);      
      data_to_send = 15+i;
      gpioWrite(3, LOW );

      t1 = gpioTick();
      gpioWrite(0, HIGH);
      i2cWriteByte(i2c_mega, data_to_send);
      //std::cout << "Sent data: " << (int)data_to_send << ", ";
      t2 = gpioTick();
      // Read data from arduino
      int received_data = i2cReadByte(i2c_mega);
      gpioWrite(0, LOW);
      t3 = gpioTick();
      
      //std::cout << "Data received: " << received_data << ", ";

      //if (received_data == data_to_send) {
      //  std::cout << "Success!\n";
      //}

      dt_send = t2-t1;
      dt_receive = t3-t2;
      gpioWrite(1, HIGH);
      fprintf(fp, "i = %i, dt = %i, dt_send = %i, dt_receive = %i, sent = %i, received = %i\n", i, dt, dt_send, dt_receive,
	      data_to_send, received_data);
      prev_t = t;
      gpioWrite(1, LOW);
      //delayMicroseconds(100);
    }
    fclose(fp);
    i2cClose(i2c_mega);
    gpioTerminate();
    return 0;
}
