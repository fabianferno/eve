"""Drive the MicroPython raw REPL to scan Wi-Fi and BLE on an ESP32."""
import serial, sys, time

PORT = sys.argv[1]

DEVICE_CODE = r'''
import network, bluetooth, time, ubinascii
print("=== WIFI ===")
w = network.WLAN(network.STA_IF); w.active(True)
print("sta_mac", ubinascii.hexlify(w.config("mac"), ":").decode())
nets = w.scan()
print("wifi_count", len(nets))
for n in sorted(nets, key=lambda x: -x[3])[:10]:
    print("  ch%2d rssi %4d  %s" % (n[2], n[3], n[0].decode() or "<hidden>"))
w.active(False)
print("=== BLE ===")
ble = bluetooth.BLE(); ble.active(True)
print("ble_mac", ubinascii.hexlify(ble.config("mac")[1], ":").decode())
seen = {}
done = [False]
def irq(ev, data):
    if ev == 5:  # _IRQ_SCAN_RESULT
        at, addr, adv_type, rssi, adv = data
        seen[bytes(addr)] = rssi
    elif ev == 6:  # _IRQ_SCAN_DONE
        done[0] = True
ble.irq(irq)
ble.gap_scan(8000, 30000, 30000)
t = time.ticks_ms()
while not done[0] and time.ticks_diff(time.ticks_ms(), t) < 10000:
    time.sleep_ms(100)
print("ble_count", len(seen))
for a, r in sorted(seen.items(), key=lambda x: -x[1])[:10]:
    print("  rssi %4d  %s" % (r, ubinascii.hexlify(a, ":").decode()))
ble.active(False)
print("=== DONE ===")
'''

s = serial.Serial(PORT, 115200, timeout=0.1)
s.dtr = False; s.rts = False
time.sleep(0.2); s.rts = True; time.sleep(0.1); s.rts = False  # reset
time.sleep(3); s.read(100000)

s.write(b"\r\x03\x03"); time.sleep(0.3)
s.write(b"\r\x01"); time.sleep(0.5)  # enter raw REPL
banner = s.read(10000)
if b"raw REPL" not in banner:
    print("Could not enter raw REPL. Got:", banner[-300:]); sys.exit(1)

s.write(DEVICE_CODE.encode() + b"\x04")
buf = b""; t = time.time()
while time.time() - t < 45:
    buf += s.read(4096)
    if b"=== DONE ===" in buf or b"Traceback" in buf and buf.endswith(b">"):
        time.sleep(0.3); buf += s.read(4096); break
s.write(b"\x02")  # back to normal REPL
print(buf.decode(errors="replace"))
