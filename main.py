#!/usr/bin/env python3
"""news-image-20261118 - Sum up Wednesday 18 November 2026 world news in one image.

Pure Python 3.13 standard library (zlib + struct + math only). Draws a
1024x1024 front-page style image with the day's six top stories: a
full-width lead story, a 2x2 grid of four stories, and a bottom strip.
Each story has a kicker, a big headline, a short subhead and a small
drawn scene. Deterministic: fixed constants, no clock, no randomness,
no network. Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Stories (as reported on 18 November 2026):
 1. US and Iran exchange fire: Iran drones target a US radar at the
    Sheikh Isa air base in Bahrain (intercepted); US jets hit an IRGC
    missile launch site on Qeshm Island. Third Bahrain attack in 5 days.
 2. Three tankers strike mines in the Strait of Hormuz; the LPG tanker
    Tara Gas is hit twice off Oman and catches fire; Kuwait reports
    drone attacks.
 3. Ukraine strikes the Crimean bridge for a second consecutive day;
    Russia pounds bridges in Kyiv.
 4. Trump lands in Manila for Quad talks ahead of his China visit;
    Xi, Trump and Putin are set to meet Thursday in Shenzhen.
 5. Canada and China extend trade deals as Xi meets Carney ahead of
    the APEC summit.
 6. MS Dhoni announces his retirement from the IPL and becomes the
    Chennai Super Kings mentor.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (248, 244, 232)
INK = (17, 17, 17)
WHITE = (255, 255, 255)
RED = (180, 35, 24)
BAND = (241, 237, 226)
GREY = (120, 116, 104)
NIGHT = (24, 32, 54)
SEA = (44, 110, 150)
SKY = (232, 236, 240)
ORANGE = (226, 88, 34)
GOLD = (255, 210, 0)

# 5x7 pixel font: each glyph is 7 rows, low 5 bits, bit 4 = leftmost pixel.
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x08, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    "-": (0, 0, 0, 0x0E, 0, 0, 0),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    "/": (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
}


class Canvas:
    """A plain RGB pixel buffer with tiny vector drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c, t=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
                if (r - t) * (r - t) <= d <= r * r:
                    self.set(xx, yy, c)

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        ymin = min(y0, y1, y2)
        ymax = max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay, bx, by) in ((x0, y0, x1, y1), (x1, y1, x2, y2),
                                    (x2, y2, x0, y0)):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by) or yy == ymax and yy == max(ay, by):
                    xs.append(ax + (bx - ax) * (yy - ay) / (by - ay))
            if len(xs) >= 2:
                for xx in range(int(min(xs)), int(max(xs)) + 1):
                    self.set(xx, yy, c)


def text_w(s, scale):
    return len(s) * 6 * scale


