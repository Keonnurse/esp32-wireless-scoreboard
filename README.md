# ESP32 Wireless Ping-Pong Scoreboard

A three-device wireless scoreboard system built with ESP32 microcontrollers communicating over Bluetooth Low Energy (BLE). Two player buttons send score updates wirelessly to a central scoreboard display.

## System architecture

- **Scoreboard (receiver):** ESP32 wired to a P10 LED matrix panel, continuously scanning for BLE advertisements and updating the display when a player scores.
- **Player 1 button (sender):** ESP32 with a momentary button wired to GPIO 4. When pressed, the ESP32 broadcasts a BLE advertisement with the device name `P1_SCORE`.
- **Player 2 button (sender):** Identical to P1, but broadcasts `P2_SCORE`. Both buttons use the same firmware with a single `#define` changed at compile time.

The scoreboard increments the correct player's score based on which device name it sees in the advertisement.

## Why connectionless BLE?

Instead of pairing the buttons to the scoreboard over a persistent BLE connection, each button simply *advertises* its name when pressed. The scoreboard scans for advertisements and recognizes them by name.

This means:
- No pairing or connection state to manage.
- No reconnection logic when a device resets or goes out of range.
- Either button can be swapped, reset, or replaced without touching the scoreboard.
- Adding a third or fourth player unit in the future is trivial — just give it a new name.

For a scoreboard that needs to "just work" in the middle of a game, connectionless was the cleaner design.

## Handling the two-core problem

The scoreboard has to do two demanding things at the same time:
1. Continuously refresh the P10 LED matrix (the panel won't hold its own pixels — it needs to be scanned constantly or it goes dark).
2. Continuously scan for BLE advertisements from the buttons.

Doing both on one core caused the display to flicker and the ESP32 to crash with `Guru Meditation` errors — the hardware timer driving the display was being starved by BLE.

The fix:
- **Core 0** runs a FreeRTOS task pinned to it that handles BLE scanning.
- **Core 1** runs the main loop and a hardware timer interrupt (`IRAM_ATTR triggerScan`) that refreshes the P10 panel.
- A `volatile bool scoreChanged` flag lets the BLE task signal the main loop to redraw the display, but only when the score actually changes.

This eliminated both the flicker and the crashes.

## Hardware

- 3× ESP32 development boards (ELEGOO ESP32 Dev Modules)
- 1× P10 single-color LED matrix panel (32×16 pixels)
- 2× 19mm metal momentary push buttons with screw terminals
- Jumper wires (currently breadboarded — enclosures and soldered wiring are a future step)

## Software

- Written in C/C++ on the Arduino framework
- ESP32 Arduino core 1.0.6 (compatible with the timer API used)
- [DMD32](https://github.com/Qudor-Engineer/DMD32) library for driving the P10 panel
- Built-in ESP32 BLE libraries (`BLEDevice`, `BLEScan`, `BLEAdvertising`)
- Font: `Arial_Black_16` from DMD32

## Repository structure

```
.
├── Scoreboard/
│   └── Scoreboard.ino          # receiver firmware (BLE scan + display)
├── ButtonSender_P1/
│   └── ButtonSender_P1.ino     # player 1 button firmware
└── ButtonSender_P2/
    └── ButtonSender_P2.ino     # player 2 button firmware (same code, PLAYER = "P2_SCORE")
```

## What's working

- Three-device BLE communication end-to-end.
- Stable display refresh with no flicker during BLE scanning.
- Scores 0–9 display correctly for both players on the P10 panel.
- Software debouncing on the scoreboard (800 ms window) filters out rapid repeat advertisements from the same button press.

## Known issues and to-do

- **Double-digit scores don't display correctly.** `showScores()` draws only the first character when a score is ≥ 10, so 10 shows as "1", 20 shows as "2", etc. Fix: detect score length and draw both digits with adjusted x positions.
- **No reset function.** Scores can only be cleared by power-cycling the scoreboard. Planned fix: long-press on either button triggers a reset broadcast.
- **Single press sometimes counts as multiple increments.** The button broadcasts for 500 ms, and during that window the scoreboard's scanner can see the same advertisement multiple times. The 800 ms scoreboard-side debounce mostly handles this, but edge cases remain. Planned fix: use a non-blocking advertising window on the button side and/or include a rolling message ID in the advertisement.
- **Blocking `delay(500)` on the button side.** While advertising, the button is unresponsive — a rapid double-press can miss the second press. Planned fix: replace with a non-blocking `millis()` check.
- **No negative-scoring or correction gesture.** Original design called for double-tap = −1. Not yet implemented.
- **No deep sleep on the button units.** They run continuously on USB power. For battery operation, both senders need to sleep between presses and wake on GPIO interrupt.

## Next steps

1. Fix double-digit display rendering.
2. Implement reset and negative-score gestures on the sender firmware.
3. Add deep sleep to the button senders and wire up LiPo + TP4056 charging.
4. 3D print enclosures for the buttons and a frame for the P10 panel.
5. Solder permanent connections between the scoreboard ESP32 and the P10 panel.
