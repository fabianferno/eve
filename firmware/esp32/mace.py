# Spiked mace smash animation for the GC9A01 round display.
import framebuf, math, random, time, gc, micropython
from array import array
from gc9a01 import GC9A01, rgb, W, H

GROUND = 176
PX, PY = 178.0, 128.0                 # pivot (grip)
LH = 85.0                             # pivot -> head centre
PHI_I = math.atan2(34, -78)           # head resting on the ground
PHI_R = PHI_I + math.radians(110)     # raised
BACK = math.radians(6)
IX, IY = 100, GROUND                  # impact point
T_LOOP, T_RAISE, T_HOLD, T_SWING = 3.0, 0.9, 1.25, 1.5
MARGIN = 16


def mixc(a, b, t):
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    return (int(a[0] + (b[0] - a[0]) * t), int(a[1] + (b[1] - a[1]) * t), int(a[2] + (b[2] - a[2]) * t))


def mix(a, b, t):
    return rgb(*mixc(a, b, t))


def ease_io(t):
    return t * t * (3 - 2 * t)


# ---- palette ----
SKY_TOP, SKY_HOR = (22, 18, 48), (96, 62, 112)
GR_TOP, GR_BOT, GR_EDGE = (98, 82, 66), (48, 40, 34), (140, 118, 92)
STEEL, STEEL_D, STEEL_L, HILITE = (150, 156, 168), (82, 88, 100), (196, 202, 214), (240, 244, 255)
WOOD, LEATHER, GOLD, GOLD_D = (122, 80, 44), (66, 42, 28), (212, 168, 64), (150, 112, 36)
DUST, CRACK, WHITE, FLASHY = (176, 154, 124), (34, 26, 22), (255, 255, 255), (255, 226, 120)
TRAIL_BG = (70, 50, 96)


def bg_row(y):
    if y < GROUND:
        return mixc(SKY_TOP, SKY_HOR, y / GROUND)
    if y == GROUND:
        return GR_EDGE
    return mixc(GR_TOP, GR_BOT, (y - GROUND) / (H - GROUND))


BG = array("H", [rgb(*bg_row(min(H - 1, max(0, y - MARGIN)))) for y in range(H + 2 * MARGIN)])
BGF = array("H", [rgb(*mixc(bg_row(min(H - 1, max(0, y - MARGIN))), WHITE, 0.55)) for y in range(H + 2 * MARGIN)])

# ---- pixel-art mace sprite (18x18 palette indices, 0 = transparent) ----
SPRITE = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x04\x03\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x04\x04\x04\x03\x03\x03\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x04\x05\x05\x03\x03\x03\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x04\x04\x05\x03\x03\x03\x02\x03\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x03\x03\x03\x03\x03\x02\x02\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x03\x03\x03\x02\x02\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x03\x03\x02\x02\x02\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\t\t\x01\x02\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\t\t\x01\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06\x07\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x07\x08\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x06\x07\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x07\x08\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x06\x07\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\n\n\x08\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\n\n\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
SN = 18
SPAL = array("H", [0] + [rgb(*c) for c in (
    (24, 22, 30),      # 1 outline
    (64, 66, 78),      # 2 head dark
    (104, 108, 122),   # 3 head mid
    (152, 158, 172),   # 4 head light
    (214, 220, 232),   # 5 highlight
    (226, 220, 196),   # 6 handle light
    (176, 166, 140),   # 7 handle mid
    (118, 108, 88),    # 8 handle dark
    (86, 160, 170),    # 9 collar
    (60, 62, 72),      # 10 pommel
)])
PIV_U, PIV_V = 2.5, 15.0            # grip texel
HEAD_U, HEAD_V = 13.0, 5.0          # head centre texel
AXIS = math.atan2(HEAD_V - PIV_V, HEAD_U - PIV_U)
SCALE = LH / math.sqrt((HEAD_U - PIV_U) ** 2 + (HEAD_V - PIV_V) ** 2)
C_CRACK = rgb(*CRACK)
SPRM = array("i", [0] * 12)

# ---- effects (deterministic) ----
random.seed(3)
DEBRIS = []
for _ in range(18):
    vx = random.uniform(-170, 170)
    vy = random.uniform(-300, -110)
    tl = (-vy + math.sqrt(vy * vy + 4 * 350 * 7)) / 700  # time until it lands on GROUND+3
    DEBRIS.append((vx, vy, tl, random.choice((2, 3, 3, 4, 5)),
                   rgb(*random.choice((GR_TOP, GR_EDGE, (120, 100, 80), (80, 66, 54))))))
