
import math
import random
import tkinter as tk
from tkinter import font as tkfont
from pathlib import Path

try:
    import pygame
except ImportError:
    pygame = None

W, H = 900, 800
BG = '#060208'

root = tk.Tk()
root.title('Love Heart ✨')

canvas = tk.Canvas(
    root, width=W, height=H,
    bg=BG, highlightthickness=0
)
canvas.pack()

PHRASES = [
    'I love you', 'Seni seviyorum', 'Te amo', "Je t’aime",
    'Ich liebe dich', 'Ti amo', 'Eu te amo', 'Я тебя люблю',
    '사랑해', '愛してる', '我爱你', 'मैं तुमसे प्यार करता हूँ',
    'Σ’ αγαπώ', 'Ik hou van jou', 'Jag älskar dig',
    'Kocham cię', 'ฉันรักเธอ', 'Anh yêu em',
    'Aku cinta kamu', 'Я тебе кохаю', 'Mahal kita',
    'Nakupenda', 'Te iubesc', 'Miluji tě',
    'Jeg elsker dig', 'Jeg elsker deg'
]

COLORS = [
    '#ff355e', '#ff729f', '#ffb3c6',
    '#ffd08a', '#d5a2ff', '#92cfff'
]

fonts = {
    size: tkfont.Font(
        root=root, family='Arial',
        size=size, weight='bold'
    )
    for size in (9, 10, 11, 12)
}

def screen(x, y):
    return W / 2 + x, H / 2 - y

def heart(a):
    return (
        16 * math.sin(a)**3 * 21,
        (
            13 * math.cos(a)
            - 5 * math.cos(2*a)
            - 2 * math.cos(3*a)
            - math.cos(4*a)
        ) * 21 + 20
    )

poly = [
    heart(2 * math.pi * i / 720)
    for i in range(720)
]

edges = list(zip(poly, poly[1:] + poly[:1]))

ymin = min(y for x, y in poly)
ymax = max(y for x, y in poly)

def spans(y):
    xs = []

    for (x1, y1), (x2, y2) in edges:
        if (y1 <= y < y2) or (y2 <= y < y1):
            xs.append(
                x1 + (y-y1)*(x2-x1)/(y2-y1)
            )

    xs.sort()
    return list(zip(xs[::2], xs[1::2]))

def build_words():
    words = []

    row_height = max(
        f.metrics('linespace')
        for f in fonts.values()
    ) + 4

    y = ymax - row_height / 2

    while y > ymin + row_height / 2:
        upper = spans(y + row_height / 2)
        lower = spans(y - row_height / 2)

        for a, b in upper:
            for c, d in lower:
                lo = max(a, c) + 4
                hi = min(b, d) - 4

                if hi - lo < 25:
                    continue

                x = lo + random.uniform(0, 8)
                line = []

                for _ in range(80):
                    candidates = [
                        (p, z, fonts[z].measure(p))
                        for p in random.sample(
                            PHRASES, len(PHRASES)
                        )
                        for z in random.sample(
                            list(fonts), len(fonts)
                        )
                    ]

                    fit = next(
                        (
                            (p, z, w)
                            for p, z, w in candidates
                            if x + w <= hi
                        ),
                        None
                    )

                    if fit is None:
                        break

                    p, z, w = fit
                    line.append([x+w/2, p, z, w])
                    x += w + 7

                if len(line) > 1:
                    extra = hi - (
                        line[-1][0] + line[-1][3]/2
                    )

                    for i, item in enumerate(line):
                        item[0] += (
                            extra*i/(len(line)-1)
                        )

                elif line:
                    line[0][0] = (lo+hi)/2

                for cx, p, z, w in line:
                    words.append((cx, y, p, z))

        y -= row_height

    random.shuffle(words)
    return words

words = build_words()
text_items = []
word_index = 0
fireworks = []
finale = False
finished = False

# ---------------- HEART ANIMATION ----------------

def spawn_word():
    global word_index, finished

    for _ in range(
        max(1, math.ceil(len(words)/150))
    ):
        if word_index >= len(words):
            break

        x, y, phrase, size = words[word_index]
        word_index += 1

        px, py = screen(x, y)

        item = canvas.create_text(
            px, py-30,
            text=phrase,
            font=fonts[size],
            fill='#16060b',
            tags='word'
        )

        text_items.append({
            'id': item,
            'x': px,
            'y': py,
            'age': 0,
            'color': random.choice([
                '#b70d28', '#d31a32',
                '#ec3047', '#ff5366'
            ])
        })

    for p in text_items[:]:
        p['age'] += 1
        k = min(1, p['age']/36)

        canvas.coords(
            p['id'],
            p['x'],
            p['y'] - 30*(1-(1-k)**3)
        )

        if k < .3:
            color = '#63101c'
        elif k < .7:
            color = '#ac1930'
        else:
            color = p['color']

        canvas.itemconfigure(
            p['id'], fill=color
        )

        if k >= 1:
            text_items.remove(p)

    if word_index < len(words) or text_items:
        root.after(35, spawn_word)

    elif not finished:
        finished = True
        root.after(450, grand_finale)
        root.after(200, shimmer)

