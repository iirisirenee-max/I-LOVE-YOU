
import math as m
import random as r
import tkinter.font as tkf
from pathlib import Path
import turtle as t

# Optional music support: python -m pip install pygame-ce
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    PYGAME_AVAILABLE = False

# -------------------- DESIGN --------------------
SC = 21
OY = 20
DURATION = 10
TICK = 16
ANIM = 42
LIFT = 34
GAP = 7
SIZES = (9, 10, 11, 12)
FONT = "Arial"
BG = "#060208"

FIREWORK_INTERVAL_MIN = 700
FIREWORK_INTERVAL_MAX = 1700
PARTICLE_COUNT = 34
GRAND_FINALE_COUNT = 7

s = t.Screen()
s.setup(800, 800)
s.bgcolor(BG)
s.title("Love Heart")
s.tracer(0)

cv = s.getcanvas()
rng = r.Random()

PHRASES = [
    "I love you", "Seni seviyorum", "Te amo", "Je t'aime",
    "Ich liebe dich", "Ti amo", "Eu te amo", "Я тебя люблю",
    "사랑해", "愛してる", "我爱你", "मैं तुमसे प्यार करता हूँ",
    "Σ' αγαπώ", "Ik hou van jou", "Jag älskar dig", "Kocham cię",
    "ฉันรักเธอ", "Anh yêu em", "Aku cinta kamu", "Я тобі кохаю",
    "Mahal kita", "Nakupenda", "Te iubesc", "Miluji tě",
    "Jeg elsker dig", "Jeg elsker deg",
]

FIREWORK_COLORS = [
    (1.00, 0.12, 0.22),
    (1.00, 0.32, 0.46),
    (1.00, 0.66, 0.72),
    (1.00, 0.72, 0.38),
    (0.92, 0.20, 0.38),
]

FLASH = (1.0, 0.78, 0.78)
_fonts = {}

def font_for(size):
    if size not in _fonts:
        _fonts[size] = tkf.Font(
            root=cv, family=FONT, size=size, weight="bold"
        )
    return _fonts[size]

def heart(a):
    x = 16 * (m.sin(a) ** 3)
    y = (
        13 * m.cos(a)
        - 5 * m.cos(2 * a)
        - 2 * m.cos(3 * a)
        - m.cos(4 * a)
    )
    return x * SC, y * SC + OY

def hx(c):
    return "#%02x%02x%02x" % tuple(
        int(max(0, min(1, v)) * 255) for v in c
    )

def mix(a, b, k):
    k = max(0.0, min(1.0, k))
    return tuple(p + (q - p) * k for p, q in zip(a, b))

def dim(c, k):
    return tuple(v * k for v in c)

POLY = [heart(2 * m.pi * i / 720) for i in range(720)]
EDGES = list(zip(POLY, POLY[1:] + POLY[:1]))
YMAX = max(p[1] for p in POLY)
YMIN = min(p[1] for p in POLY)
CY = (YMAX + YMIN) / 2

def spans(y):
    xs = []
    for (x1, y1), (x2, y2) in EDGES:
        if (y1 <= y < y2) or (y2 <= y < y1):
            xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    xs.sort()
    return list(zip(xs[0::2], xs[1::2]))

def intersect(A, B):
    out = []
    for a in A:
        for b in B:
            lo, hi = max(a[0], b[0]), min(a[1], b[1])
            if hi - lo > 14:
                out.append((lo, hi))
    return out

def phrase_cycle():
    while True:
        order = PHRASES[:]
        rng.shuffle(order)
        yield from order

def math_dist(x, y):
    return m.hypot(x / (16 * SC), (y - CY) / (14.5 * SC))

def build():
    cycle = phrase_cycle()
    row_h = max(font_for(z).metrics("linespace") for z in SIZES) + 4
    half = row_h / 2
    placed = []
    y = YMAX - half

    while y > YMIN + half:
        row = intersect(spans(y + half), spans(y - half))

        for lo, hi in row:
            lo += 4
            hi -= 4
            cur = lo + rng.uniform(0, 8)
            line = []

            while True:
                fit = None
                for _ in range(12):
                    text = next(cycle)
                    size = rng.choice(SIZES)
                    w = font_for(size).measure(text)
                    if cur + w <= hi:
                        fit = (text, size, w)
                        break
                if not fit:
                    break

                text, size, w = fit
                line.append([cur + w / 2, text, size, w])
                cur += w + GAP

            if not line:
                continue

            if len(line) > 1:
                left = hi - (line[-1][0] + line[-1][3] / 2)
                for i, it in enumerate(line):
                    it[0] += left * i / (len(line) - 1)
            else:
                line[0][0] = (lo + hi) / 2

            for i, (x, text, size, w) in enumerate(line):
                edge = i == 0 or i == len(line) - 1
                placed.append(
                    dict(x=x, y=y, text=text, size=size, edge=edge)
                )

        y -= row_h

    wine = (0.58, 0.0, 0.09)
    crimson = (0.90, 0.05, 0.14)
    blood = (0.98, 0.10, 0.16)

    for p in placed:
        rad = min(1.0, math_dist(p["x"], p["y"]))
        base = mix(wine, crimson, 0.25 + 0.75 * rad)
        base = mix(
            base, blood,
            min(1.0, r.uniform(0, 0.35) + (0.3 if p["edge"] else 0))
        )
        p["color"] = tuple(min(1, v) for v in base)
        p["rad"] = rad

    edges = [p for p in placed if p["edge"]]
    inner = [p for p in placed if not p["edge"]]
    edges.sort(key=lambda p: m.atan2(p["x"], p["y"] - CY) % (2 * m.pi))
    inner.sort(key=lambda p: -p["rad"] + r.uniform(0, 0.08))
    return edges + inner

BGC = tuple(int(BG[i:i + 2], 16) / 255 for i in (1, 3, 5))
main_ids = []
active = []
fireworks = []
finale_started = False
heart_finished = False

def clamp(v):
    return max(0.0, min(1.0, v))

def spawn(p):
    x, y = p
