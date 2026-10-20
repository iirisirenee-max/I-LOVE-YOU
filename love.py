
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
    x, y = p["x"], -p["y"]
    size, text, c = p["size"], p["text"], p["color"]
    font = (FONT, size, "bold")
    big = (FONT, size + 1, "bold")

    shadow = cv.create_text(x + 2, y + 3, text=text, font=font, fill=BG)
    halo = cv.create_text(x, y, text=text, font=big, fill=BG)
    main = cv.create_text(x, y - LIFT, text=text, font=font, fill=BG)

    p.update(
        shadow=shadow, halo=halo, main=main,
        f=0, dx=r.uniform(-10, 10)
    )
    main_ids.append((main, c))
    active.append(p)

def math_sin(v):
    return m.sin(m.pi * v)

def animate(p):
    p["f"] += 1
    u = clamp(p["f"] / ANIM)
    e = 1 - (1 - u) ** 3
    c = p["color"]
    x, y = p["x"], -p["y"]
    hover = (1 - e) * LIFT
    px = x + p["dx"] * (1 - e)
    py = y - hover

    cv.itemconfig(p["shadow"], fill=hx(mix(BGC, dim(c, 0.30), e)))
    cv.itemconfig(p["halo"], fill=hx(mix(BGC, dim(c, 0.20), e * e)))
    cv.coords(p["halo"], px, py)

    flash = 0.75 * math_sin(clamp((u - 0.55) / 0.45))
    col = mix(mix(BGC, c, e ** 1.5), FLASH, flash)
    cv.itemconfig(p["main"], fill=hx(col))
    cv.coords(p["main"], px, py)

    if u >= 1:
        cv.coords(p["halo"], x, y)
        cv.coords(p["main"], x, y)
        cv.itemconfig(p["main"], fill=hx(c))
        return False
    return True

# -------------------- FIREWORKS --------------------
def heart_vector(a):
    x = 16 * (m.sin(a) ** 3)
    y = (
        13 * m.cos(a)
        - 5 * m.cos(2 * a)
        - 2 * m.cos(3 * a)
        - m.cos(4 * a)
    )
    length = m.hypot(x, y) or 1
    return x / length, -y / length

def create_firework(x=None, y=None, heart_burst=None, scale=None):
    if x is None:
        x = r.uniform(-285, 285)
    if y is None:
        y = r.uniform(-260, 250)

    if heart_burst is None:
        heart_burst = r.random() < 0.38
    if scale is None:
        scale = r.uniform(0.72, 1.18)

    color = r.choice(FIREWORK_COLORS)
    count = r.randint(25, PARTICLE_COUNT)
    particles = []

    flash_id = cv.create_oval(
        x - 2, y - 2, x + 2, y + 2,
        fill=hx(color), outline=""
    )

    for i in range(count):
        if heart_burst:
            dx, dy = heart_vector(2 * m.pi * i / count)
            speed = r.uniform(1.5, 3.0) * scale
            speed *= r.uniform(0.84, 1.14)
        else:
            angle = 2 * m.pi * i / count + r.uniform(-0.12, 0.12)
            speed = r.uniform(1.3, 3.2) * scale
            dx, dy = m.cos(angle), m.sin(angle)

        particle_color = mix(
            color, (1.0, 0.88, 0.68), r.uniform(0, 0.35)
        )
        radius = r.choice((1.2, 1.5, 1.8, 2.1))
        dot = cv.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=hx(particle_color), outline=""
        )
        trail = cv.create_line(
            x, y, x, y,
            fill=hx(dim(particle_color, 0.55)),
            width=1, capstyle="round"
        )
        particles.append({
            "id": dot, "trail": trail, "x": x, "y": y,
            "vx": dx * speed, "vy": dy * speed,
            "life": r.randint(35, 56), "maxlife": 56,
            "color": particle_color, "radius": radius,
            "gravity": r.uniform(0.025, 0.055),
        })

    fireworks.append({"particles": particles, "flash": flash_id, "age": 0})

