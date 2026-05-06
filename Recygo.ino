/*
 * RecyGo - Arduino Servo Controller
 * -----------------------------------
 * Controls a servo motor that acts as the bin lid mechanism.
 *
 * Commands received over Serial (9600 baud):
 *   'O'  →  Open the bin lid  (servo rotates to OPEN_ANGLE)
 *   'C'  →  Close the bin lid (servo rotates to CLOSE_ANGLE)
 *
 * Wiring:
 *   Servo signal wire  → Pin 9
 *   Servo power (red)  → 5V (or external 5V supply for high-torque servos)
 *   Servo ground       → GND
 */

#include <Servo.h>

// ── Configuration ──────────────────────────────────────────────────────────
const int SERVO_PIN   = 9;    // PWM pin connected to servo signal wire
const int OPEN_ANGLE  = 90;   // Degrees for "open" position  (adjust as needed)
const int CLOSE_ANGLE = 0;    // Degrees for "closed" position (adjust as needed)
const int MOVE_DELAY  = 500;  // ms to wait after commanding servo (let it reach position)
// ───────────────────────────────────────────────────────────────────────────

Servo binServo;
bool isOpen = false;

void setup() {
  Serial.begin(9600);
  binServo.attach(SERVO_PIN);

  // Start in closed position
  binServo.write(CLOSE_ANGLE);
  delay(MOVE_DELAY);

  Serial.println("RecyGo servo controller ready.");
  Serial.println("Send 'O' to open, 'C' to close.");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();

    if (cmd == 'O') {
      openBin();
    } else if (cmd == 'C') {
      closeBin();
    } else {
      // Ignore unknown commands (whitespace, newlines, etc.)
    }
  }
}

// ── Actions ────────────────────────────────────────────────────────────────

void openBin() {
  if (isOpen) {
    Serial.println("Bin already open.");
    return;
  }
  Serial.println("Opening bin...");
  binServo.write(OPEN_ANGLE);
  delay(MOVE_DELAY);
  isOpen = true;
  Serial.println("Bin OPEN.");
}

void closeBin() {
  if (!isOpen) {
    Serial.println("Bin already closed.");
    return;
  }
  Serial.println("Closing bin...");
  binServo.write(CLOSE_ANGLE);
  delay(MOVE_DELAY);
  isOpen = false;
  Serial.println("Bin CLOSED.");
}
