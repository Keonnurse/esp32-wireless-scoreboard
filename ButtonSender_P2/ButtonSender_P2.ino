#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

#define BUTTON_PIN 4  // GPIO pin your button is wired to
#define PLAYER "P2_SCORE"  

BLEAdvertising* pAdvertising;
bool buttonPressed = false;
bool lastButtonState = HIGH;

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  BLEDevice::init(PLAYER);
  pAdvertising = BLEDevice::getAdvertising();
  Serial.println("Button unit ready - " PLAYER);
}

void loop() {
  bool currentState = digitalRead(BUTTON_PIN);

  // Detect button press (LOW = pressed with INPUT_PULLUP)
  if (currentState == LOW && lastButtonState == HIGH) {
    Serial.println("Button pressed! Broadcasting...");
    pAdvertising->start();
    delay(500);  // Broadcast for 500ms
    pAdvertising->stop();
  }

  lastButtonState = currentState;
  delay(10);
}