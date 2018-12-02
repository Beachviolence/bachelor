// INFORMARSJON //

// Filnavn: motorkontroller.ino

// Forfatter: Simon Strandvold og Hans Petter Leines

// Beskrivelse:
// Denne koden er lastet opp på arduinobrettet som
// styrer motorene på farkosten og oversetter mottatt
// kommando til handling.

#include <AFMotor.h> //import your motor shield library 
AF_DCMotor motor1(1,MOTOR12_64KHZ); // set up motors.
AF_DCMotor motor2(2,MOTOR12_64KHZ);

int dataRecieved; 
int prevData = 85;
char myvar[5];
int potPin = 2;
int turnSens = 0;

const int U = 85;
const int D = 68;
const int R = 82;
const int L = 76;

void setup() {
  Serial.begin(9600);
  motor1.setSpeed(130);
  motor2.setSpeed (130);
}

void loop() {
  myvar[0] = 'N';
  int bytes = -1;
  while(!Serial.available());
  while(bytes == -1 || bytes == 10){
    bytes = Serial.read();
  }
  dataRecieved = bytes;

  double analogInn = analogRead(potPin);
  double thrust = analogInn/1024;
  turnSens = 300 + thrust * 600;
  
  drive();
  delay(500);
}

void drive(){
  char orientation = prevData;
  switch(dataRecieved){
    case U:
      if(orientation == dataRecieved) break;
      else if (orientation == R) left(turnSens);
      else if (orientation == L) right(turnSens);
      else if (orientation == D) left(turnSens*2);
      break;
    case D:
      if(orientation == dataRecieved) break;
      else if (orientation == R) right(turnSens);
      else if (orientation == L) left(turnSens);
      else if (orientation == U) left(turnSens*2);
      break;
    case R:
      if(orientation == dataRecieved) break;
      else if (orientation == U) right(turnSens);
      else if (orientation == L) left(turnSens*2);
      else if (orientation == D) left(turnSens);
      break;
    case L:
      if(orientation == dataRecieved) break;
      else if (orientation == R) left(turnSens*2);
      else if (orientation == U) right(turnSens);
      else if (orientation == D) right(turnSens*2);
      break;
  }
  motor1.run(FORWARD);
  motor2.run(FORWARD);
  delay(800);
  motor1.run(RELEASE);
  motor2.run(RELEASE);
  prevData = dataRecieved;
  
}

void left(int length){
  motor2.run(FORWARD);
  motor1.run(BACKWARD);
  delay(length);
  motor2.run(RELEASE);
  motor1.run(RELEASE);
}
void right(int length){
  motor1.run(FORWARD);
  motor2.run(BACKWARD);
  delay(length);
  motor2.run(RELEASE);
  motor1.run(RELEASE);
}
