//  Weather update server
//  Binds PUB socket to tcp://*:5556
//  Publishes random weather updates

#include <zhelpers.h>
#include <math.h>

int main (void)
{
  //  Prepare our context and publisher
  void *context = zmq_ctx_new ();
  void *publisher = zmq_socket (context, ZMQ_PUB);
  int rc = zmq_bind (publisher, "tcp://*:5556");
  assert (rc == 0);

  int mymax = pow(2, 16);
  printf("mymax = %i\n", mymax);
  
  //  Initialize random number generator
  int n=0;
  while (1) {
    //  Send message to all subscribers
    char update [20];
    sprintf (update, "%i",n);
    s_send (publisher, update);
    n++;
    if (n >= mymax){
      n=0;
    }
  }
  zmq_close (publisher);
  zmq_ctx_destroy (context);
  return 0;
}
