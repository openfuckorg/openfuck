#include <SPI.h>
#include <AMIS30543.h>
#include <AccelStepper.h>
//Stepper 1 FWD
const uint8_t amisDirPin1 = 2;
const uint8_t amisStepPin1 = 3;
const uint8_t amisSlaveSelect1 = 4;

//Stepper 2 FWD
const uint8_t amisDirPin2 = 5;
const uint8_t amisStepPin2 = 6;
const uint8_t amisSlaveSelect2 = 7;

//Timing Variables
float ts = 0;
float te = 0;

//Serial Input Variable
int input = 0;

int go_to_f = 0;
int go_to_b = 0;

//Initialize Steppers (Pololu AMIS 30543 Library)
AMIS30543 stepper1; // Forward
AMIS30543 stepper2; // Backward

//Initialize Stepper (Accelstepper Library)
AccelStepper accelStepper1(AccelStepper::DRIVER, amisStepPin1, amisDirPin1); // Forward
AccelStepper accelStepper2(AccelStepper::DRIVER, amisStepPin2, amisDirPin2); // Backward


void setup() {
  // Initialize Serial and SPI
  Serial.begin(115200);
  SPI.begin();

  //Initialize Steppers
  stepper1.init(amisSlaveSelect1); //Forward
  stepper2.init(amisSlaveSelect2); //Backward
  delay(5);

  //Stepper 1 FWD
  stepper1.resetSettings();
  stepper1.setCurrentMilliamps(385);
  stepper1.setStepMode(1);
  stepper1.enableDriver();

  delay(5);
  //Stepper 2 BCK

  stepper2.resetSettings();
  stepper2.setCurrentMilliamps(385);
  stepper2.setStepMode(1);
  stepper2.enableDriver();

  // Maximum Speed and Acceleration

  //Stepper 1 FWD
  accelStepper1.setMaxSpeed(900.0); //Spec Sheet Limit 585
  accelStepper1.setAcceleration(15000.0);
  //accelStepper1.setMaxSpeed(1000.0); //Maximum Tested
  //accelStepper1.setAcceleration(20000.0);//Maximum Tested


  //Stepper 2 BCK
  accelStepper2.setMaxSpeed(900.0); //Spec Sheet Limit 585
  accelStepper2.setAcceleration(15000.0);

  //accelStepper2.setMaxSpeed(1000.0); //Maximum Tested
  //accelStepper2.setAcceleration(20000.0);//Maximum Tested


  // Home the Steppers fully closed
  //FWD HOME
  accelStepper1.runToNewPosition(-500);
  accelStepper1.setCurrentPosition(0);
  // BCK HOME
  accelStepper2.runToNewPosition(-500);
  accelStepper2.setCurrentPosition(0);

}

void loop() {

  // Serial Input
  if (Serial.available() > 0) {
    input = Serial.read();

    if (input >= 0 && input <= 100) {
      go_to_f = input * 4;
      accelStepper1.moveTo(go_to_f);  ;
    }

    else if (input >= 101 && input <= 201) {
      go_to_b = (input - 101) * 4;
      accelStepper2.moveTo(go_to_b);
    }

    else if (input == 210) {  //Home the Valves
      accelStepper1.moveTo(-500);
      accelStepper2.moveTo(-500);
      //stepper1.enableDriver();
      //stepper2.enableDriver();
      while ((abs(accelStepper1.distanceToGo()) > 0) && (abs(accelStepper2.distanceToGo()) > 0)) {
        accelStepper1.run();
        accelStepper2.run();
      }
      accelStepper1.setCurrentPosition(0);
      accelStepper2.setCurrentPosition(0);
    }

    else if (input == 211) { // go to zero
      accelStepper1.moveTo(0);
      accelStepper2.moveTo(0);
      //stepper1.enableDriver();
      //stepper2.enableDriver();
      accelStepper1.runToPosition();
      accelStepper2.runToPosition();
    }
    else if (input == 212) { // go to full open
      accelStepper1.moveTo(400);
      accelStepper2.moveTo(400);
      //stepper1.enableDriver();
      //stepper2.enableDriver();
      accelStepper1.runToPosition();
      accelStepper2.runToPosition();

    }

    else if (input == 213) { //FWD Step + 10
      accelStepper1.moveTo(accelStepper1.currentPosition() + 10);
      //stepper1.enableDriver();
      ts = millis();
      accelStepper1.runToPosition();
      te = millis();
      Serial.println(te - ts);


    }
    else if (input == 214) { //FWD Step - 10
      accelStepper1.moveTo(accelStepper1.currentPosition() - 10);
      // stepper1.enableDriver();
      ts = millis();
      accelStepper1.runToPosition();
      te = millis();
      Serial.println(te - ts);
    }

    else if (input == 215) { //BCK Step + 10
      accelStepper2.moveTo(accelStepper2.currentPosition() + 10);
      //stepper2.enableDriver();
      ts = millis();
      accelStepper2.runToPosition();
      te = millis();
      Serial.println(te - ts);
    }
    else if (input == 216) { //BCK Step - 10
      accelStepper2.moveTo(accelStepper2.currentPosition() - 10);
      // stepper2.enableDriver();
      ts = millis();
      accelStepper2.runToPosition();
      te = millis();
      Serial.println(te - ts);
    }

  }

  //Run the steppers
  accelStepper1.run();
  accelStepper2.run();

}




