#!/usr/bin/env python3
"""Compose the gta6-meme-x-01 meme: Vice City sunset, make.fun ghost as the
protagonist (its magenta disc = the setting sun), big Anton caption text.
Output: 1080x1080 JPEG (+ PNG)."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1080
random.seed(6)

# ---------- sky gradient ----------
stops = [
    (0.00, (24, 8, 51)),      # deep indigo
    (0.30, (76, 29, 149)),    # purple
    (0.52, (168, 28, 160)),   # magenta-purple
    (0.64, (236, 72, 153)),   # hot pink
    (0.72, (249, 115, 22)),   # orange
    (0.80, (253, 208, 71)),   # yellow near horizon
]
HORIZON = 690

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

img = Image.new("RGB", (W, H))
px = img.load()
for y in range(HORIZON):
    t = y / HORIZON
    for i in range(len(stops) - 1):
        if stops[i][0] <= t <= stops[i + 1][0]:
            f = (t - stops[i][0]) / (stops[i + 1][0] - stops[i][0])
            c = lerp(stops[i][1], stops[i + 1][1], f)
            break
    else:
        c = stops[-1][1]
    for x in range(W):
        px[x, y] = c

d = ImageDraw.Draw(img, "RGBA")

# stars in the upper sky
for _ in range(70):
    x = random.randint(20, W - 20)
    y = random.randint(15, 300)
    r = random.choice([1, 1, 2])
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, random.randint(90, 200)))

# birds
for bx, by, s in [(180, 180, 16), (230, 150, 12), (880, 210, 14), (830, 160, 10)]:
    d.arc([bx - s, by - s, bx, by + s], 200, 340, fill=(20, 6, 31, 220), width=3)
    d.arc([bx, by - s, bx + s, by + s], 200, 340, fill=(20, 6, 31, 220), width=3)

# ---------- ground ----------
d.rectangle([0, HORIZON, W, H], fill=(21, 8, 41))
# road: perspective trapezoid from horizon to bottom
d.polygon([(430, HORIZON), (650, HORIZON), (860, H), (220, H)], fill=(38, 16, 66))
# road edge lines
d.line([(430, HORIZON), (220, H)], fill=(255, 120, 200, 160), width=4)
d.line([(650, HORIZON), (860, H)], fill=(255, 120, 200, 160), width=4)
# dashed center line, growing with perspective
y = HORIZON + 12
while y < H - 30:
    frac = (y - HORIZON) / (H - HORIZON)
    wdt = int(3 + 9 * frac)
    ln = int(10 + 26 * frac)
    d.rectangle([540 - wdt // 2, y, 540 + wdt // 2, y + ln], fill=(253, 224, 71, 220))
    y += ln + int(14 + 34 * frac)
# neon horizon glow line
d.line([(0, HORIZON), (W, HORIZON)], fill=(255, 80, 180, 255), width=5)
d.line([(0, HORIZON + 5), (W, HORIZON + 5)], fill=(255, 80, 180, 90), width=10)

# ---------- palm trees ----------
def bezier(p0, p1, p2, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts

def palm(base_x, base_y, height, lean, scale=1.0, flip=False):
    top_x = base_x + lean
    top_y = base_y - height
    # trunk: tapered segments along a curve
    ctrl = (base_x + lean * 0.3, base_y - height * 0.55)
    pts = bezier((base_x, base_y), ctrl, (top_x, top_y), 20)
    for i in range(len(pts) - 1):
        wdt = max(3, int((14 - 11 * i / len(pts)) * scale))
        d.line([pts[i], pts[i + 1]], fill=(18, 6, 31), width=wdt)
    # fronds: long drooping blades, drawn as tapering curved strokes
    for k in range(7):
        base_ang = -168 + k * 28  # fan across the top
        ang = math.radians(base_ang)
        if flip:
            ang = math.radians(180 - base_ang)
        length = (165 + 45 * math.sin(k * 1.3)) * scale
        droop = (95 + 35 * math.cos(k * 0.9)) * scale
        # control point: out and slightly up; tip: out and drooped down
        p0 = (top_x, top_y)
        p1 = (top_x + math.cos(ang) * length * 0.55, top_y + math.sin(ang) * length * 0.45 - 30 * scale)
        p2 = (top_x + math.cos(ang) * length, top_y + math.sin(ang) * length * 0.45 + droop)
        pts = bezier(p0, p1, p2, 16)
        for i in range(len(pts) - 1):
            wdt = max(2, int((11 - 9 * i / len(pts)) * scale))
            d.line([pts[i], pts[i + 1]], fill=(18, 6, 31), width=wdt)
    # coconuts
    d.ellipse([top_x - 12, top_y + 2, top_x + 2, top_y + 16], fill=(18, 6, 31))
    d.ellipse([top_x + 2, top_y + 6, top_x + 16, top_y + 20], fill=(18, 6, 31))

palm(95, HORIZON + 6, 300, 70, scale=1.05)
palm(985, HORIZON + 6, 330, -80, scale=1.12, flip=True)

# ---------- the ghost (real mark) as the sun ----------
mark = Image.open("assets/mark-1024.png").convert("RGBA")
GHOST = 470
mark = mark.resize((GHOST, GHOST), Image.LANCZOS)
# soft glow behind the disc
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
gd.ellipse([540 - 330, 535 - 330, 540 + 330, 535 + 330], fill=(255, 190, 60, 70))
glow = glow.filter(ImageFilter.GaussianBlur(60))
img = Image.alpha_composite(img.convert("RGBA"), glow)
img.paste(mark, (540 - GHOST // 2, 535 - GHOST // 2), mark)
d = ImageDraw.Draw(img, "RGBA")

# ---------- caption text ----------
ANTON = "assets/Anton-Regular.ttf"

def text_center(y, s, size, stroke=9):
    f = ImageFont.truetype(ANTON, size)
    bbox = d.textbbox((0, 0), s, font=f, stroke_width=stroke)
    w = bbox[2] - bbox[0]
    d.text(((W - w) / 2 - bbox[0], y), s, font=f, fill=(255, 255, 255),
           stroke_width=stroke, stroke_fill=(10, 4, 20))

text_center(42, "WAITED 13 YEARS", 118)
text_center(168, "FOR GTA 6", 118)
text_center(798, "FIRST MISSION:", 96)
text_center(898, "DELETE 200GB OF GAMES", 80)

img.convert("RGB").save("meme.jpg", quality=94)
img.convert("RGB").save("meme.png")
print("saved /tmp/meme.jpg + /tmp/meme.png")
