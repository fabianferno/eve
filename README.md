# eve

ESP32-based build. Parts list: [INVENTORY.md](INVENTORY.md).

## Layout

| Path | What |
|---|---|
| `firmware/esp32/gc9a01.py` | Minimal MicroPython driver for the 1.28" round GC9A01 display |
| `firmware/esp32/mace.py` | Pixel-art mace smash animation (flash, shockwave, cracks, debris, shake) |
| `firmware/esp32/main.py` | Autostart: runs the mace animation on boot |
| `firmware/esp32/tests/` | Hardware checks for the ISD1820 voice module |
| `tools/mpexec.py` | Run a MicroPython file on the board over the raw REPL |
| `tools/upload.py` | Copy a file onto the board's filesystem |
| `tools/radio_test.py` | Wi-Fi + BLE scan smoke test |
| `tools/sprite_gen.py` | Generates the mace sprite bytes used in `mace.py` |

## Board

ESP32-D0WD-V3 (WROOM-32), 4 MB flash, running MicroPython v1.29.0. Flash at 115200 baud;
460800 and above are unreliable on this board's USB-serial adapter.

## Wiring

| Device | Pin | ESP32 |
|---|---|---|
| GC9A01 display | VCC / GND | 3V3 / GND |
| | SCL / SDA | D18 / D23 |
| | CS / DC / RST | D21 / D22 / D4 |
| | BL (if present) | 3V3 |
| ISD1820 voice module | VCC / GND | VIN (5V) / GND |
| | REC / PLAYE / PLAYL / FT | D25 / D26 / D27 / D33 |

## Usage

```sh
pip install esptool pyserial
PORT=/dev/cu.usbserial-0001

# upload to the board
python tools/upload.py $PORT firmware/esp32/gc9a01.py gc9a01.py
python tools/upload.py $PORT firmware/esp32/mace.py mace.py
python tools/upload.py $PORT firmware/esp32/main.py main.py

# run something once (stops whatever is running first)
python tools/mpexec.py $PORT firmware/esp32/tests/isd1820_record_play.py 40
```
