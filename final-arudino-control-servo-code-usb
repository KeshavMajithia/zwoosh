#include <Servo.h>

Servo panServo;  // Create a servo object for the pan servo
Servo tiltServo; // Create a servo object for the tilt servo



void setup() {
  panServo.attach(9);  // Attach the pan servo to pin 9
  tiltServo.attach(10); // Attach the tilt servo to pin 10
  tiltServo.write(70);
  panServo.write(70);
  Serial.begin(9600); // Initialize USB serial communication
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();

    switch (command) {
      case '1':
        panServo.write(30); // Move the pan servo to 35 degrees
        break;
      case '2':
        panServo.write(55); // Move the pan servo to 70 degrees
        break;
      case '3':
        panServo.write(70); // Move the pan servo to 105 degrees
        break;
      case '4':
        panServo.write(90); // Move the pan servo to 140 degrees
        break;
      case '5':
        panServo.write(105); // Move the pan servo to 180 degrees
        break;
      default:
        // Handle other commands or errors here, if needed
        break;
    }
  }
}
