# Component Inventory

| # | Component | Qty | Interface | Logic / Power | Notes |
|---|-----------|-----|-----------|---------------|-------|
| 1 | ISD1820 voice record/playback module (onboard mic + speaker) | 1 | Digital trigger pins (REC, PLAYE, PLAYL, FT) | 3.3–5V | ~10 s record time, standalone (no codec/I2S). ESP32 triggers via GPIO. Not suitable for streaming audio. |
| 2 | SG90 micro servo 9g | 2 | PWM (1 signal wire each) | 4.8–6V | Power from 5V rail, not the ESP32 3V3 pin. Share GND with ESP32. |
| 3 | ESP32 dev board (ESP-WROOM-32, SquadPixel) | 1 | WiFi, BT, SPI/I2C/UART/PWM | 3.3V logic | Main controller. Dual core. |
| 4 | 1.28" round TFT, GC9A01, 240x240 IPS (OceanLabz) | 1 | SPI | 3.3V | Good for an "eye"/face/gauge UI. |
| 5 | ST NUCLEO-G491RE (STM32G491RET6U) | 1 | SPI/I2C/UART/etc, onboard ST-LINK | 3.3V logic | Cortex-M4 @ 170 MHz, 512 KB flash, 128 KB RAM. Optional second MCU or co-processor. |
| 6 | 2.4" 240x320 TFT module (SPI) | 1 | SPI | 3.3V | Likely ILI9341 driver, verify from the back of the board. May have touch (XPT2046) and SD slot. |

## Open questions
- Is the 2.4" TFT's controller ILI9341 or ST7789? Does it have touch/SD pins?
- Which display is for the main UI: round GC9A01 or 2.4"?
- Is the NUCLEO in the build, or only a spare?

## Not in inventory yet (likely needed)
- Breadboard, jumper wires
- 5V supply or USB power for the servos
- Optional: I2S mic (INMP441) and amp (MAX98357A) if real audio is needed, since the ISD1820 can't stream
