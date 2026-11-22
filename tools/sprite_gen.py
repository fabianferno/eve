"""Generate the 18x18 pixel-art mace sprite (palette indices) for firmware/esp32/mace.py and print an ASCII preview."""
N = 18
g = [[0] * N for _ in range(N)]
_set = lambda x, y, c: g[y + 1].__setitem__(x + 1, c)
# 1 outline, 2 head dark, 3 head mid, 4 head light, 5 highlight, 6 handle light, 7 handle mid,
# 8 handle dark, 9 collar, 10 pommel

# head: 6x6 block, shaded light top-left -> dark bottom-right
for y in range(1, 7):
    for x in range(9, 15):
        d = (x - 9) + (y - 1)
        _set(x, y, 4 if d <= 2 else (3 if d <= 6 else 2))
_set(10, 2, 5); _set(11, 2, 5); _set(10, 3, 5)
# knobs on each side
for x, y, c in ((11, 0, 4), (12, 0, 3), (15, 3, 3), (15, 4, 2), (11, 7, 2), (12, 7, 2), (8, 3, 4), (8, 4, 3)):
    _set(x, y, c)
# collar between head and handle
for x, y in ((8, 7), (7, 8), (8, 8), (9, 7)):
    _set(x, y, 9)
# handle: 2-thick diagonal staircase with segment bands
for i in range(6):
    a, b = 6 - i, 9 + i
    band = i % 2 == 1
    _set(a, b, 7 if band else 6)
    _set(a + 1, b, 8 if band else 7)
# pommel
for x, y in ((0, 15), (1, 15), (0, 14), (1, 14)):
    _set(x, y, 10)
# auto outline: transparent texels touching an opaque one
filled = [[g[y][x] != 0 for x in range(N)] for y in range(N)]
for y in range(N):
    for x in range(N):
        if not filled[y][x]:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                xx, yy = x + dx, y + dy
                if 0 <= xx < N and 0 <= yy < N and filled[yy][xx]:
                    g[y][x] = 1
                    break

chars = " #dmlHPQRcp"
for row in g:
    print("".join(chars[v] * 2 for v in row))
print("SPRITE =", bytes(v for row in g for v in row))