# ---------------- FIREWORKS ----------------

def heart_point(a):
    return (
        16*math.sin(a)**3/18,
        (
            13*math.cos(a)
            - 5*math.cos(2*a)
            - 2*math.cos(3*a)
            - math.cos(4*a)
        )/18
    )

def burst(x=None, y=None, shape=None, power=1):
    if x is None:
        x = random.uniform(80, W-80)

    if y is None:
        y = random.uniform(80, H-80)

    if shape is None:
        shape = random.random() < .42

    base = random.choice(COLORS)
    particles = []
    n = 42

    for i in range(n):
        a = 2*math.pi*i/n

        if shape:
            dx, dy = heart_point(a)
            speed = random.uniform(
                2.3, 3.3
            ) * power
            vx, vy = dx*speed, -dy*speed

        else:
            speed = random.uniform(
                2.2, 4.0
            ) * power
            vx = math.cos(a)*speed
            vy = math.sin(a)*speed

        col = random.choice([
            base, base,
            '#ffe4ad', '#ffffff'
        ])

        dot = canvas.create_oval(
            x-2, y-2, x+2, y+2,
            fill=col,
            outline='',
            tags='firework'
        )

        trail = canvas.create_line(
            x, y, x, y,
            fill=col,
            width=2,
            tags='firework'
        )

        particles.append({
            'dot': dot,
            'trail': trail,
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy,
            'life': random.randint(35, 55),
            'color': col
        })

    fireworks.append(particles)

    # Fireworks stay behind the words.
    canvas.tag_lower('firework', 'word')

def tick_fireworks():
    for group in fireworks[:]:
        living = False

        for p in group:
            if p['life'] <= 0:
                continue

            living = True

            ox, oy = p['x'], p['y']

            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += .045
            p['vx'] *= .985
            p['life'] -= 1

            x, y = p['x'], p['y']

            canvas.coords(
                p['dot'],
                x-2, y-2, x+2, y+2
            )

            canvas.coords(
                p['trail'],
                ox, oy, x, y
            )

            if p['life'] < 15:
                canvas.itemconfigure(
                    p['dot'], fill='#532334'
                )
                canvas.itemconfigure(
                    p['trail'], fill='#351620'
                )

        if not living:
            for p in group:
                canvas.delete(p['dot'])
                canvas.delete(p['trail'])

            fireworks.remove(group)

    root.after(25, tick_fireworks)

def random_bursts():
    if not finale:
        burst()

        root.after(
            random.randint(500, 900),
            random_bursts
        )

def grand_finale():
    global finale
    finale = True

    for i in range(14):
        root.after(
            i*140,
            lambda i=i: burst(
                shape=(i % 2 == 0),
                power=1.3
            )
        )

    root.after(2600, after_finale)

def after_finale():
    burst()

    root.after(
        random.randint(750, 1300),
        after_finale
    )

# ---------------- SHIMMER ----------------

def shimmer():
    ids = canvas.find_withtag('word')

    if ids:
        item = random.choice(ids)
        old = canvas.itemcget(item, 'fill')

        canvas.itemconfigure(
            item, fill='#ffb9be'
        )

        root.after(
            180,
            lambda: canvas.itemconfigure(
                item, fill=old
            )
        )

    root.after(240, shimmer)

# ---------------- MUSIC ----------------

def music():
    path = (
        Path(__file__).resolve().parent
        / 'angel.mp3'
    )

    if pygame is None:
        print(
            'Install pygame-ce for music.'
        )
        return

    if not path.exists():
        print('Music not found:', path)
        return

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(.42)
        pygame.mixer.music.play(-1)

    except Exception as e:
        print('Music error:', e)

# ---------------- CLOSE WINDOW ----------------

def close():
    if pygame is not None:
        try:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception:
            pass

    root.destroy()

# ---------------- START PROGRAM ----------------

root.protocol('WM_DELETE_WINDOW', close)

music()

root.after(100, spawn_word)
root.after(250, random_bursts)
root.after(25, tick_fireworks)

root.mainloop()
