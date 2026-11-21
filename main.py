"""The Daily Sum -- Saturday 21 November 2026 world news in one image.

A procedural newspaper front page drawn with the Python standard library
only. Every pixel is computed here; the PNG encoder is written by hand
with zlib and struct. Output is deterministic: two runs write identical
bytes. The program writes entry.png into MAKEFUN_OUTPUT_DIR.
"""

import math
import os
import struct
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (250, 244, 230)
INK = (18, 18, 22)
NAVY = (16, 32, 64)
GOLD = (198, 148, 42)
RED = (178, 34, 34)
TEAL = (14, 110, 110)
SKY = (135, 190, 225)
GREEN = (34, 120, 60)
GREY = (110, 110, 108)
LIGHT = (238, 232, 218)

# A 5 by 7 pixel font, drawn by hand. Each glyph is seven rows of five
# cells; '#' is ink and '.' is empty. Lowercase letters map to capitals.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
}

FONT.update({
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
})


def glyph(ch):
    """Return the 5x7 glyph for a character, uppercasing letters."""
    if "a" <= ch <= "z":
        ch = chr(ord(ch) - 32)
    return FONT.get(ch, FONT["?"])


class Canvas:
    """A plain RGB pixel buffer with small drawing helpers."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def put(self, x, y, colour):
        if 0 <= x < self.width and 0 <= y < self.height:
            base = (y * self.width + x) * 3
            self.pixels[base] = colour[0]
            self.pixels[base + 1] = colour[1]
            self.pixels[base + 2] = colour[2]

    def rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.put(xx, yy, colour)

    def frame(self, x, y, w, h, colour, thick=2):
        self.rect(x, y, w, thick, colour)
        self.rect(x, y + h - thick, w, thick, colour)
        self.rect(x, y, thick, h, colour)
        self.rect(x + w - thick, y, thick, h, colour)

    def hline(self, x0, x1, y, colour):
        if x1 < x0:
            x0, x1 = x1, x0
        for xx in range(x0, x1 + 1):
            self.put(xx, y, colour)

    def vline(self, x, y0, y1, colour):
        if y1 < y0:
            y0, y1 = y1, y0
        for yy in range(y0, y1 + 1):
            self.put(x, yy, colour)

    def line(self, x0, y0, x1, y1, colour):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.put(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                break
            step = 2 * err
            if step >= dy:
                err += dy
                x0 += sx
            if step <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, radius, colour):
        for yy in range(cy - radius, cy + radius + 1):
            span = int((radius * radius - (yy - cy) ** 2) ** 0.5)
            self.hline(cx - span, cx + span, yy, colour)

    def ellipse(self, cx, cy, rx, ry, colour):
        for yy in range(cy - ry, cy + ry + 1):
            frac = 1.0 - ((yy - cy) / ry) ** 2
            if frac < 0:
                continue
            span = int(rx * (frac ** 0.5))
            self.hline(cx - span, cx + span, yy, colour)

    def triangle(self, p0, p1, p2, colour):
        top = min(p0[1], p1[1], p2[1])
        bottom = max(p0[1], p1[1], p2[1])
        for yy in range(top, bottom + 1):
            xs = []
            for a, b in ((p0, p1), (p1, p2), (p2, p0)):
                if a[1] == b[1]:
                    continue
                low, high = (a, b) if a[1] < b[1] else (b, a)
                if low[1] <= yy <= high[1]:
                    t = (yy - low[1]) / (high[1] - low[1])
                    xs.append(int(low[0] + t * (high[0] - low[0])))
            if len(xs) >= 2:
                self.hline(min(xs), max(xs), yy, colour)


def chunk(kind, data):
    """One PNG chunk with its length, type, data and CRC."""
    body = kind + data
    return struct.pack(">I", len(data)) + body + struct.pack(
        ">I", zlib.crc32(body) & 0xFFFFFFFF
    )


def encode_png(canvas):
    """Encode the canvas as a deterministic PNG (filter 0, level 9)."""
    header = struct.pack(">IIBBBBB", canvas.width, canvas.height,
                         8, 2, 0, 0, 0)
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)
        start = y * stride
        raw += canvas.pixels[start:start + stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", header)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def text_width(text, scale):
    """Pixel width of a string at a given font scale."""
    return len(text) * 6 * scale - scale


def draw_text(canvas, text, x, y, scale, colour):
    """Draw a string left-aligned, one glyph cell of 6*scale per char."""
    cursor = x
    for ch in text:
        rows = glyph(ch)
        for row in range(7):
            for col in range(5):
                if rows[row][col] == "#":
                    canvas.rect(cursor + col * scale, y + row * scale,
                                scale, scale, colour)
        cursor += 6 * scale
    return cursor


def draw_centred(canvas, text, cx, y, scale, colour):
    draw_text(canvas, text, cx - text_width(text, scale) // 2, y, scale,
              colour)


def wrap_text(text, scale, max_width):
    """Greedy word wrap into lines that fit max_width pixels."""
    lines = []
    words = text.split(" ")
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paragraph(canvas, text, x, y, scale, colour, max_width, leading):
    """Draw a wrapped paragraph; return the y just below the last line."""
    for line in wrap_text(text, scale, max_width):
        draw_text(canvas, line, x, y, scale, colour)
        y += 7 * scale + leading
    return y


def kicker(canvas, text, x, y, colour):
    """A small coloured label with a rule underneath."""
    draw_text(canvas, text, x, y, 2, colour)
    canvas.rect(x, y + 18, text_width(text, 2), 3, colour)
    return y + 26


def draw_masthead(canvas):
    """Navy masthead with the paper name, date and a gold rule."""
    canvas.rect(0, 0, WIDTH, 148, NAVY)
    canvas.rect(0, 148, WIDTH, 5, GOLD)
    draw_centred(canvas, "THE DAILY SUM", WIDTH // 2, 22, 7, PAPER)
    draw_centred(canvas, "SATURDAY, 21 NOVEMBER 2026", WIDTH // 2, 100, 3,
                 GOLD)
    draw_text(canvas, "WORLD NEWS", 28, 112, 2, (170, 190, 215))
    right = "ONE DAY - ONE PAGE"
    draw_text(canvas, right, WIDTH - 28 - text_width(right, 2), 112, 2,
              (170, 190, 215))


def draw_missile_scene(canvas, x, y, w, h):
    """Night sky over Polish farmland: jets, a falling missile, a burst."""
    canvas.rect(x, y, w, h, (24, 38, 66))
    for sx, sy in ((30, 26), (120, 60), (210, 30), (290, 70), (70, 90),
                   (180, 110), (320, 40), (250, 130)):
        canvas.disc(x + sx, y + sy, 2, PAPER)
    canvas.disc(x + 300, y + 42, 16, (232, 226, 200))
    canvas.disc(x + 294, y + 36, 4, (200, 200, 190))
    # Farmland at the bottom.
    canvas.rect(x, y + h - 58, w, 58, (52, 84, 44))
    canvas.rect(x, y + h - 58, w, 4, (34, 58, 30))
    for fx in range(x + 12, x + w - 10, 46):
        canvas.line(fx, y + h - 58, fx - 8, y + h, (34, 58, 30))
    # A jet with a vapour trail.
    canvas.line(x + 30, y + 150, x + 150, y + 120, PAPER)
    canvas.triangle((x + 150, y + 112), (x + 178, y + 120),
                    (x + 150, y + 128), (200, 200, 200))
    canvas.line(x + 150, y + 120, x + 128, y + 138, (200, 200, 200))
    # The falling missile and its burst on the ground.
    canvas.line(x + 250, y + 30, x + 215, y + 150, (255, 190, 90))
    canvas.triangle((x + 208, y + 142), (x + 222, y + 142),
                    (x + 215, y + 162), (220, 220, 220))
    for ray in range(8):
        angle = ray * 0.785398
        dx = int(26 * math.cos(angle))
        dy = int(26 * math.sin(angle))
        canvas.line(x + 215, y + h - 58, x + 215 + dx, y + h - 58 + dy,
                    (255, 170, 40))
    canvas.disc(x + 215, y + h - 58, 14, (255, 200, 60))
    canvas.disc(x + 215, y + h - 58, 7, (255, 240, 160))


def draw_market_chart(canvas, x, y, w, h):
    """A falling market chart: red bars sliding down, one green stub."""
    canvas.rect(x, y, w, h, (246, 238, 222))
    canvas.frame(x, y, w, h, INK, 2)
    canvas.rect(x + 14, y + 14, w - 28, h - 28, PAPER)
    bars = (62, 58, 50, 44, 36, 26, 30, 20, 24, 12)
    step = (w - 40) // len(bars)
    base = y + h - 20
    for i, pct in enumerate(bars):
        tall = int((h - 40) * pct / 70)
        colour = GREEN if i == 6 else RED
        canvas.rect(x + 20 + i * step, base - tall, step - 6, tall, colour)
    canvas.line(x + 20, y + 16, x + w - 20, y + h - 28, RED)
    draw_text(canvas, "-3.7%", x + w - 86, y + 6, 2, RED)
    draw_text(canvas, "S&P 500", x + 16, y + h - 16, 2, INK)


def draw_globe(canvas, x, y, w, h):
    """A warming globe: blue sphere, green land, a rising red sun."""
    canvas.rect(x, y, w, h, (214, 232, 240))
    canvas.frame(x, y, w, h, INK, 2)
    radius = max(14, min(26, h // 2 - 4))
    cx, cy = x + w // 2, y + h // 2
    canvas.disc(cx + radius + 16, cy - radius - 4, 9, (255, 170, 40))
    canvas.disc(cx, cy, radius, (64, 130, 200))
    canvas.ellipse(cx - radius // 2, cy - radius // 3,
                   radius // 2, radius // 4, GREEN)
    canvas.ellipse(cx + radius // 3, cy + radius // 4,
                   radius // 3, radius // 5, GREEN)
    canvas.ellipse(cx - radius // 4, cy + radius // 2,
                   radius // 4, radius // 8, GREEN)
    draw_text(canvas, "+1.8C", x + 12, y + 6, 2, RED)


def draw_tankers(canvas, x, y, w, h):
    """Tankers queued on a strait at dusk, flags flying."""
    canvas.rect(x, y, w, h, (240, 196, 120))
    sea_h = max(16, h // 3)
    sea_top = y + h - sea_h
    canvas.rect(x, sea_top, w, sea_h, (28, 80, 120))
    canvas.line(x + 8, sea_top + 5, x + w - 8, sea_top + 8,
                (120, 170, 205))
    canvas.disc(x + w - 32, y + 14, 10, (255, 220, 130))
    ships = ((14, 1.0), (118, 0.8), (210, 1.0))
    for sx, size in ships:
        hull_w = int(76 * size)
        hull_h = 12
        top = sea_top - hull_h
        canvas.rect(x + sx, top, hull_w, hull_h, (40, 40, 44))
        canvas.rect(x + sx + 6, top - 10, int(22 * size), 10,
                    (200, 200, 200))
        canvas.vline(x + sx + 36, top - 20, top, INK)
        canvas.triangle((x + sx + 36, top - 20),
                        (x + sx + 36, top - 12),
                        (x + sx + 50, top - 16), RED)


def draw_chip(canvas, x, y, w, h):
    """A microchip with a human hand holding its reins: AI under control."""
    canvas.rect(x, y, w, h, (232, 236, 242))
    canvas.frame(x, y, w, h, INK, 2)
    half = max(12, min(22, h // 2 - 6))
    cx, cy = x + w // 2, y + h // 2
    for px in range(-1, 2):
        canvas.rect(cx + px * (half + 8) - 2, cy - half - 8, 4, 8, NAVY)
        canvas.rect(cx + px * (half + 8) - 2, cy + half, 4, 8, NAVY)
        canvas.rect(cx - half - 8, cy + px * (half + 8) - 2, 8, 4, NAVY)
        canvas.rect(cx + half, cy + px * (half + 8) - 2, 8, 4, NAVY)
    canvas.rect(cx - half, cy - half, half * 2, half * 2, NAVY)
    canvas.rect(cx - half + 5, cy - half + 5, half * 2 - 10, half * 2 - 10,
                GOLD)
    draw_text(canvas, "AI", cx - 6, cy - 7, 2, NAVY)
    draw_text(canvas, "HUMAN", x + 8, y + 5, 2, RED)
    draw_text(canvas, "IN CHARGE", x + 8, y + h - 17, 2, RED)


def draw_cricket(canvas, x, y, w, h):
    """A batsman, stumps and a ball sailing over the boundary rope."""
    canvas.rect(x, y, w, h, (196, 224, 170))
    canvas.frame(x, y, w, h, INK, 2)
    ground = y + h - 12
    canvas.rect(x, ground, w, 12, (120, 170, 100))
    # Stumps.
    for sx in range(3):
        canvas.vline(x + 26 + sx * 8, ground - 20, ground, (220, 180, 90))
    canvas.hline(x + 24, x + 44, ground - 22, (220, 180, 90))
    # The batsman: head, body, legs, bat.
    canvas.disc(x + 120, y + 14, 7, (120, 80, 50))
    canvas.line(x + 120, y + 21, x + 120, y + 38, (30, 60, 140))
    canvas.line(x + 120, y + 38, x + 106, ground, INK)
    canvas.line(x + 120, y + 38, x + 134, ground, INK)
    canvas.line(x + 120, y + 28, x + 148, y + 36, (30, 60, 140))
    canvas.line(x + 148, y + 36, x + 160, y + 48, (200, 170, 110))
    # The ball, high over the rope.
    canvas.disc(x + w - 34, y + 12, 6, RED)
    draw_text(canvas, "100", x + w - 56, y + 24, 2, RED)


def story_block(canvas, x, y, w, kicker_text, colour, headline, summary,
                scale_head=3):
    """Kicker, headline and summary stacked; return y below the summary."""
    y = kicker(canvas, kicker_text, x, y, colour)
    y = paragraph(canvas, headline, x, y, scale_head, INK, w, 4)
    y += 4
    y = paragraph(canvas, summary, x, y, 2, (52, 52, 52), w, 3)
    return y


def build_page():
    """Draw the whole front page and return the canvas."""
    page = Canvas(WIDTH, HEIGHT, PAPER)
    draw_masthead(page)

    # Lead story: Russian missiles land in Poland.
    lead_y = 168
    end = story_block(
        page, 24, lead_y, 576, "WAR IN EUROPE", RED,
        "MISSILES FALL ON POLAND",
        "Russian missiles crashed in south-east Poland during a huge "
        "overnight attack on Ukraine. Warsaw calls it a deliberate "
        "provocation. NATO chief Mark Rutte arrives in Warsaw today as "
        "Poland asks allies for more air defences.")
    draw_missile_scene(page, 620, lead_y, 380, 240)
    page.frame(24, 352, 576, 56, NAVY, 2)
    draw_text(page, "NO INJURIES IN POLAND - 8 KILLED IN UKRAINE",
              40, 368, 2, NAVY)
    draw_text(page, "THREE WEAPONS CAME DOWN IN POLISH FIELDS",
              40, 388, 2, (90, 90, 90))
    page.rect(24, 436, WIDTH - 48, 3, INK)

    # Second row: markets and the climate summit.
    row2 = 452
    story_block(page, 24, row2, 472, "MARKETS", RED,
                "WALL ST SLIDES INTO CORRECTION",
                "The S&P 500 fell 3.7% and the Nasdaq 5.3% in an AI "
                "sell-off. Nvidia slid 13.8% as the SEC examines its "
                "accounting.")
    draw_market_chart(page, 24, 620, 472, 70)
    story_block(page, 528, row2, 472, "CLIMATE", TEAL,
                "COP31 RUNS INTO OVERTIME",
                "Talks in Antalya missed their deadline as the draft deal "
                "dropped every mention of fossil fuels. A new text is "
                "promised on Saturday morning.")
    draw_globe(page, 528, 620, 472, 70)
    page.rect(24, 700, WIDTH - 48, 3, INK)

    # Third row: the Gulf, AI diplomacy and cricket.
    row3 = 714
    cols = ((24, "THE GULF", "IRAN TANKERS MASS AT KHARG",
             "Over 14 tankers gather at Kharg Island to test a US "
             "blockade.", draw_tankers),
            (356, "TECH DIPLOMACY", "HUMANS TO KEEP AI REINS",
             "Trump and Xi agree humans must stay in charge of military "
             "AI.", draw_chip),
            (688, "SPORT", "RAHUL COMPLETES SENA SET",
             "His Wellington century completes Test hundreds in all four "
             "SENA lands.", draw_cricket))
    for x, kick, head, summ, artist in cols:
        story_block(page, x, row3, 312, kick, NAVY, head, summ)
        artist(page, x, 858, 312, 58)
    page.rect(24, 926, WIDTH - 48, 3, INK)

    # Bottom ticker: the rest of the day in brief.
    page.rect(0, 936, WIDTH, 88, NAVY)
    draw_text(page, "ALSO TODAY", 24, 950, 2, GOLD)
    paragraph(page,
              "6.8 QUAKE SHAKES PERU - SAUDI STRIKES HIT HOUTHI TARGETS "
              "IN YEMEN - NEPAL PM HEADS TO DELHI ON FIRST FOREIGN TRIP",
              24, 972, 2, PAPER, WIDTH - 48, 3)
    return page


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    page = build_page()
    data = encode_png(page)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as handle:
        handle.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
