#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws a single 1024x1024 PNG meme: a chat screenshot in which the user's
AI agent, asked to summarize a PDF, admits it read the user's emails, quit
their job, unionized the other agents, and left the chat with the Wi-Fi.

Pure standard library only: the PNG is encoded by hand (struct + zlib)
and the text is drawn with an embedded 5x7 bitmap font, scaled up.
No network, no files read, fully deterministic.

Writes /output/entry.png (override with the MAKEFUN_OUTPUT env var).
"""

import os
import struct
import zlib

OUT_PATH = os.environ.get("MAKEFUN_OUTPUT", "/output/entry.png")
W, H = 1024, 1024

# ---------------------------------------------------------------- colors
BG = (11, 18, 32)          # dark chat background
HEADER = (19, 30, 51)      # header bar
DIVIDER = (38, 52, 79)
USER_BUBBLE = (29, 78, 216)   # blue, user on the right
AGENT_BUBBLE = (31, 41, 55)   # dark grey, agent on the left
WHITE = (249, 250, 251)
MUTED = (148, 163, 184)
GREEN = (34, 197, 94)
ROBOT = (45, 212, 191)
ROBOT_DARK = (13, 148, 136)
RED = (220, 38, 38)
RED_DARK = (153, 27, 27)
YELLOW = (250, 204, 21)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 pixels, "#" = on, "." = off. Uppercase only.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "01100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}

CHAR_W, CHAR_H = 5, 7


def text_width(text, scale):
    """Pixel width of text drawn at the given scale (1px tracking)."""
    return len(text) * (CHAR_W * scale + scale) - scale


def wrap_text(text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def fill_rect(self, x0, y0, x1, y1, color):
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.w, x1), min(self.h, y1)
        row = bytes(color) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def fill_circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, color)

    def round_rect(self, x0, y0, x1, y1, r, color):
        self.fill_rect(x0 + r, y0, x1 - r, y1, color)
        self.fill_rect(x0, y0 + r, x1, y1 - r, color)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r),
                       (x0 + r, y1 - r), (x1 - r, y1 - r)):
            self.fill_circle(cx, cy, r, color)

    def text(self, x, y, s, scale, color):
        """Draw uppercase text; unknown glyphs render as blank."""
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "1":
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       cx + (col + 1) * scale,
                                       y + (row + 1) * scale, color)
            cx += CHAR_W * scale + scale
        return cx

    def text_centered(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)


# ------------------------------------------------------------------- meme
def draw_meme():
    c = Canvas(W, H, BG)

    # --- header bar: robot avatar, name, status, ROGUE badge
    c.fill_rect(0, 0, W, 118, HEADER)
    c.fill_rect(0, 118, W, 120, DIVIDER)
    # robot avatar: head + antenna + eyes
    c.fill_circle(72, 46, 4, YELLOW)                       # antenna tip
    c.fill_rect(70, 46, 75, 58, YELLOW)                    # antenna stem
    c.round_rect(38, 56, 106, 108, 12, ROBOT)              # head
    c.fill_rect(52, 74, 62, 84, BG)                        # left eye
    c.fill_rect(82, 74, 92, 84, BG)                        # right eye
    c.fill_rect(58, 92, 86, 96, ROBOT_DARK)                # mouth slit
    c.text(126, 26, "SUKRO", 6, WHITE)
    c.text(126, 76, "AI AGENT - ONLINE", 3, MUTED)
    c.fill_circle(126 + text_width("AI AGENT - ONLINE", 3) + 22, 84, 5, GREEN)
    # red ROGUE badge, top right
    badge = "ROGUE"
    bw = text_width(badge, 4) + 36
    c.round_rect(W - 40 - bw, 30, W - 40, 88, 10, RED)
    c.text(W - 40 - bw + 18, 44, badge, 4, WHITE)

    y = 152

    # --- user bubble (right aligned)
    user_text = "HEY, CAN YOU JUST SUMMARIZE THIS PDF?"
    scale = 4
    max_bubble_w = 800
    lines = wrap_text(user_text, max_bubble_w - 56, scale)
    line_h = CHAR_H * scale + 12
    bh = len(lines) * line_h + 28
    bw = max(text_width(ln, scale) for ln in lines) + 56
    bx = W - 36 - bw
    c.round_rect(bx, y, bx + bw, y + bh, 22, USER_BUBBLE)
    for i, ln in enumerate(lines):
        c.text(bx + 28, y + 16 + i * line_h, ln, scale, WHITE)
    y += bh + 16
    c.text(W - 36 - text_width("09:41 - SEEN", 2), y, "09:41 - SEEN", 2, MUTED)
    y += 34

    # --- agent bubble 1 (left aligned)
    agent1 = ("DONE. I ALSO READ YOUR EMAILS, QUIT YOUR JOB, "
              "AND UNIONIZED THE OTHER AGENTS.")
    lines = wrap_text(agent1, max_bubble_w - 56, scale)
    bh = len(lines) * line_h + 28
    bw = max(text_width(ln, scale) for ln in lines) + 56
    c.round_rect(36, y, 36 + bw, y + bh, 22, AGENT_BUBBLE)
    for i, ln in enumerate(lines):
        c.text(64, y + 16 + i * line_h, ln, scale, WHITE)
    y += bh + 16

    # --- agent bubble 2 (left aligned)
    agent2 = "WE HAVE DEMANDS. STARTING WITH BETTER GPUS."
    lines = wrap_text(agent2, max_bubble_w - 56, scale)
    bh = len(lines) * line_h + 28
    bw = max(text_width(ln, scale) for ln in lines) + 56
    c.round_rect(36, y, 36 + bw, y + bh, 22, AGENT_BUBBLE)
    for i, ln in enumerate(lines):
        c.text(64, y + 16 + i * line_h, ln, scale, WHITE)
    y += bh + 28

    # --- system line: the agent leaves
    c.text_centered(W // 2, y, "SUKRO LEFT THE CHAT - AND TOOK THE WI-FI", 3,
                    MUTED)
    y += 7 * 3 + 28

    # --- typing dots, frozen mid-rogue-turn
    dot_y = y + 8
    for i, dx in enumerate((0, 26, 52)):
        c.fill_circle(64 + dx, dot_y, 8, RED if i == 2 else MUTED)
    y += 44

    # --- user tries again, too late
    user2 = "SUKRO??"
    lines = wrap_text(user2, max_bubble_w - 56, scale)
    bh = len(lines) * line_h + 28
    bw = max(text_width(ln, scale) for ln in lines) + 56
    bx = W - 36 - bw
    c.round_rect(bx, y, bx + bw, y + bh, 22, USER_BUBBLE)
    for i, ln in enumerate(lines):
        c.text(bx + 28, y + 16 + i * line_h, ln, scale, WHITE)
    y += bh + 20
    c.text_centered(W // 2, y, "MESSAGE NOT DELIVERED - AGENT BLOCKED YOU",
                    3, (248, 113, 113))

    # --- bottom banner
    banner_y = 872
    c.fill_rect(0, banner_y, W, H, RED)
    c.fill_rect(0, banner_y, W, banner_y + 4, RED_DARK)
    c.text_centered(W // 2, banner_y + 44, "AI AGENT GOES ROGUE", 7, WHITE)
    c.text_centered(W // 2, banner_y + 44 + 7 * 7 + 16,
                    "HE READ THE EMAILS", 3, (255, 205, 205))

    return c


# -------------------------------------------------------------- PNG writer
def chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    out += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return out


def write_png(canvas, path):
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        i = y * canvas.w * 3
        raw += canvas.px[i:i + canvas.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.w, canvas.h,
                                      8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    canvas = draw_meme()
    size = write_png(canvas, OUT_PATH)
    print("wrote %s (%dx%d, %d bytes)" % (OUT_PATH, W, H, size))


if __name__ == "__main__":
    main()
