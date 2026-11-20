#!/usr/bin/env python3
"""Build three 1024x1024 PNG variants summing up the world news of
Friday 20 November 2026. All text is drawn with PIL (DejaVu) so it
stays crisp; all artwork is drawn with PIL primitives. No network,
no AI-generated imagery.

Stories (all verified by web search on 20 Nov 2026, see NOTES.md):
 1. Cyclone Akvan landfall, Odisha, India (IMD)
 2. COP31 closes in Antalya, Turkiye (UNFCCC / press)
 3. Prabowo meets Xi in Shenzhen (ANTARA)
 4. The Hunger Games: Sunrise on the Reaping opens (Deadline)
 5. NZ v India 1st Test, Day 2, Wellington (Cricbuzz/Cricinfo)
 6. World Children's Day (UNICEF)
 7. Saturn close to the Moon tonight (astronomy listings)
 8. Canada sees little US movement on tariff relief (Reuters)
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
OUT = os.path.dirname(os.path.abspath(__file__))

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def F(path, size):
    return ImageFont.truetype(path, size)

def wrap(draw, text, font, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def para(draw, xy, text, font, fill, max_w, leading=None):
    x, y = xy
    leading = leading or int(font.size * 1.28)
    for line in wrap(draw, text, font, max_w):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y

def headline(draw, xy, text, font, fill, max_w, leading=None):
    return para(draw, xy, text, font, fill, max_w, leading)

def rule(draw, x0, y, x1, w=2, fill=(30, 30, 30)):
    draw.line([(x0, y), (x1, y)], fill=fill, width=w)

def badge(draw, cx, cy, r, num, fill, fg=(255, 255, 255)):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    f = F(SANS_B, int(r * 1.05))
    tw = draw.textlength(str(num), font=f)
    th = f.size
    draw.text((cx - tw / 2, cy - th / 2 - 1), str(num), font=f, fill=fg)

# ---------------------------------------------------------------- icons
def draw_cyclone(draw, cx, cy, R, col=(255, 255, 255), col2=(140, 200, 240)):
    """Spiral storm: concentric arcs rotating inward."""
    for i, r in enumerate(range(R, 8, -14)):
        a0 = i * 55
        a1 = a0 + 300
        draw.arc([cx - r, cy - r, cx + r, cy + r], a0, a1,
                 fill=col2 if i % 2 else col, width=9)
    draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=col)
    # rain streaks
    for k in range(10):
        ang = math.radians(k * 36 + 15)
        x0 = cx + int(math.cos(ang) * (R + 18))
        y0 = cy + int(math.sin(ang) * (R + 18))
        x1 = cx + int(math.cos(ang) * (R + 34))
        y1 = cy + int(math.sin(ang) * (R + 34))
        draw.line([(x0, y0), (x1, y1)], fill=col2, width=4)

def draw_globe(draw, cx, cy, R, sea=(18, 90, 140), land=(46, 160, 90)):
    draw.ellipse([cx - R, cy - R, cx + R, cy + R], fill=sea,
                 outline=(255, 255, 255), width=4)
    # abstract continents as blobs (stylised, not a real map)
    blobs = [
        (-0.52, -0.42, 0.34, 0.26), (-0.05, -0.55, 0.30, 0.20),
        (0.42, -0.30, 0.30, 0.34), (-0.35, 0.28, 0.42, 0.26),
        (0.30, 0.38, 0.26, 0.20), (-0.62, 0.05, 0.16, 0.30),
    ]
    for bx, by, bw, bh in blobs:
        draw.ellipse([cx + bx * R - bw * R, cy + by * R - bh * R,
                      cx + bx * R + bw * R, cy + by * R + bh * R], fill=land)
    # latitude lines
    for fy in (-0.5, 0.0, 0.5):
        yy = cy + fy * R
        half = int(math.sqrt(max(0.0, 1 - fy * fy)) * R)
        draw.arc([cx - half, yy - 14, cx + half, yy + 14], 180, 360,
                 fill=(255, 255, 255), width=2)
    # orbit ring
    draw.ellipse([cx - R - 26, cy - R - 26, cx + R + 26, cy + R + 26],
                 outline=(255, 255, 255), width=3)

def draw_moon_saturn(draw, cx, cy, R):
    # ringed planet + moon
    draw.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(232, 196, 120),
                 outline=(180, 140, 70), width=3)
    draw.ellipse([cx - R - 26, cy - 8, cx + R + 26, cy + 8],
                 outline=(240, 210, 150), width=6)
    draw.ellipse([cx + R + 34, cy - R - 30, cx + R + 66, cy - R + 2],
                 fill=(240, 240, 235))
    for sx, sy in [(cx - R - 40, cy - R + 10), (cx + R + 10, cy + R - 20),
                   (cx - 10, cy - R - 34)]:
        draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 255, 255))

def draw_film(draw, x, y, s):
    # film strip / clapper
    draw.rounded_rectangle([x, y, x + s, y + int(s * 0.72)], radius=8,
                           fill=(30, 30, 40), outline=(255, 255, 255), width=3)
    for i in range(4):
        fx = x + 10 + i * int(s / 4)
        draw.rectangle([fx, y + 8, fx + 14, y + 22], fill=(255, 255, 255))
        draw.rectangle([fx, y + int(s * 0.72) - 22, fx + 14,
                        y + int(s * 0.72) - 8], fill=(255, 255, 255))
    draw.ellipse([x + s // 2 - 16, y + int(s * 0.72) // 2 - 16,
                  x + s // 2 + 16, y + int(s * 0.72) // 2 + 16],
                 outline=(255, 200, 60), width=4)
    draw.polygon([(x + s // 2 - 6, y + int(s * 0.72) // 2 - 10),
                  (x + s // 2 - 6, y + int(s * 0.72) // 2 + 10),
                  (x + s // 2 + 12, y + int(s * 0.72) // 2)],
                 fill=(255, 200, 60))

def draw_cricket(draw, x, y, s):
    draw.ellipse([x, y, x + s, y + s], fill=(178, 34, 34),
                 outline=(120, 10, 10), width=3)
    draw.arc([x + 8, y + s * 0.28, x + s - 8, y + s * 0.72], 300, 60,
             fill=(255, 255, 255), width=3)
    draw.arc([x + 8, y + s * 0.28, x + s - 8, y + s * 0.72], 120, 240,
             fill=(255, 255, 255), width=3)
    # stumps
    bx = x + s + 14
    for k in range(3):
        draw.rectangle([bx + k * 12, y + 6, bx + k * 12 + 7, y + s - 6],
                       fill=(222, 184, 120))
    draw.rectangle([bx, y, bx + 32, y + 6], fill=(222, 184, 120))

# ---------------------------------------------------------------- stories
STORIES = [
    # (tag, headline, deck)
    ("INDIA · WEATHER", "Cyclone Akvan hits Odisha",
     "Landfall due near Gopalpur at noon; 105,000 people moved to shelters as winds reach 100 km/h."),
    ("TURKIYE · CLIMATE", "COP31 closes in Antalya",
     "Final day of the UN climate talks; adaptation finance still unsettled as the draft drops its $120bn target."),
    ("CHINA · DIPLOMACY", "Prabowo meets Xi in Shenzhen",
     "Indonesia's president holds bilateral talks with China's leader a day after APEC, then joins a business forum."),
    ("CULTURE", "Sunrise on the Reaping opens",
     "The new Hunger Games film reaches cinemas worldwide today, tracking a $160-190m opening weekend."),
    ("SPORT · CRICKET", "Nicholls 146* as NZ reach 317-6",
     "Day two of the first Test in Wellington; Glenn Phillips made 109 as New Zealand frustrated India."),
    ("WORLD", "World Children's Day",
     "UNICEF marks the day under the theme \u201cMy Day. My Rights. My Future.\u201d"),
    ("SPACE", "Saturn beside the Moon",
     "The ringed planet shines close to the Moon in tonight's sky."),
    ("NORTH AMERICA · TRADE", "Canada sees little US tariff relief",
     "Ottawa says Washington has offered little movement on easing tariffs, Reuters reports."),
]

NAVY = (13, 32, 61)
PAPER = (250, 246, 235)
INK = (22, 22, 22)
RED = (178, 34, 34)
TEAL = (10, 90, 110)

# ================================================================ VARIANT 1
# Newspaper front page: masthead + lead story + "also today" list.
def variant_v1():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # masthead band
    d.rectangle([0, 0, W, 148], fill=NAVY)
    d.text((512, 18), "THE WORLD", font=F(SERIF_B, 74),
           fill=(255, 255, 255), anchor="ma")
    d.text((512, 104), "FRIDAY 20 NOVEMBER 2026",
           font=F(SANS_B, 34), fill=(255, 214, 90), anchor="ma")
    d.text((40, 152), "ONE DAY  ·  ONE PAGE  ·  THE WORLD'S NEWS",
           font=F(SANS_B, 19), fill=RED)
    rule(d, 40, 182, 984, 3)

    # ---- lead story (left, top)
    lx, ly, lw = 40, 204, 560
    d.text((lx, ly), "INDIA  ·  WEATHER", font=F(SANS_B, 22), fill=RED)
    y = headline(d, (lx, ly + 34), "Cyclone Akvan hits India's east coast",
                 F(SERIF_B, 58), INK, lw, leading=62)
    y += 6
    y = para(d, (lx, y), "Severe Cyclonic Storm Akvan is due to cross the "
             "Odisha coast near Gopalpur around noon today, with sustained "
             "winds of 90-100 km/h. More than 105,000 people have already "
             "been moved to shelters.", F(SANS, 24), INK, lw, leading=31)
    # cyclone illustration panel
    py = y + 16
    d.rectangle([lx, py, lx + lw, py + 170], fill=(16, 60, 96))
    draw_cyclone(d, lx + 100, py + 85, 62)
    d.text((lx + 205, py + 42), "LANDFALL: TODAY, NOON",
           font=F(SANS_B, 23), fill=(255, 255, 255))
    d.text((lx + 205, py + 76), "NEAR GOPALPUR, ODISHA",
           font=F(SANS_B, 23), fill=(255, 214, 90))
    d.text((lx + 205, py + 110), "WINDS 90-100 KM/H",
           font=F(SANS, 21), fill=(220, 235, 245))
    lead_bottom = py + 170

    # ---- right column: the day at a glance (stories 2..5)
    rx, rw = 640, 344
    d.text((rx, ly), "THE DAY AT A GLANCE", font=F(SANS_B, 22), fill=NAVY)
    rule(d, rx, ly + 32, 984, 2, fill=NAVY)
    yy = ly + 48
    for i, (tag, head, _deck) in enumerate(STORIES[1:5], start=2):
        deck = SHORT_DECKS[i - 1]
        badge(d, rx + 18, yy + 16, 17, i, NAVY)
        d.text((rx + 46, yy - 2), tag, font=F(SANS_B, 17), fill=RED)
        yy = headline(d, (rx + 46, yy + 20), head, F(SERIF_B, 24),
                      INK, rw - 46, leading=28)
        yy = para(d, (rx + 46, yy + 2), deck, F(SANS, 17), (60, 60, 60),
                  rw - 46, leading=21) + 8
    glance_bottom = yy

    # ---- bottom band: remaining stories (6..8) in three columns
    by = max(lead_bottom, glance_bottom) + 12
    rule(d, 40, by, 984, 3)
    by += 14
    d.text((40, by), "ALSO TODAY", font=F(SANS_B, 21), fill=NAVY)
    by += 36
    col_w = 304
    for k, (tag, head, _deck) in enumerate(STORIES[5:8]):
        deck = SHORT_DECKS[5 + k]
        cx = 40 + k * (col_w + 16)
        badge(d, cx + 18, by + 16, 17, 6 + k, RED)
        d.text((cx + 46, by - 2), tag, font=F(SANS_B, 16), fill=RED)
        yy = headline(d, (cx + 46, by + 20), head, F(SERIF_B, 22),
                      INK, col_w - 46, leading=26)
        para(d, (cx + 46, yy + 2), deck, F(SANS, 17), (60, 60, 60),
             col_w - 46, leading=21)
    # footer
    fy = H - 38
    rule(d, 40, fy - 10, 984, 2)
    d.text((40, fy), "Sources: IMD  ·  Reuters  ·  ANTARA  ·  Deadline  ·  "
           "UNICEF  ·  UNFCCC  ·  Cricbuzz",
           font=F(SANS, 17), fill=(90, 90, 90))
    d.text((984, fy), "20 NOV 2026", font=F(SANS_B, 17), fill=(90, 90, 90),
           anchor="ra")
    img.save(os.path.join(OUT, "variant-v1.png"), optimize=True)
    return img

# Short decks (<=100 chars) for the tight globe variant list.
SHORT_DECKS = [
    "Landfall near Gopalpur at noon; 105,000 people in shelters.",
    "Final day in Antalya; adaptation finance still unsettled.",
    "Bilateral talks a day after APEC, then a business forum.",
    "In cinemas worldwide today; a $160-190m opening is tracked.",
    "Day two in Wellington; Phillips made 109 for the hosts.",
    "UNICEF theme: \u201cMy Day. My Rights. My Future.\u201d",
    "The ringed planet shines close to the Moon tonight.",
    "Ottawa says Washington offers little movement, Reuters reports.",
]

# ================================================================ VARIANT 2
# Globe + numbered story list.
def variant_v2():
    img = Image.new("RGB", (W, H), (12, 44, 78))
    d = ImageDraw.Draw(img)
    # top banner
    d.rectangle([0, 0, W, 132], fill=(8, 28, 54))
    d.text((512, 14), "THE WORLD IN ONE DAY", font=F(SERIF_B, 56),
           fill=(255, 255, 255), anchor="ma")
    d.text((512, 84), "FRIDAY 20 NOVEMBER 2026",
           font=F(SANS_B, 32), fill=(255, 214, 90), anchor="ma")
    # globe panel (left)
    draw_globe(d, 250, 400, 140)
    d.text((250, 585), "8 STORIES", font=F(SANS_B, 30),
           fill=(255, 255, 255), anchor="ma")
    d.text((250, 622), "4 CONTINENTS  ·  ONE DAY", font=F(SANS, 21),
           fill=(180, 210, 230), anchor="ma")
    d.text((250, 660), "STORM  ·  CLIMATE  ·  SPORT", font=F(SANS_B, 18),
           fill=(180, 210, 230), anchor="ma")
    d.text((250, 688), "SCREEN  ·  SPACE  ·  TRADE", font=F(SANS_B, 18),
           fill=(180, 210, 230), anchor="ma")
    # story list (right)
    lx, lw = 480, 504
    yy = 158
    for i, (tag, head, _deck) in enumerate(STORIES, start=1):
        deck = SHORT_DECKS[i - 1]
        badge(d, lx + 20, yy + 18, 19, i, (255, 214, 90), fg=NAVY)
        d.text((lx + 52, yy - 2), tag, font=F(SANS_B, 17), fill=(255, 214, 90))
        yy = headline(d, (lx + 52, yy + 20), head, F(SERIF_B, 24),
                      (255, 255, 255), lw - 52, leading=28)
        yy = para(d, (lx + 52, yy + 2), deck, F(SANS, 17),
                  (205, 225, 235), lw - 52, leading=21) + 8
    # footer
    rule(d, 40, H - 46, 984, 2, fill=(120, 150, 180))
    d.text((40, H - 36), "Sources: IMD  ·  Reuters  ·  ANTARA  ·  Deadline  ·  "
           "UNICEF  ·  UNFCCC  ·  Cricbuzz",
           font=F(SANS, 17), fill=(170, 195, 215))
    d.text((984, H - 36), "20 NOV 2026", font=F(SANS_B, 17),
           fill=(170, 195, 215), anchor="ra")
    img.save(os.path.join(OUT, "variant-v2.png"), optimize=True)
    return img

# ================================================================ VARIANT 3
# Magazine cover: big lead visual + cover lines + story strip.
def variant_v3():
    img = Image.new("RGB", (W, H), (10, 70, 80))
    d = ImageDraw.Draw(img)
    # masthead
    d.text((512, 22), "FRIDAY", font=F(SERIF_B, 84), fill=(255, 255, 255),
           anchor="ma")
    d.rectangle([212, 122, 812, 168], fill=(255, 214, 90))
    d.text((512, 130), "20 NOVEMBER 2026", font=F(SANS_B, 30),
           fill=NAVY, anchor="ma")
    d.text((512, 178), "THE WORLD'S NEWS IN ONE IMAGE",
           font=F(SANS_B, 20), fill=(200, 225, 235), anchor="ma")
    # lead visual: giant cyclone over a coastline strip
    draw_cyclone(d, 512, 430, 155)
    d.rectangle([0, 596, W, 656], fill=(16, 60, 96))
    d.text((512, 606), "INDIA BRACES AS AKVAN COMES ASHORE",
           font=F(SERIF_B, 32), fill=(255, 255, 255), anchor="ma")
    # cover lines
    yy = 672
    d.text((40, yy), "INSIDE TODAY", font=F(SANS_B, 22), fill=(255, 214, 90))
    yy += 36
    lines = [
        ("COP31 closes in Antalya", "climate talks end with the money fight open"),
        ("Prabowo meets Xi in Shenzhen", "a day after APEC, Indonesia and China talk business"),
        ("Sunrise on the Reaping opens", "the new Hunger Games film eyes a $160-190m weekend"),
        ("Nicholls 146* as NZ reach 317-6", "day two of the first Test in Wellington"),
    ]
    for head, deck in lines:
        d.text((40, yy), "\u25b8  " + head, font=F(SERIF_B, 26),
               fill=(255, 255, 255))
        yy += 32
        d.text((72, yy), deck, font=F(SANS, 19), fill=(200, 225, 235))
        yy += 28
    # also strip
    d.text((40, yy + 2), "ALSO:  World Children's Day  ·  Saturn beside the Moon  ·  "
           "Canada's tariff wait", font=F(SANS_B, 20), fill=(255, 214, 90))
    # footer
    rule(d, 40, H - 46, 984, 2, fill=(120, 170, 180))
    d.text((40, H - 36), "Sources: IMD  ·  Reuters  ·  ANTARA  ·  Deadline  ·  "
           "UNICEF  ·  UNFCCC  ·  Cricbuzz",
           font=F(SANS, 17), fill=(170, 205, 215))
    d.text((984, H - 36), "20 NOV 2026", font=F(SANS_B, 17),
           fill=(170, 205, 215), anchor="ra")
    img.save(os.path.join(OUT, "variant-v3.png"), optimize=True)
    return img

if __name__ == "__main__":
    for fn in (variant_v1, variant_v2, variant_v3):
        im = fn()
        print(fn.__name__, im.size)
    for name in ("variant-v1.png", "variant-v2.png", "variant-v3.png"):
        p = os.path.join(OUT, name)
        print(name, os.path.getsize(p), "bytes")
