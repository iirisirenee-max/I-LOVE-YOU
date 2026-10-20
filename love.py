
import math as m
import random as r
import tkinter.font as tkf
from pathlib import Path
import turtle as t

# Optional music: python -m pip install pygame-ce
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    pygame = None
    PYGAME_AVAILABLE = False


# -------------------- DESIGN --------------------

WIDTH = 800
HEIGHT = 800
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

FIREWORK_INTERVAL_MIN = 300
FIREWORK_INTERVAL_MAX = 750
PARTICLE_COUNT = 45
GRAND_FINALE_COUNT = 12

s = t.Screen()
s.setup(WIDTH, HEIGHT)
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
    "ฉันรักเธอ", "Anh yêu em", "Aku cinta kamu",
    "Я тебе кохаю", "Mahal kita", "Nakupenda", "Te iubesc",
    "Miluji tě", "Jeg elsker dig", "Jeg elsker deg",
]

FIREWORK_COLORS = [
    (1.00, 0.12, 0.22),
    (1.00, 0.32, 0.46),
    (1.00, 0.66, 0.72),
    (1.00, 0.72, 0.38),
    (0.92, 0.20, 0.38),
    (0.80, 0.38, 1.00),
    (0.45, 0.72, 1.00),
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
            lo = max(a[0], b[0])
            hi = min(a[1], b[1])

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
    row_h = max(
        font_for(z).metrics("linespace") for z in SIZES
    ) + 4

    half = row_h / 2
    placed = []
    y = YMAX - half

    while y > YMIN + half:
        row = intersect(
            spans(y + half),
            spans(y - half)
        )

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
                left = hi - (
                    line[-1][0] + line[-1][3] / 2
                )

                for i, item in enumerate(line):
                    item[0] += left * i / (len(line) - 1)
            else:
                line[0][0] = (lo + hi) / 2

            for i, (x, text, size, w) in enumerate(line):
                placed.append({
                    "x": x,
                    "y": y,
                    "text": text,
                    "size": size,
                    "edge": i == 0 or i == len(line) - 1,
                })

        y -= row_h

    wine = (0.58, 0.0, 0.09)
    crimson = (0.90, 0.05, 0.14)
    blood = (0.98, 0.10, 0.16)

    for p in placed:
        rad = min(1.0, math_dist(p["x"], p["y"]))
        base = mix(wine, crimson, 0.25 + 0.75 * rad)
        base = mix(
            base,
            blood,
            min(
                1.0,
                r.uniform(0, 0.35)
                + (0.3 if p["edge"] else 0)
            )
        )

        p["color"] = tuple(min(1, v) for v in base)
        p["rad"] = rad

    edges = [p for p in placed if p["edge"]]
    inner = [p for p in placed if not p["edge"]]

    edges.sort(
        key=lambda p: m.atan2(p["x"], p["y"] - CY) % (2 * m.pi)
    )
    inner.sort(
        key=lambda p: -p["rad"] + r.uniform(0, 0.08)
    )

    return edges + inner


# -------------------- ANIMATION STATE --------------------

BGC = tuple(
    int(BG[i:i + 2], 16) / 255 for i in (1, 3, 5)
)

main_ids = []
active = []
fireworks = []
finale_started = False
heart_finished = False


def clamp(v):
    return max(0.0, min(1.0, v))


def spawn(p):
    x, y = p["x"], -p["y"]
    size = p["size"]
    text = p["text"]
    color = p["color"]

    font = (FONT, size, "bold")
    big = (FONT, size + 1, "bold")

    shadow = cv.create_text(
        x + 2, y + 3, text=text, font=font, fill=BG
    )
    halo = cv.create_text(
        x, y, text=text, font=big, fill=BG
    )
    main = cv.create_text(
        x, y - LIFT, text=text, font=font, fill=BG
    )

    p.update({
        "shadow": shadow,
        "halo": halo,
        "main": main,
        "f": 0,
        "dx": r.uniform(-10, 10),
    })

    main_ids.append((main, color))
    active.append(p)


def math_sin(v):
    return m.sin(m.pi * v)


def animate(p):
    p["f"] += 1
    u = clamp(p["f"] / ANIM)
    e = 1 - (1 - u) ** 3

    color = p["color"]
    x, y = p["x"], -p["y"]
    hover = (1 - e) * LIFT
    px = x + p["dx"] * (1 - e)
    py = y - hover

    cv.itemconfig(
        p["shadow"],
        fill=hx(mix(BGC, dim(color, 0.30), e))
    )
    cv.itemconfig(
        p["halo"],
        fill=hx(mix(BGC, dim(color, 0.20), e * e))
    )
    cv.coords(p["halo"], px, py)

    flash = 0.75 * math_sin(clamp((u - 0.55) / 0.45))
    col = mix(mix(BGC, color, e ** 1.5), FLASH, flash)

    cv.itemconfig(p["main"], fill=hx(col))
    cv.coords(p["main"], px, py)

    if u >= 1:
        cv.coords(p["halo"], x, y)
        cv.coords(p["main"], x, y)
        cv.itemconfig(p["main"], fill=hx(color))
        return False

    return True



# -------------------- FIREWORKS --------------------

fireworks = []
finale_started = False
heart_finished = False

FIREWORK_COLORS = [
    "#ff3355", "#ff6688", "#ffc078",
    "#ffb6d9", "#d98cff", "#83cfff", "#ffffff"
]

PARTICLE_COUNT = 42
GRAND_FINALE_COUNT = 12

def heart_vector(a):
    x = 16 * (m.sin(a) ** 3)
    y = (
        13 * m.cos(a)
        - 5 * m.cos(2 * a)
        - 2 * m.cos(3 * a)
        - m.cos(4 * a)
    )
    length = m.hypot(x, y) or 1
    return x / length, y / length

def create_firework(x=None, y=None, heart_burst=None, scale=None):
    if x is None:
        x = r.uniform(-330, 330)
    if y is None:
        y = r.uniform(-300, 300)

    if heart_burst is None:
        heart_burst = r.random() < 0.45
    if scale is None:
        scale = r.uniform(0.8, 1.25)

    color = r.choice(FIREWORK_COLORS)

    # One dedicated Turtle draws each burst.
    pen = t.Turtle(visible=False)
    pen.speed(0)
    pen.penup()

    particles = []
    count = PARTICLE_COUNT

    for i in range(count):
        if heart_burst:
            dx, dy = heart_vector(2 * m.pi * i / count)
            speed = r.uniform(1.8, 3.6) * scale
        else:
            angle = 2 * m.pi * i / count
            dx = m.cos(angle)
            dy = m.sin(angle)
            speed = r.uniform(1.8, 3.6) * scale

        particles.append({
            "x": x,
            "y": y,
            "old_x": x,
            "old_y": y,
            "vx": dx * speed,
            "vy": dy * speed,
            "life": r.randint(35, 55),
            "maxlife": 55,
            "color": r.choice([color, color, "#ffe6a6", "#ffffff"]),
        })

    fireworks.append({
        "pen": pen,
        "particles": particles,
        "color": color,
        "age": 0,
    })

def update_fireworks():
    for fw in fireworks[:]:
        pen = fw["pen"]
        pen.clear()
        fw["age"] += 1
        alive = False

        for p in fw["particles"]:
            if p["life"] <= 0:
                continue

            alive = True

            p["old_x"] = p["x"]
            p["old_y"] = p["y"]

            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] -= 0.035

            p["vx"] *= 0.985
            p["vy"] *= 0.985
            p["life"] -= 1

            fade = p["life"] / p["maxlife"]

            # Draw a fading particle trail.
            pen.penup()
            pen.goto(p["old_x"], p["old_y"])
            pen.pendown()
            pen.pensize(max(1, 2 * fade))
            pen.pencolor(p["color"])
            pen.goto(p["x"], p["y"])
            pen.penup()

            # Draw the glowing particle.
            pen.goto(p["x"], p["y"])
            pen.dot(max(2, 5 * fade), p["color"])

        if not alive:
            pen.clear()
            pen.hideturtle()
            fireworks.remove(fw)

