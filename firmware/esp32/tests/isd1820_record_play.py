from machine import Pin
import time
rec = Pin(25, Pin.OUT, value=0); playe = Pin(26, Pin.OUT, value=0)
Pin(27, Pin.OUT, value=0); Pin(33, Pin.OUT, value=0)
time.sleep(3)
print("REC on"); rec.value(1); time.sleep(5); rec.value(0); print("REC off")
time.sleep(1)
print("PLAYE pulse"); playe.value(1); time.sleep_ms(100); playe.value(0)
time.sleep(7)
print("done")