def draw_text(cv, x, y, s, scale, c):
    """Draw uppercase text; unknown chars render as blank."""
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits & (1 << (4 - col)):
                    cv.rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def draw_text_c(cv, x, y, w, s, scale, c):
    draw_text(cv, x + (w - text_w(s, scale)) // 2, y, s, scale, c)


def wrap(s, max_w, scale):
    """Greedy word wrap; returns a list of lines fitting max_w pixels."""
    lines = []
    for word in s.split(" "):
        if not lines:
            lines.append(word)
            continue
        trial = lines[-1] + " " + word
        if text_w(trial, scale) <= max_w:
            lines[-1] = trial
        else:
            lines.append(word)
    return lines


def starburst(cv, cx, cy, r, c):
    """12-spike explosion burst centred on (cx, cy)."""
    for k in range(12):
        ang = math.radians(k * 30)
        rr = r if k % 2 == 0 else r // 2
        x1 = cx + int(rr * math.cos(ang))
        y1 = cy + int(rr * math.sin(ang))
        cv.line(cx, cy, x1, y1, c, 3)
    cv.disc(cx, cy, r // 3, c)


def drone(cv, cx, cy, s, c):
    """A small quad drone: an X with four rotor dots."""
    cv.line(cx - s, cy - s, cx + s, cy + s, c, 2)
    cv.line(cx - s, cy + s, cx + s, cy - s, c, 2)
    cv.disc(cx - s, cy - s, 2, c)
    cv.disc(cx + s, cy - s, 2, c)
    cv.disc(cx - s, cy + s, 2, c)
    cv.disc(cx + s, cy + s, 2, c)


# ---------------------------------------------------------------- scenes
# Each scene draws inside the band (bx, by, w, h) it is given.

def scene_gulf(cv, bx, by, w, h, accent):
    # Night sky over a Gulf air base: radar tower, incoming drones,
    # an interception burst.
    cv.rect(bx, by, w, h, NIGHT)
    for (sx, sy) in ((30, 18), (120, 40), (210, 14), (300, 34)):
        cv.disc(bx + sx, by + sy, 2, WHITE)
    # Ground and base buildings.
    cv.rect(bx, by + h - 26, w, 26, (52, 58, 74))
    cv.rect(bx + 20, by + h - 52, 70, 26, (70, 78, 96))
    cv.rect(bx + 100, by + h - 44, 46, 18, (70, 78, 96))
    # Radar tower: mast, crossbar, dish.
    tx = bx + w // 2 - 90
    cv.vline(tx, by + 30, h - 56, WHITE, 5)
    cv.line(tx - 26, by + 34, tx + 26, by + 62, WHITE, 4)
    cv.line(tx + 26, by + 34, tx - 26, by + 62, WHITE, 4)
    cv.disc(tx, by + 48, 22, (190, 200, 214))
    cv.disc(tx, by + 48, 22, (190, 200, 214))
    cv.ring(tx, by + 48, 22, WHITE, 2)
    cv.line(tx, by + 48, tx + 40, by + 20, GOLD, 3)
    # Three drones sweeping in from the right, with trails.
    for (dx, dy, s) in ((w - 40, 30, 9), (w - 80, 62, 8), (w - 30, 92, 7)):
        cv.line(bx + dx + 16, by + dy, bx + dx + 52, by + dy - 8, GREY, 2)
        drone(cv, bx + dx, by + dy, s, WHITE)
    # Interception burst between tower and drones.
    starburst(cv, bx + w - 130, by + 52, 20, ORANGE)
    cv.disc(bx + w - 130, by + 52, 6, RED)


def scene_tanker(cv, bx, by, w, h, accent):
    # A tanker ablaze in the strait: sea, hull, containers, flames,
    # smoke and a spiked mine. Drawn for a short (48px) band.
    cv.rect(bx, by, w, h, (214, 228, 236))
    cv.rect(bx, by + h - 10, w, 10, SEA)
    cv.hline(bx, by + h - 10, w, WHITE, 2)
    # Containers sit on the deck, fully inside the band.
    cv.rect(bx + 48, by + 8, 30, 16, (200, 60, 40))
    cv.rect(bx + 84, by + 8, 30, 16, (40, 90, 160))
    cv.rect(bx + 120, by + 8, 30, 16, (220, 170, 40))
    # Hull, bow and funnel.
    cv.rect(bx + 30, by + 24, 200, 10, accent)
    cv.tri(bx + 230, by + 24, bx + 252, by + 24, bx + 230, by + 34,
           accent)
    cv.rect(bx + 30, by + 34, 224, 4, INK)
    cv.rect(bx + 254, by + 6, 8, 32, INK)
    # Flames over the deck and smoke above them.
    cv.tri(bx + 180, by + 8, bx + 172, by + 24, bx + 188, by + 24,
           ORANGE)
    cv.tri(bx + 196, by + 8, bx + 190, by + 24, bx + 202, by + 24,
           GOLD)
    cv.disc(bx + 168, by + 4, 4, GREY)
    cv.disc(bx + 186, by + 2, 5, GREY)
    # Spiked mine and a second fireball to the right.
    starburst(cv, bx + w - 90, by + h - 20, 10, INK)
    cv.disc(bx + w - 90, by + h - 20, 4, INK)
    starburst(cv, bx + w - 40, by + 10, 10, ORANGE)
    cv.disc(bx + w - 40, by + 10, 3, RED)
    draw_text(cv, bx + w - 130, by + 2, "X3", 2, RED)


def scene_bridge(cv, bx, by, w, h, accent):
    # A bridge hit again: sky, deck with a gap, two towers, a falling
    # span and a blast over the gap.
    cv.rect(bx, by, w, h, SKY)
    cv.rect(bx, by + h - 14, w, 14, SEA)
    cv.hline(bx, by + h - 26, w, INK, 4)
    cv.hline(bx, by + 12, w, INK, 2)
    cv.rect(bx + 50, by + 4, 8, h - 18, INK)
    cv.rect(bx + w - 140, by + 4, 8, h - 18, INK)
    cv.line(bx + 54, by + 4, bx + 110, by + h - 26, INK, 2)
    cv.line(bx + w - 136, by + 4, bx + w - 192, by + h - 26, INK, 2)
    # The gap in the deck and the span dropping into the sea.
    gx = bx + w // 2 - 22
    cv.rect(gx, by + h - 26, 44, 4, SKY)
    cv.line(gx + 2, by + h - 24, gx + 40, by + h - 8, accent, 5)
    starburst(cv, bx + w // 2, by + 12, 13, ORANGE)
    cv.disc(bx + w // 2, by + 12, 4, RED)
    # A second blast mark over the far tower.
    starburst(cv, bx + w - 110, by + 10, 9, ORANGE)


def scene_quad(cv, bx, by, w, h, accent):
    # Four flag poles: the Quad leaders meet in Manila.
    cv.rect(bx, by, w, h, (222, 232, 238))
    flags = (
        ((200, 40, 40), (255, 255, 255), (200, 40, 40)),   # US stripes
        ((255, 153, 51), (255, 255, 255), (19, 136, 8)),    # India
        ((255, 255, 255), (255, 255, 255), (188, 0, 45)),   # Japan
        ((0, 40, 104), (0, 40, 104), (0, 40, 104)),         # Australia
    )
    for i, bands in enumerate(flags):
        fx = bx + 30 + i * 106
        cv.vline(fx, by + 4, h - 8, INK, 3)
        for j, col in enumerate(bands):
            cv.rect(fx + 3, by + 6 + j * 9, 62, 9, col)
        cv.frame(fx + 3, by + 6, 62, 27, INK, 1)
    # Japan disc and Australia stars.
    cv.disc(bx + 30 + 2 * 106 + 34, by + 19, 7, (188, 0, 45))
    for (sx, sy) in ((8, 10), (52, 12), (30, 24)):
        cv.disc(bx + 30 + 3 * 106 + 3 + sx, by + 6 + sy, 2, WHITE)
    # A small skyline base under the flags.
    cv.rect(bx, by + h - 8, w, 8, INK)


def scene_trade(cv, bx, by, w, h, accent):
    # Two-way trade: containers, arrows both ways, and the two flags
    # as roundels.
    cv.rect(bx, by, w, h, BAND)
    cv.rect(bx + 24, by + h - 22, 90, 16, (200, 60, 40))
    cv.rect(bx + 24, by + h - 38, 90, 16, (40, 90, 160))
    cv.rect(bx + w - 114, by + h - 22, 90, 16, (220, 170, 40))
    cv.rect(bx + w - 114, by + h - 38, 90, 16, (14, 124, 107))
    # Arrows pointing both ways between the stacks.
    mid = by + 12
    cv.line(bx + 130, mid, bx + w - 130, mid, INK, 3)
    cv.tri(bx + w - 130, mid, bx + w - 148, mid - 6, bx + w - 148, mid + 6, INK)
    cv.line(bx + w - 130, mid + 14, bx + 130, mid + 14, INK, 3)
    cv.tri(bx + 130, mid + 14, bx + 148, mid + 8, bx + 148, mid + 20, INK)
    # Roundels: maple red for Canada, star red for China.
    cv.disc(bx + 52, by + 10, 12, (200, 40, 40))
    draw_text(cv, bx + 40, by + 3, "CA", 2, WHITE)
    cv.disc(bx + w - 64, by + 10, 12, (222, 41, 16))
    starburst(cv, bx + w - 64, by + 10, 8, GOLD)


def scene_cricket(cv, bx, by, w, h, accent):
    # Stumps, a bat mid-swing, a red ball and the number 7.
    cv.rect(bx, by, w, h, (210, 226, 190))
    cv.rect(bx, by + h - 10, w, 10, (90, 140, 70))
    # Stumps.
    for i in range(3):
        cv.vline(bx + 40 + i * 10, by + h - 44, 34, GOLD, 4)
    cv.hline(bx + 40, by + h - 46, 28, GOLD, 3)
    # Bat, angled up to the right.
    cv.line(bx + 110, by + h - 12, bx + 170, by + 8, (160, 110, 60), 10)
    cv.line(bx + 170, by + 8, bx + 196, by - 2, (120, 80, 40), 5)
    # Ball in flight and the number 7, clear of the bat's swing.
    cv.disc(bx + w - 60, by + 18, 9, RED)
    cv.ring(bx + w - 60, by + 18, 9, WHITE, 1)
    draw_text(cv, bx + w - 42, by + h - 40, "7", 4, INK)


LEAD = {
    "kicker": "GULF - CONFLICT", "color": (158, 43, 37),
    "head": ["US AND IRAN", "EXCHANGE FIRE"],
    "sub": "IRAN DRONES TARGET US RADAR IN BAHRAIN; US JETS HIT A MISSILE SITE ON QESHM ISLAND.",
    "scene": scene_gulf,
}

GRID = [
    {"kicker": "MIDDLE EAST - ENERGY", "color": (14, 124, 107),
     "head": ["TANKERS HIT", "IN THE STRAIT"],
     "sub": "THREE TANKERS STRIKE MINES; LPG TANKER TARA GAS HIT TWICE OFF OMAN.",
     "scene": scene_tanker},
    {"kicker": "EUROPE - CONFLICT", "color": (29, 78, 137),
     "head": ["BRIDGE HIT", "SECOND DAY"],
     "sub": "UKRAINE STRIKES THE CRIMEAN BRIDGE AGAIN; RUSSIA POUNDS BRIDGES IN KYIV.",
     "scene": scene_bridge},
    {"kicker": "ASIA - DIPLOMACY", "color": (158, 43, 37),
     "head": ["TRUMP LANDS", "IN MANILA"],
     "sub": "QUAD TALKS OPEN IN MANILA AHEAD OF TRUMP'S CHINA VISIT AND THURSDAY SUMMIT.",
     "scene": scene_quad},
    {"kicker": "TRADE - APEC", "color": (91, 74, 138),
     "head": ["CANADA-CHINA", "TRADE DEAL"],
     "sub": "OTTAWA AND BEIJING EXTEND TRADE DEALS AS XI MEETS CARNEY BEFORE APEC.",
     "scene": scene_trade},
]

STRIP = {
    "kicker": "SPORT - CRICKET", "color": (51, 65, 85),
    "head": "DHONI CALLS TIME ON IPL",
    "sub": "MS DHONI RETIRES FROM PLAYING AND BECOMES CHENNAI SUPER KINGS MENTOR.",
    "scene": scene_cricket,
}


# ---------------------------------------------------------------- layout

def build():
    cv = Canvas(W, H, PAPER)
    # Masthead.
    cv.hline(24, 16, 976, RED, 4)
    draw_text_c(cv, 0, 34, W, "THE WORLD IN ONE DAY", 6, INK)
    draw_text_c(cv, 0, 92, W, "WEDNESDAY 18 NOVEMBER 2026", 5, RED)
    cv.hline(24, 142, 976, RED, 4)
    # Lead story: full-width panel.
    px, py, pw, ph = 24, 158, 976, 258
    cv.rect(px, py, pw, ph, WHITE)
    cv.frame(px, py, pw, ph, INK, 2)
    cv.rect(px, py, pw, 34, LEAD["color"])
    draw_text(cv, px + 14, py + 7, LEAD["kicker"], 3, WHITE)
    draw_text(cv, px + 14, py + 46, LEAD["head"][0], 6, INK)
    draw_text(cv, px + 14, py + 92, LEAD["head"][1], 6, INK)
    sub = wrap(LEAD["sub"], 556, 2)
    draw_text(cv, px + 14, py + 150, sub[0], 2, INK)
    if len(sub) > 1:
        draw_text(cv, px + 14, py + 168, sub[1], 2, INK)
    if len(sub) > 2:
        draw_text(cv, px + 14, py + 186, sub[2], 2, INK)
    sx, sy = px + 600, py + 44
    cv.rect(sx, sy, 362, 200, NIGHT)
    cv.frame(sx, sy, 362, 200, GREY, 1)
    LEAD["scene"](cv, sx, sy, 362, 200, LEAD["color"])
    # Grid: 2 columns x 2 rows of 480 x 196 panels.
    for i, st in enumerate(GRID):
        px = 24 + (i % 2) * (480 + 16)
        py = 432 + (i // 2) * (196 + 16)
        cv.rect(px, py, 480, 196, WHITE)
        cv.frame(px, py, 480, 196, INK, 2)
        cv.rect(px, py, 480, 30, st["color"])
        draw_text(cv, px + 14, py + 6, st["kicker"], 3, WHITE)
        draw_text(cv, px + 12, py + 38, st["head"][0], 4, INK)
        draw_text(cv, px + 12, py + 66, st["head"][1], 4, INK)
        sub = wrap(st["sub"], 456, 2)
        draw_text(cv, px + 12, py + 100, sub[0], 2, INK)
        if len(sub) > 1:
            draw_text(cv, px + 12, py + 116, sub[1], 2, INK)
        bx, by = px + 14, py + 140
        cv.rect(bx, by, 452, 48, BAND)
        cv.frame(bx, by, 452, 48, GREY, 1)
        st["scene"](cv, bx, by, 452, 48, st["color"])
    # Bottom strip: the cricket story.
    px, py, pw, ph = 24, 856, 976, 84
    cv.rect(px, py, pw, ph, WHITE)
    cv.frame(px, py, pw, ph, INK, 2)
    cv.rect(px, py, 8, ph, STRIP["color"])
    draw_text(cv, px + 20, py + 12, STRIP["head"], 4, INK)
    sub = wrap(STRIP["sub"], 660, 2)
    draw_text(cv, px + 20, py + 48, sub[0], 2, INK)
    if len(sub) > 1:
        draw_text(cv, px + 20, py + 64, sub[1], 2, INK)
    sx, sy = px + 700, py + 10
    cv.rect(sx, sy, 262, 64, BAND)
    cv.frame(sx, sy, 262, 64, GREY, 1)
    STRIP["scene"](cv, sx, sy, 262, 64, STRIP["color"])
    # Footer.
    cv.hline(24, 956, 976, INK, 2)
    draw_text_c(cv, 0, 970, W,
                "SIX STORIES FROM ONE DAY - WEDNESDAY 18 NOVEMBER 2026", 2, INK)
    return cv


def png_bytes(cv):
    def chunk(kind, data):
        out = struct.pack(">I", len(data)) + kind + data
        out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 6))
            + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes, %dx%d)" % (path, len(data), W, H))


if __name__ == "__main__":
    main()
