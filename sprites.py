#!/usr/bin/env python3
"""Generate pixel-art sprite PNGs for each pet state."""
from PIL import Image
import os

SCALE = 4
OUT_DIR = os.path.join(os.path.dirname(__file__), "sprites")
BG = (235, 235, 235)

PAL = {
    '.': BG,
    '#': (35,  35,  35),
    'f': (230, 185, 90),
    'p': (255, 140, 160),
    'w': (255, 255, 255),
    'g': (70,  200, 110),   # green iris — happy
    'b': (90,  155, 220),   # blue iris  — okay
    's': (130, 120, 190),   # muted iris — sad
    'u': (35,  35,  35),    # pupil
    'x': (210,  55,  55),   # red X — dead
    'T': (255, 110, 130),   # tongue
    'W': (200, 200, 200),   # skull grey
}

# fmt: off
HAPPY = [
    "....##....##....",
    "...#ff#..#ff#...",
    "..#fffff##ffff#.",
    ".#ffffffffffff#.",
    "#ffwwfffffwwff#.",
    "#ffwgfffffwgff#.",
    "#ff##fffff##ff#.",
    "#ffffffffffff#..",
    "#fffpfffffpff#..",
    "#fff#fffffff#f#.",   # smile corners down
    "#ffffTTTTTfff#..",   # tongue
    ".#ffffffffffff#.",
    "..############..",
    "................",
    "................",
    "................",
]

OKAY = [
    "....##....##....",
    "...#ff#..#ff#...",
    "..#fffff##ffff#.",
    ".#ffffffffffff#.",
    "#ffwwfffffwwff#.",
    "#ffwbfffffwbff#.",
    "#ff##fffff##ff#.",
    "#ffffffffffff#..",
    "#fffpfffffpff#..",
    "#fff##fffff##f#.",  # flat mouth corners
    "#ffffffffffff#..",  # flat mouth
    ".#ffffffffffff#.",
    "..############..",
    "................",
    "................",
    "................",
]

SAD = [
    "....##....##....",
    "...#ff#..#ff#...",
    "..#fffff##ffff#.",
    ".#ffffffffffff#.",
    "#fffwwffffwwff#.",  # eyes shifted, droopy
    "#fffwsffffwsff#.",
    "#fff##ffff##ff#.",
    "#ffffffffffff#..",
    "#fffpfffffpff#..",
    "#ffff##fff##ff#.",  # frown — corners up, middle down
    "#fff#fffffffff#.",  # frown dip
    ".#ffffffffffff#.",
    "..############..",
    "................",
    "................",
    "................",
]

DEAD = [
    "....##....##....",
    "...#ff#..#ff#...",
    "..#fffff##ffff#.",
    ".#ffffffffffff#.",
    "#ffx#fffff#xff#.",  # X eyes
    "#ff#xfffffff#f#.",
    "#ffx#fffff#xff#.",
    "#ffffffffffff#..",
    "#ffffffffffff#..",
    "#fff##fffff##f#.",  # flat mouth
    "#ffffffffffff#..",
    ".#ffffffffffff#.",
    "..############..",
    "................",
    "................",
    "................",
]
# fmt: on


def render(rows, path):
    size = 16 * SCALE
    img = Image.new("RGB", (size, size), BG)
    px = img.load()
    for r, row in enumerate(rows):
        for c, ch in enumerate(row[:16]):
            color = PAL.get(ch, BG)
            for dy in range(SCALE):
                for dx in range(SCALE):
                    px[c * SCALE + dx, r * SCALE + dy] = color
    img.save(path)


def generate():
    os.makedirs(OUT_DIR, exist_ok=True)
    for name, grid in [("happy", HAPPY), ("okay", OKAY), ("sad", SAD), ("dead", DEAD)]:
        assert all(len(row) == 16 for row in grid), f"{name} has bad row lengths"
        assert len(grid) == 16, f"{name} must have 16 rows"
        render(grid, os.path.join(OUT_DIR, f"{name}.png"))
        print(f"  sprites/{name}.png")


if __name__ == "__main__":
    generate()
    print("Done.")
