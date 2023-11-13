#include <Servo.h>
Servo panServo;
Servo tiltServo;
int panAngle = 65;  // initial angle for pan servo
int tiltAngle = 60;  // initial angle for tilt servo
int panIncrement = 10;  // increment for smooth movement
bool isMoving = false;  // flag to indicate if the servo is currently moving

void setup() {
  Serial.begin(9600);
  panServo.attach(9);  // assuming pan servo is connected to pin 9
  panServo.write(panAngle);  // set initial pan angle
  // Assuming you have a tilt servo connected to another pin
  tiltServo.attach(10);
  tiltServo.write(tiltAngle);  // set initial tilt angle
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();

    // Process commands
    if (command == 'I') {
      initializeServo();
    } else if (command == 'Q') {
      setNewPositions();
    } else if (command == 'L' && !isMoving) {
      moveServo(120);
    } else if (command == 'R' && !isMoving) {
      moveServo(30);
    } else if (command == 'S') {
      stopServo();
    }
  }
}

void initializeServo() {
  panServo.write(panAngle);
  tiltServo.write(tiltAngle);
}

void setNewPositions() {
  panServo.write(0);  // Set pan to 0
  tiltServo.write(165);  // Set tilt to 165
}

void moveServo(int targetAngle) {
  isMoving = true;
  int currentAngle = panServo.read();

  while (currentAngle != targetAngle) {
    if (currentAngle < targetAngle) {
      currentAngle = min(currentAngle + panIncrement, targetAngle);
    } else {
      currentAngle = max(currentAngle - panIncrement, targetAngle);
    }
    
    panServo.write(currentAngle);
    delay(300);  // Adjust delay for desired speed
    if (Serial.available() > 0 && Serial.read() == 'S') {
      stopServo();
      break;
    }
  }

  isMoving = false;
}

void stopServo() {
  // Stop the servo at the current angle
  // (do nothing here since the servo will maintain its current position)
}