PUFFS = [(random.uniform(-26, 26), random.uniform(-10, 2), random.uniform(-40, 40), random.uniform(4, 8))
         for _ in range(7)]
CRACKS = []
for k in range(6):
    side = -1 if k % 2 else 1
    pts = [(IX, IY + 1)]
    x, y = IX, IY + 1
    for _ in range(4):
        x += side * random.uniform(9, 20)
        y += random.uniform(0, 6)
        pts.append((x, min(y, H - 1)))
    CRACKS.append(pts)


def add_mace(ops, phi, ghost=None):
    ops.append(("s", phi - AXIS, -1 if ghost is None else ghost))


@micropython.viper
def raster(buf, prm, tex, pal):
    # nearest-neighbour rotated sprite blit via inverse mapping (16.16 fixed point)
    b = ptr16(buf); p = ptr32(prm); t = ptr8(tex); pl = ptr16(pal)
    x0 = p[0]; x1 = p[1]; y0 = p[2]; y1 = p[3]
    urow = p[4]; vrow = p[5]; A = p[6]; B = p[7]; C = p[8]; D = p[9]
    solid = p[10]; sn = p[11]
    hi = sn << 16
    y = y0
    while y < y1:
        u = urow; v = vrow
        i = y * 240 + x0
        x = x0
        while x < x1:
            if u >= 0 and u < hi and v >= 0 and v < hi:
                k = t[(v >> 16) * sn + (u >> 16)]
                if k != 0:
                    if solid >= 0:
                        b[i] = solid
                    else:
                        b[i] = pl[k]
            u += A; v += C; i += 1; x += 1
        urow += B; vrow += D
        y += 1


def blit_sprite(buf, rows, theta, solid, sx, dy):
    c, s = math.cos(theta), math.sin(theta)
    px, py = PX + sx, PY + dy
    xs = []; ys = []
    for u, v in ((0, 0), (SN, 0), (0, SN), (SN, SN)):
        du, dv = (u - PIV_U) * SCALE, (v - PIV_V) * SCALE
        xs.append(px + du * c - dv * s); ys.append(py + du * s + dv * c)
    x0 = max(0, int(min(xs)) - 1); x1 = min(W, int(max(xs)) + 2)
    y0 = max(0, int(min(ys)) - 1); y1 = min(rows, int(max(ys)) + 2)
    if x0 >= x1 or y0 >= y1:
        return
    dx = x0 + 0.5 - px; dyy = y0 + 0.5 - py
    p = SPRM; F = 65536
    p[0] = x0; p[1] = x1; p[2] = y0; p[3] = y1
    p[4] = int((PIV_U + (dx * c + dyy * s) / SCALE) * F)
    p[5] = int((PIV_V + (-dx * s + dyy * c) / SCALE) * F)
    p[6] = int(c / SCALE * F); p[7] = int(s / SCALE * F)
    p[8] = int(-s / SCALE * F); p[9] = int(c / SCALE * F)
    p[10] = solid; p[11] = SN
    raster(buf, p, SPRITE, SPAL)


def star(cx, cy, ro, ri, n, rot):
    pts = array("h", [0] * (4 * n))
    for k in range(2 * n):
        r = ro if k % 2 == 0 else ri
        a = rot + k * math.pi / n
        pts[2 * k] = int(cx + r * math.cos(a))
        pts[2 * k + 1] = int(cy + r * math.sin(a) * 0.8)
    return pts


