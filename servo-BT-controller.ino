#include <Servo.h>
#include <SoftwareSerial.h>

Servo panServo;  // Create a servo object for the pan servo
Servo tiltServo; // Create a servo object for the tilt servo

int panAngle = 90;  // Initial pan angle (centered)
int tiltAngle = 90; // Initial tilt angle (centered)

SoftwareSerial BTSerial(2, 3); // RX, TX for HC-05 Bluetooth module

void setup() {
  panServo.attach(9);  // Attach the pan servo to pin 9
  tiltServo.attach(10); // Attach the tilt servo to pin 10
  BTSerial.begin(9600); // Bluetooth module communication
  Serial.begin(9600); // Serial monitor for debugging
}

void loop() {
  // Read data from Bluetooth module
  if (BTSerial.available() > 0) {
    char command = BTSerial.read();

    // Process the received Bluetooth command
    int angleValue;
    switch (command) {
      case '1':
        // Move the pan servo to 35 degrees
        angleValue = 35;
        panAngle = angleValue;
        panServo.write(panAngle);
        break;
      case '2':
        // Move the pan servo to 70 degrees
        angleValue = 70;
        panAngle = angleValue;
        panServo.write(panAngle);
        break;
      case '3':
        // Move the pan servo to 105 degrees
        angleValue = 105;
        panAngle = angleValue;
        panServo.write(panAngle);
        break;
      case '4':
        // Move the pan servo to 140 degrees
        angleValue = 140;
        panAngle = angleValue;
        panServo.write(panAngle);
        break;
        case '5':
        // Move the pan servo to 180 degrees
        angleValue = 180;
        panAngle = angleValue;
        panServo.write(panAngle);
        break;
      default:
        // Handle other commands or errors here, if needed
        break;
    }
  }

  // Debugging: Print servo angles to the Serial Monitor
  Serial.print("Pan Angle: ");
  Serial.print(panAngle);
  Serial.print(", Tilt Angle: ");
  Serial.println(tiltAngle);
  
  delay(100);
}
