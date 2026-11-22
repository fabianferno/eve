from machine import Pin
import time
PINS = {"REC": 25, "PLAYE": 26, "PLAYL": 27, "FT": 33}
for name, n in PINS.items():
    p = Pin(n, Pin.IN, Pin.PULL_UP); time.sleep_ms(20); up = p.value()
    p = Pin(n, Pin.IN, Pin.PULL_DOWN); time.sleep_ms(20); down = p.value()
    o = Pin(n, Pin.OUT, value=0); time.sleep_ms(5); low = o.value()
    print("%-5s D%-2d  pullup->%d  pulldown->%d  drive-low readback->%d" % (name, n, up, down, low))
print("all pins left driven LOW")
