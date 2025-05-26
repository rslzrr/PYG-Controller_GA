int VRx = A0; // X-axis pin
int VRy = A1; // Y-axis pin
int SW = 2;   // Joystick button pin

// Button pins
int whiteButton = 3;  // Exit
int yellowButton = 4; // Shoot
int blueButton = 5;   // Skill
int redButton = 6;    // Pause
int greenButton = 7;  // Resume

void setup() {
  Serial.begin(9600);
  
  // Joystick button setup
  pinMode(SW, INPUT_PULLUP);

  // Button setup with pull-up resistors
  pinMode(whiteButton, INPUT_PULLUP);
  pinMode(yellowButton, INPUT_PULLUP);
  pinMode(blueButton, INPUT_PULLUP);
  pinMode(redButton, INPUT_PULLUP);
  pinMode(greenButton, INPUT_PULLUP);
}

void loop() {
  int xValue = analogRead(VRx);
  int yValue = analogRead(VRy);
  int buttonState = digitalRead(SW);

  int whiteState = digitalRead(whiteButton);
  int yellowState = digitalRead(yellowButton);
  int blueState = digitalRead(blueButton);
  int redState = digitalRead(redButton);
  int greenState = digitalRead(greenButton);

  // Map joystick values from 0-1023 to -1 to 1
  int mappedX = map(xValue, 0, 1023, -1, 1);
  int mappedY = map(yValue, 0, 1023, -1, 1);

  // Send joystick and button data over serial
  Serial.print(mappedX);
  Serial.print(",");
  Serial.print(mappedY);
  Serial.print(",");
  Serial.print(buttonState);
  Serial.print(",");
  Serial.print(whiteState);
  Serial.print(",");
  Serial.print(yellowState);
  Serial.print(",");
  Serial.print(blueState);
  Serial.print(",");
  Serial.print(redState);
  Serial.print(",");
  Serial.println(greenState);

  delay(100); // Delay to prevent flooding the serial port
}
