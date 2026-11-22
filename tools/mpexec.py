"""Run a MicroPython snippet on the ESP32 via raw REPL (no reset). Usage: mpexec.py PORT FILE [timeout]"""
import serial, sys, time

port, path = sys.argv[1], sys.argv[2]
timeout = float(sys.argv[3]) if len(sys.argv) > 3 else 30
code = open(path).read()

s = serial.Serial()
s.port, s.baudrate, s.timeout = port, 115200, 0.1
s.dtr = False; s.rts = False  # set before open to avoid resetting the board
s.open()
time.sleep(0.3); s.read(100000)
s.write(b"\r\x03\x03"); time.sleep(0.3)
s.write(b"\r\x01"); time.sleep(0.5)
if b"raw REPL" not in s.read(10000):
    print("ERROR: could not enter raw REPL"); sys.exit(1)
s.write(code.encode() + b"\x04")
buf = b""; t = time.time()
while time.time() - t < timeout:
    buf += s.read(4096)
    if buf.count(b"\x04") >= 2:  # raw REPL: OK <stdout> \x04 <stderr> \x04
        break
s.write(b"\x02")
out = buf.decode(errors="replace")
if out.startswith("OK"): out = out[2:]
parts = out.split("\x04")
print(parts[0].strip())
if len(parts) > 1 and parts[1].strip():
    print("STDERR:", parts[1].strip())