def firework_tick():
    update_fireworks()
    s.update()
    cv.after(25, firework_tick)

def random_firework_loop():
    if not finale_started:
        create_firework(
            heart_burst=(r.random() < 0.45),
            scale=r.uniform(0.8, 1.2)
        )

        cv.after(
            r.randint(350, 800),
            random_firework_loop
        )

def grand_finale():
    global finale_started

    if finale_started:
        return

    finale_started = True

    for i in range(GRAND_FINALE_COUNT):
        x = r.uniform(-300, 300)
        y = r.uniform(-260, 260)

        cv.after(
            i * 180,
            lambda x=x, y=y, i=i: create_firework(
                x=x,
                y=y,
                heart_burst=(i % 2 == 0),
                scale=r.uniform(0.9, 1.35)
            )
        )

    cv.after(2500, post_finale_fireworks)

def post_finale_fireworks():
    create_firework(
        x=r.uniform(-330, 330),
        y=r.uniform(-300, 300),
        heart_burst=(r.random() < 0.5),
        scale=r.uniform(0.75, 1.1)
    )

    cv.after(
        r.randint(500, 1100),
        post_finale_fireworks
    )

# -------------------- SHIMMER --------------------

def _safe(item_id, color):
    try:
        cv.itemconfig(item_id, fill=hx(color))
    except Exception:
        pass


def shimmer():
    if not main_ids:
        cv.after(140, shimmer)
        return

    item_id, color = r.choice(main_ids)

    _safe(item_id, mix(color, FLASH, 0.6))

    cv.after(
        260,
        lambda i=item_id, c=color: _safe(i, c)
    )
    cv.after(140, shimmer)


# -------------------- MUSIC --------------------

def start_music():
    if not PYGAME_AVAILABLE:
        print("Music skipped: install pygame-ce to enable music.")
        return

    audio_path = Path(__file__).resolve().parent / "angel.mp3"

    if not audio_path.is_file():
        print(f"Music file not found: {audio_path}")
        return

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(str(audio_path))
        pygame.mixer.music.set_volume(0.42)
        pygame.mixer.music.play(-1)
    except Exception as exc:
        print(f"Music error: {exc}")


# -------------------- HEART ANIMATION --------------------

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


# -------------------- SAFE EXIT --------------------

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


# -------------------- START --------------------

try:
    start_music()
    cv.create_oval(390, 390, 410, 410, fill="hotpink", outline="")
cv.create_text(400, 360, text="FIREWORK TEST", fill="white")

    # Start the heart, fireworks and particle animation.
    cv.after(200, step)
    cv.after(500, random_firework_loop)
    cv.after(16, firework_tick)

    s.getcanvas().winfo_toplevel().protocol(
        "WM_DELETE_WINDOW", close_app
    )

    t.done()

except (t.Terminator, Exception) as exc:
    print(f"Animation stopped: {exc}")
    close_app()
