# ESP32 Wireless Ping-Pong Scoreboard


<img width="200" height="267" alt="scoreboard-demo" src="https://github.com/user-attachments/assets/eb24efb0-4113-4301-8e6b-09717e2b3c53" /> <img width="200" height="267" alt="IMG_2350" src="https://github.com/user-attachments/assets/64202d5b-c638-4918-83a2-e8826a6aca97" /><img width="200" height="267" alt="IMG_3167 (1)" src="https://github.com/user-attachments/assets/2e24577c-931a-43d5-90a1-c2882931102d" /> <img width="360" height="267" alt="IMG_1653" src="https://github.com/user-attachments/assets/72dc5f18-df94-42b7-8166-03bd135e7363" />




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
- Adding a third or fourth player unit in the future is trivial: just give it a new name.

For a scoreboard that needs to "just work" in the middle of a game, connectionless was the cleaner design.

## Handling the two-core problem

The scoreboard has to do two demanding things at the same time:
1. Continuously refresh the P10 LED matrix (the panel won't hold its own pixels, so it needs to be scanned constantly or it goes dark).
2. Continuously scan for BLE advertisements from the buttons.

Doing both on one core caused the display to flicker and the ESP32 to crash with `Guru Meditation` errors. The hardware timer driving the display was being starved by BLE.

The fix:
- **Core 0** runs a FreeRTOS task pinned to it that handles BLE scanning.
- **Core 1** runs the main loop and a hardware timer interrupt (`IRAM_ATTR triggerScan`) that refreshes the P10 panel.
- A `volatile bool scoreChanged` flag lets the BLE task signal the main loop to redraw the display, but only when the score actually changes.

This eliminated both the flicker and the crashes.

## Hardware

- 3× ESP32 development boards (ELEGOO ESP32 Dev Modules)
- 1× P10 single-color LED matrix panel (32×16 pixels)
- 2× 19mm metal momentary push buttons with screw terminals
- Jumper wires (currently breadboarded, with enclosures and soldered wiring as a future step)

## Software

- Written in C/C++ on the Arduino framework
- ESP32 Arduino core 1.0.6 (compatible with the timer API used)
- [DMD32](https://github.com/Qudor-Engineer/DMD32) library for driving the P10 panel
- Built-in ESP32 BLE libraries (`BLEDevice`, `BLEScan`, `BLEAdvertising`)
- Font: `Arial_Black_16` from DMD32

## Enclosure and stand

Every printed part is a **parametric Fusion 360 Python script**. Dimensions live as tunable constants at the top of each file, so a part can be re-cut for a different panel or printer tolerance without redrawing anything.

<p align="center">
  <img src="docs/images/renders/01-scoreboard-enclosure-frame-cad.png" width="48%" alt="Scoreboard enclosure frame, Fusion 360 render">
</p>
  <img src="docs/images/renders/03-scoreboard-stand-bracket-cad.png" width="48%" alt="Scoreboard stand, Fusion 360 render">


| Part | Script | Notes |
|---|---|---|
| Stand | `cad/stand/stand.py` | Grooved cradle, 12° back tilt. Print two, one under each end of the frame |
| Left front panel | `cad/left_panel/left_panel.py` | Slotted side panel, printed front face down |
| Right cap | `cad/right_cap/right_cap.py` | Closed rounded end, widened 15.3 mm in v2 to close the measured seam gap |

To run one: in Fusion 360 go to **Utilities → Add-Ins → Scripts and Add-Ins**, click **+**, pick the part folder, then **Run**.

## Wiring

<p align="center">
  <img src="docs/images/wiring/05-esp32-to-p10-led-panel-wiring.png" width="46%" alt="ESP32 to P10 LED panel wiring">
  <img src="docs/images/wiring/04-power-system-lipo-tp4056-esp32.png" width="49%" alt="LiPo, TP4056 and ESP32 power system">
<img width="400" height="267" alt="RotatedIMG_3098" src="https://github.com/user-attachments/assets/893e3e7b-09cb-444a-b12f-5f5082d4092c" />
</p>

## Repository structure

```
.
├── Scoreboard/
│   └── Scoreboard.ino           # receiver: BLE scan + display
├── ButtonSender_P1/
│   └── ButtonSender_P1.ino      # player 1 button
├── ButtonSender_P2/
│   └── ButtonSender_P2.ino      # player 2 button (PLAYER = "P2_SCORE")
├── cad/
│   ├── stand/                   # Fusion 360
│   ├── left_half/               # Fusion 360
│   ├── right_cap/               # Fusion 360
│   └── button_enclosure/        # CadQuery + 3MF + STL
└── docs/images/
    ├── renders/                 # CAD renders
    ├── wiring/                  # wiring diagrams
    └── button/                  # button enclosure photos and renders
```

## What's working

- Three-device BLE communication end-to-end.
- Stable display refresh with no flicker during BLE scanning.
- Scores 0-99 display correctly for both players on the P10 panel, double digits included.
- Long press to reset the scoreboard to 0 - 0.
- Software debouncing on the scoreboard (800 ms window) filters out rapid repeat advertisements from the same button press.

## Known issues and to-do
- **No negative-scoring or correction gesture.** Original design called for double-tap = -1. Not yet implemented.
- **No deep sleep on the button units.** They run continuously on USB power. For battery operation, both senders need to sleep between presses and wake on GPIO interrupt.

## Next steps

1. Implement reset and negative-score gestures on the sender firmware.
2. Add deep sleep or on/off switches on the button.
3. 3D print enclosures for the buttons and a frame for the P10 panel.
4. Solder permanent connections between the scoreboard ESP32 and the P10 panel.
