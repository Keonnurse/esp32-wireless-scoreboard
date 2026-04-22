#include <SPI.h>
#include <DMD32.h>
#include "fonts/Arial_black_16.h"
#include <BLEDevice.h>
#include <BLEScan.h>
#include <BLEAdvertisedDevice.h>

#define DISPLAYS_ACROSS 1
#define DISPLAYS_DOWN 1

DMD dmd(DISPLAYS_ACROSS, DISPLAYS_DOWN);
hw_timer_t* timer = NULL;

volatile int scoreP1 = 0;
volatile int scoreP2 = 0;
volatile bool scoreChanged = true;

unsigned long lastP1Time = 0;
unsigned long lastP2Time = 0;
const unsigned long DEBOUNCE_MS = 800;

BLEScan* pBLEScan;

void IRAM_ATTR triggerScan() {
  dmd.scanDisplayBySPI();
}

void showScores() {
  dmd.clearScreen(true);
  dmd.selectFont(Arial_Black_16);

  char p1[4];
  char p2[4];
  sprintf(p1, "%d", scoreP1);
  sprintf(p2, "%d", scoreP2);

  // P1 on the left side
  if (scoreP1 >= 10) {
    dmd.drawChar(0, 0, p1[0], GRAPHICS_NORMAL);
    dmd.drawChar(8, 0, p1[1], GRAPHICS_NORMAL);
  } else {
    dmd.drawChar(4, 0, p1[0], GRAPHICS_NORMAL);
  }

  // P2 on the right side
  if (scoreP2 >= 10) {
    dmd.drawChar(17, 0, p2[0], GRAPHICS_NORMAL);
    dmd.drawChar(25, 0, p2[1], GRAPHICS_NORMAL);
  } else {
    dmd.drawChar(21, 0, p2[0], GRAPHICS_NORMAL);
  }
}

class MyAdvertisedDeviceCallbacks : public BLEAdvertisedDeviceCallbacks {
  void onResult(BLEAdvertisedDevice advertisedDevice) {
    String name = advertisedDevice.getName().c_str();
    unsigned long now = millis();

    if (name == "P1_SCORE") {
      if (now - lastP1Time > DEBOUNCE_MS) {
        scoreP1++;
        scoreChanged = true;
        lastP1Time = now;
        Serial.print("P1: "); Serial.print(scoreP1);
        Serial.print("  P2: "); Serial.println(scoreP2);
      }
    }
    if (name == "P2_SCORE") {
      if (now - lastP2Time > DEBOUNCE_MS) {
        scoreP2++;
        scoreChanged = true;
        lastP2Time = now;
        Serial.print("P1: "); Serial.print(scoreP1);
        Serial.print("  P2: "); Serial.println(scoreP2);
      }
    }
  }
};

void bleTask(void* parameter) {
  BLEDevice::init("");
  pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setActiveScan(true);
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99);

  while (true) {
    pBLEScan->start(1, false);
    pBLEScan->clearResults();
    vTaskDelay(50 / portTICK_PERIOD_MS);
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("Scoreboard starting...");

  timer = timerBegin(0, 80, true);
  timerAttachInterrupt(timer, &triggerScan, true);
  timerAlarmWrite(timer, 2000, true);
  timerAlarmEnable(timer);

  dmd.clearScreen(true);

  xTaskCreatePinnedToCore(
    bleTask, "BLE Task", 10000, NULL, 1, NULL, 0
  );
}

void loop() {
  if (scoreChanged) {
    scoreChanged = false;
    showScores();
  }
  delay(50);
}