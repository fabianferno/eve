# Minimal GC9A01 (240x240 round) driver. Wiring: SCL=D18 SDA=D23 CS=D21 DC=D22 RST=D4
from machine import Pin, SPI
import time

W = H = 240

_INIT = (
    (0xEF, b""), (0xEB, b"\x14"), (0xFE, b""), (0xEF, b""), (0xEB, b"\x14"),
    (0x84, b"\x40"), (0x85, b"\xFF"), (0x86, b"\xFF"), (0x87, b"\xFF"), (0x88, b"\x0A"),
    (0x89, b"\x21"), (0x8A, b"\x00"), (0x8B, b"\x80"), (0x8C, b"\x01"), (0x8D, b"\x01"),
    (0x8E, b"\xFF"), (0x8F, b"\xFF"), (0xB6, b"\x00\x20"), (0x36, b"\x08"), (0x3A, b"\x05"),
    (0x90, b"\x08\x08\x08\x08"), (0xBD, b"\x06"), (0xBC, b"\x00"), (0xFF, b"\x60\x01\x04"),
    (0xC3, b"\x13"), (0xC4, b"\x13"), (0xC9, b"\x22"), (0xBE, b"\x11"), (0xE1, b"\x10\x0E"),
    (0xDF, b"\x21\x0C\x02"), (0xF0, b"\x45\x09\x08\x08\x26\x2A"), (0xF1, b"\x43\x70\x72\x36\x37\x6F"),
    (0xF2, b"\x45\x09\x08\x08\x26\x2A"), (0xF3, b"\x43\x70\x72\x36\x37\x6F"), (0xED, b"\x1B\x0B"),
    (0xAE, b"\x77"), (0xCD, b"\x63"), (0x70, b"\x07\x07\x04\x0E\x0F\x09\x07\x08\x03"), (0xE8, b"\x34"),
    (0x62, b"\x18\x0D\x71\xED\x70\x70\x18\x0F\x71\xEF\x70\x70"),
    (0x63, b"\x18\x11\x71\xF1\x70\x70\x18\x13\x71\xF3\x70\x70"),
    (0x64, b"\x28\x29\xF1\x01\xF1\x00\x07"), (0x66, b"\x3C\x00\xCD\x67\x45\x45\x10\x00\x00\x00"),
    (0x67, b"\x00\x3C\x00\x00\x00\x01\x54\x10\x32\x98"), (0x74, b"\x10\x85\x80\x00\x00\x4E\x00"),
    (0x98, b"\x3E\x07"), (0x35, b""), (0x21, b""),
)


def rgb(r, g, b):
    """RGB888 -> RGB565, byte-swapped for use in a framebuf.RGB565 buffer."""
    c = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    return ((c & 0xFF) << 8) | (c >> 8)


class GC9A01:
    def __init__(self, sck=18, mosi=23, cs=21, dc=22, rst=4, baud=40_000_000):
        self.spi = SPI(2, baudrate=baud, polarity=0, phase=0, sck=Pin(sck), mosi=Pin(mosi))
        self.cs = Pin(cs, Pin.OUT, value=1)
        self.dc = Pin(dc, Pin.OUT, value=0)
        self.rst = Pin(rst, Pin.OUT, value=1)
        self.rst(0); time.sleep_ms(20); self.rst(1); time.sleep_ms(120)
        for c, d in _INIT:
            self.cmd(c, d)
        self.cmd(0x11); time.sleep_ms(120)
        self.cmd(0x29); time.sleep_ms(20)

    def cmd(self, c, data=b""):
        self.cs(0); self.dc(0); self.spi.write(bytes((c,)))
        if data:
            self.dc(1); self.spi.write(data)
        self.cs(1)

    def begin(self, x0=0, y0=0, x1=W - 1, y1=H - 1):
        """Open a window for pixel writes; call write() then end()."""
        self.cmd(0x2A, bytes((x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF)))
        self.cmd(0x2B, bytes((y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF)))
        self.cs(0); self.dc(0); self.spi.write(b"\x2C"); self.dc(1)

    def write(self, buf):
        self.spi.write(buf)

    def end(self):
        self.cs(1)
