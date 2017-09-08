#include <microsmooth.h>
//github.com/asheeshr/Microsmooth


int forward = 3;
int backward = 5;
int Sensor = A1;

int input = 0;
int error = 0;
int Position = 0;
int State = 0;
int freeze = 0;

int tolerance = 15;
int early_fwd = 15;
int early_bck = 13;



//Filtering variables below
int filtered = 0;
int i = 0;
uint16_t *ptr;

void setup() {

  // Wait for valve board to boot
  // put your setup code here, to run once:1
  pinMode(forward, OUTPUT);
  pinMode(backward, OUTPUT);
  pinMode(Sensor, INPUT);
  Serial.begin(115200);
  ptr = ms_init(EMA);



  input = analogRead(A1); // the piston is home wherever it is

}

void loop() {

  // We use a exponential moving average filter to smooth the analog input
  i = analogRead(A1);
  filtered = ema_filter(i, ptr);
  Position = filtered;

  //Serial.println(Position);

  // Serial Control Singal Receiver
  if (Serial.available() > 0) {
    freeze = 0;

    //for ingesting positions sent as serial bytes
    input = Serial.read();
    input = 4 * input;



    /*
     //for ingesting positions sent (0-9) over the arduino serial client
     input = Serial.read() - '0';
     input = 100 * input;
     Serial.println(input);
     */

  }
  //Motion Control - Calculate Error
  error = input - Position;

  // Check to see if we have stopped and stay there
  if ((abs (error) <= tolerance)  && State == 0) {
    //Serial.println("STOPSTOP");;
    digitalWrite(forward, LOW);
    digitalWrite(backward, LOW);
    delay(10);
    //input = Position;
    Serial.write(255);
    //Serial.println(error);
  }


  /* If we are travelling forward, here is how early we issue
  the stop command in order to avoid overshoot */
  else if ((error < (tolerance + early_fwd) ) && State == 1 && freeze == 0) {
    //Serial.println("STOP_F");
    freeze = 1; //freeze
    State = 0; // reset state
    digitalWrite(forward, LOW);
    digitalWrite(backward, LOW);
    delay(12);
    digitalWrite(forward, LOW);//brake
    digitalWrite(backward, HIGH);
    delay(20);
    digitalWrite(forward, LOW);
    digitalWrite(backward, LOW);
    //Serial.write(255);
  }

  /* If we are travelling backward, here is how early we issue
  the stop command in order to avoid overshoot */
  else if ((error > (-tolerance - early_bck) ) && State == 2 && freeze == 0) {
    //Serial.println("STOP_B");
    freeze = 1; //freeze
    State = 0; //reset state
    digitalWrite(forward, LOW);
    digitalWrite(backward, LOW);
    delay(12);
    digitalWrite(forward, HIGH);//brake
    digitalWrite(backward, LOW);
    delay(15);
    digitalWrite(forward, LOW);
    digitalWrite(backward, LOW);
    //Serial.write(255);
  }

  // Move Forward
  else if (error > 0 && freeze == 0) {
    State = 1;
    // Serial.println("FWD");
    digitalWrite(forward, HIGH);
    digitalWrite(backward, LOW);
  }

  // Move Backward
  else if (error < 0 && freeze == 0) {
    State = 2;
    //Serial.println("REV");
    digitalWrite(forward, LOW);
    digitalWrite(backward, HIGH);
  }

  // If we're stuck in a weird state, just say we're done.
  else {
    State = 0;
    digitalWrite(forward, LOW);
    digitalWrite(backward, LOW);
    //Serial.println(error);
    Serial.write(254);
  }
}

