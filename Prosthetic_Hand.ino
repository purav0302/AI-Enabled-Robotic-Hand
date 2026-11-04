#include <Servo.h>

Servo thumbServo;
Servo indexServo;
Servo middleServo;
Servo ringServo;
Servo pinkyServo;


void setup() {

  Serial.begin(115200);

  thumbServo.attach(3);
  indexServo.attach(5);
  middleServo.attach(6);
  ringServo.attach(9);
  pinkyServo.attach(10);


  // Start with hand OPEN
  thumbServo.write(0);            // normal
  indexServo.write(180);           // reversed
  middleServo.write(180);          // reversed
  ringServo.write(0);              // normal
  pinkyServo.write(180);            // reversed

  delay(1000);
}


void loop() {

  if (Serial.available()) {

    String command = Serial.readStringUntil('\n');

    int separator = command.indexOf(':');

    if (separator != -1) {

      String finger = command.substring(0, separator);
      int angle = command.substring(separator + 1).toInt();


      // Thumb normal
      if (finger == "THUMB") {
        thumbServo.write(angle);
      }

      // Index reversed
      else if (finger == "INDEX") {
        indexServo.write(180 - angle);
      }

      // Middle reversed
      else if (finger == "MIDDLE") {
        middleServo.write(180 - angle);
      }

      // Ring normal
      else if (finger == "RING") {
        ringServo.write(angle);
      }

      // Pinky reversed
      else if (finger == "PINKY") {
        pinkyServo.write(180 - angle);
      }

    }
  }
}