def build(t):
    """Return (ops, shake_x, shake_y, flash) for animation time t."""
    ops = []
    sx = sy = 0
    flash = False
    if t < T_RAISE:
        phi = PHI_I + (PHI_R - PHI_I) * ease_io(t / T_RAISE)
    elif t < T_HOLD:
        phi = PHI_R + BACK * ease_io((t - T_RAISE) / (T_HOLD - T_RAISE))
    elif t < T_SWING:
        u = (t - T_HOLD) / (T_SWING - T_HOLD)
        phi = PHI_R + BACK - (PHI_R + BACK - PHI_I) * u * u * u
    else:
        d = t - T_SWING
        phi = PHI_I + (math.radians(7) * math.sin(d / 0.2 * math.pi) if d < 0.2 else 0)

    if t >= T_SWING:
        d = t - T_SWING
        if d < 0.3:
            amp = 7 * (1 - d / 0.3)
            sx = int(random.uniform(-amp, amp)); sy = int(random.uniform(-amp, amp))
        flash = d < 0.07
        # cracks: grow, then fade back into the ground
        if d < 1.3:
            f = min(1.0, d / 0.12)
            col = C_CRACK if d < 0.9 else mix(CRACK, GR_TOP, (d - 0.9) / 0.4)
            for pts in CRACKS:
                n = 1 + int(f * (len(pts) - 1) + 0.999)
                for i in range(n - 1):
                    x0, y0 = pts[i]; x1, y1 = pts[i + 1]
                    ops.append(("l", int(x0), int(y0), int(x1), int(y1), col))
                    ops.append(("l", int(x0), int(y0) + 1, int(x1), int(y1) + 1, col))
        # shockwave rings
        for delay, thick in ((0.0, 3), (0.09, 2)):
            dd = d - delay
            if 0 <= dd < 0.55:
                rx = int(14 + 240 * dd)
                ry = max(2, int(rx * 0.22))
                col = mix(WHITE, GR_TOP, dd / 0.55)
                for k in range(thick):
                    ops.append(("e", IX, IY + 2, rx - k, ry, col, False))
        # dust behind
        if d < 0.95:
            for ox, oy, vx, r0 in PUFFS:
                r = int(r0 + 24 * d)
                ops.append(("e", int(IX + ox + vx * d), int(IY + oy - 14 * d), r, int(r * 0.7),
                            mix(DUST, SKY_HOR, d / 0.95), True))

    # motion trail during the swing
    if T_HOLD + 0.08 < t < T_SWING + 0.05:
        for k in (3, 2, 1):
            ops_phi = phi + k * 0.2
            add_mace(ops, ops_phi, ghost=mix(STEEL, TRAIL_BG, 0.35 + 0.17 * k))
    add_mace(ops, phi)

    if t >= T_SWING:
        d = t - T_SWING
        # flying rock debris, settling as rubble
        if d < 1.35:
            for vx, vy, tl, sz, col in DEBRIS:
                tt = min(d, tl)
                x = IX + vx * tt
                y = IY - 4 + vy * tt + 350 * tt * tt
                ops.append(("r", int(x), int(y) - sz, sz, sz, col))
        # impact starburst
        if d < 0.16:
            k = d / 0.16
            ops.append(("p", star(IX, IY - 6, 46 * (1 - 0.4 * k), 16, 9, d * 4), mix(WHITE, FLASHY, k * 1.5)))
            ops.append(("e", IX, IY - 6, int(14 * (1 - k)) + 2, int(10 * (1 - k)) + 2, rgb(255, 255, 255), True))
    return ops, sx, sy, flash


@micropython.viper
def bg_fill(buf, bg, start: int, rows: int):
    b = ptr16(buf); s = ptr16(bg)
    y = 0
    while y < rows:
        c = s[start + y]
        i = y * 240; e = i + 240
        while i < e:
            b[i] = c
            i += 1
        y += 1


def run(seconds=0):
    lcd = GC9A01()
    gc.collect()
    buf = None
    for rows in (120, 80, 60, 40):
        try:
            buf = bytearray(W * rows * 2); break
        except MemoryError:
            gc.collect()
    fb = framebuf.FrameBuffer(buf, W, rows, framebuf.RGB565)
    print("strip rows", rows)
    t0 = time.ticks_ms(); last = t0; frames = 0
    while True:
        now = time.ticks_ms()
        t = (time.ticks_diff(now, t0) / 1000) % T_LOOP
        ops, sx, sy, flash = build(t)
        bg = BGF if flash else BG
        lcd.begin()
        for oy in range(0, H, rows):
            bg_fill(buf, bg, oy - sy + MARGIN, rows)
            dy = sy - oy
            for op in ops:
                k = op[0]
                if k == "p":
                    fb.poly(sx, dy, op[1], op[2], True)
                elif k == "e":
                    fb.ellipse(op[1] + sx, op[2] + dy, op[3], op[4], op[5], op[6])
                elif k == "l":
                    fb.line(op[1] + sx, op[2] + dy, op[3] + sx, op[4] + dy, op[5])
                elif k == "s":
                    blit_sprite(buf, rows, op[1], op[2], sx, dy)
                else:
                    fb.fill_rect(op[1] + sx, op[2] + dy, op[3], op[4], op[5])
            lcd.write(buf)
        lcd.end()
        frames += 1
        if time.ticks_diff(now, last) >= 3000:
            print("fps %.1f" % (frames * 1000 / time.ticks_diff(now, last)))
            frames = 0; last = now
        if seconds and time.ticks_diff(now, t0) > seconds * 1000:
            break