def update_fireworks():
    for fw in fireworks[:]:
        fw["age"] += 1
        if fw["age"] == 4:
            cv.delete(fw["flash"])

        alive = False
        for p in fw["particles"]:
            if p["life"] <= 0:
                cv.delete(p["id"])
                cv.delete(p["trail"])
                continue

            alive = True
            old_x, old_y = p["x"], p["y"]
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += p["gravity"]
            p["vx"] *= 0.987
            p["vy"] *= 0.987
            p["life"] -= 1

            cv.coords(p["trail"], old_x, old_y, p["x"], p["y"])
            cv.coords(
                p["id"],
                p["x"] - p["radius"], p["y"] - p["radius"],
                p["x"] + p["radius"], p["y"] + p["radius"]
            )

            fade = p["life"] / p["maxlife"]
            faded = dim(p["color"], max(0.08, fade))
            cv.itemconfig(p["id"], fill=hx(faded))
            cv.itemconfig(p["trail"], fill=hx(dim(faded, 0.58)))

        if not alive:
            cv.delete(fw["flash"])
            fireworks.remove(fw)

def random_firework_loop():
    if not finale_started:
        if r.random() < 0.66:
            create_firework()
        cv.after(
            r.randint(FIREWORK_INTERVAL_MIN, FIREWORK_INTERVAL_MAX),
            random_firework_loop
        )

def grand_finale():
    global finale_started
    if finale_started:
        return
    finale_started = True

    for i in range(GRAND_FINALE_COUNT):
        x = r.uniform(-235, 235)
        y = r.uniform(-205, 185)
        cv.after(
            i * 210,
            lambda x=x, y=y, i=i: create_firework(
                x=x, y=y, heart_burst=(i % 2 == 0),
                scale=r.uniform(0.85, 1.18)
            )
        )
    cv.after(2400, post_finale_fireworks)

def post_finale_fireworks():
    if r.random() < 0.5:
        create_firework(
            x=r.uniform(-275, 275),
            y=r.uniform(-245, 225),
            heart_burst=(r.random() < 0.45),
            scale=r.uniform(0.65, 0.95)
        )
    cv.after(r.randint(1900, 3100), post_finale_fireworks)

def _safe(i, c):
    try:
        cv.itemconfig(i, fill=hx(c))
    except Exception:
        pass

def shimmer():
    if not main_ids:
        cv.after(140, shimmer)
        return
    i, c = r.choice(main_ids)
    _safe(i, mix(c, FLASH, 0.6))
    cv.after(260, lambda i=i, c=c: _safe(i, c))
    cv.after(140, shimmer)

# -------------------- MUSIC --------------------
def start_music():
    if not PYGAME_AVAILABLE:
        print("Music skipped: run python -m pip install pygame-ce")
        return

    audio_path = Path(__file__).resolve().parent / "angel.mp3"
    if not audio_path.is_file():
        print(f"Music error: audio file not found: {audio_path}")
        return

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(str(audio_path))
        pygame.mixer.music.set_volume(0.42)
        pygame.mixer.music.play(-1)
    except Exception as exc:
        print(f"Music error: {exc}")

ORDER = build()
items = iter(ORDER)
RATE = len(ORDER) / (DURATION * 1000 / TICK)
acc = 0.0
spawning = True

def step():
    global spawning, acc, heart_finished

    if spawning:
        acc += RATE
        try:
            while acc >= 1:
                acc -= 1
                spawn(next(items))
        except StopIteration:
            spawning = False

    active[:] = [p for p in active if animate(p)]

    if not spawning and not active:
        if not heart_finished:
            heart_finished = True
            cv.after(500, grand_finale)
        shimmer()
        return

    cv.after(TICK, step)

def close_app():
    try:
        if PYGAME_AVAILABLE:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
    except Exception:
        pass
    try:
        s.bye()
    except Exception:
        pass

try:
    start_music()
    cv.after(200, step)
    cv.after(650, random_firework_loop)
    cv.after(16, firework_tick)
    s.getcanvas().winfo_toplevel().protocol("WM_DELETE_WINDOW", close_app)
    t.done()
except (t.Terminator, Exception):
    close_app()
