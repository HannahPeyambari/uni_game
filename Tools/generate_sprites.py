"""
Generates every placeholder sprite used by the Square Jumper demo scene.

The generated PNG files are already committed to Assets/Art/Sprites, so you only
need to run this script if you want different colours or shapes.

Usage (from the project root):
    python Tools/generate_sprites.py
Needs Pillow:  pip install pillow
"""
from PIL import Image, ImageDraw
import os
import random

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "Assets", "Art", "Sprites")


def save(img, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    img.save(path, "PNG")
    print("wrote", path, img.size)


# ------------------------------------------------------------------ player 64x64
S = 64
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([6, 6, 58, 58], radius=14, fill=(255, 138, 61, 255),
                    outline=(120, 55, 18, 255), width=3)
d.rounded_rectangle([16, 34, 48, 52], radius=8, fill=(255, 196, 132, 255))
for ex in (24, 40):
    d.ellipse([ex - 7, 18, ex + 7, 34], fill=(255, 255, 255, 255),
              outline=(90, 40, 12, 255), width=2)
    d.ellipse([ex - 3, 23, ex + 4, 30], fill=(40, 30, 28, 255))
    d.ellipse([ex - 1, 24, ex + 1, 26], fill=(255, 255, 255, 255))
d.arc([24, 36, 40, 46], start=10, end=170, fill=(150, 70, 25, 255), width=3)
d.rounded_rectangle([12, 54, 26, 62], radius=4, fill=(214, 96, 34, 255),
                    outline=(120, 55, 18, 255), width=2)
d.rounded_rectangle([38, 54, 52, 62], radius=4, fill=(214, 96, 34, 255),
                    outline=(120, 55, 18, 255), width=2)
save(img, "Player.png")

# --------------------------------------------------------------- obstacle 64x128
W, H = 64, 128
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([3, 3, W - 4, H - 4], radius=10, fill=(226, 74, 74, 255),
                    outline=(120, 26, 26, 255), width=4)
for y in range(16, H - 16, 32):
    d.polygon([(12, y), (26, y), (16, y + 18), (2, y + 18)], fill=(255, 206, 92, 255))
    d.polygon([(40, y + 4), (54, y + 4), (44, y + 22), (30, y + 22)], fill=(255, 206, 92, 255))
d.rounded_rectangle([8, 8, 20, H - 9], radius=6, fill=(255, 130, 120, 255))
save(img, "Obstacle.png")

# ------------------------------------------------------------ ground tile 64x64
# Plain dirt: it is used with the Tiled draw mode and stretched to the bottom of the screen.
img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 64, 64], fill=(108, 74, 42, 255))
random.seed(7)
for _ in range(26):
    x = random.randint(0, 61)
    y = random.randint(0, 61)
    c = random.choice([(101, 68, 38, 255), (116, 80, 46, 255), (98, 66, 36, 255)])
    d.rectangle([x, y, x + 2, y + 2], fill=c)
save(img, "Ground.png")

# --------------------------------------------------- grass strip on top of the dirt
img = Image.new("RGBA", (64, 24), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 64, 24], fill=(108, 74, 42, 255))       # dirt underneath
d.rectangle([0, 0, 64, 13], fill=(124, 196, 90, 255))      # grass
d.rectangle([0, 13, 64, 17], fill=(88, 158, 66, 255))      # grass shadow
for x in range(0, 64, 16):                                  # a few grass blades
    d.polygon([(x + 3, 1), (x + 6, 1), (x + 4, -3)], fill=(140, 210, 104, 255))
save(img, "GroundGrass.png")

# ------------------------------------------------------------- sky gradient strip
img = Image.new("RGBA", (8, 256), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
top, bottom = (126, 200, 255), (222, 244, 255)
for y in range(256):
    t = y / 255.0
    col = (int(top[0] + (bottom[0] - top[0]) * t),
           int(top[1] + (bottom[1] - top[1]) * t),
           int(top[2] + (bottom[2] - top[2]) * t), 255)
    d.line([(0, y), (7, y)], fill=col)
save(img, "SkyGradient.png")

# ---------------------------------------------------- rounded white box for the UI
img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
d.rounded_rectangle([0, 0, 31, 31], radius=10, fill=(255, 255, 255, 255))
save(img, "UIRoundedBox.png")

# --------------------------------------------------------------------- cloud 128x64
img = Image.new("RGBA", (128, 64), (0, 0, 0, 0))
d = ImageDraw.Draw(img)
for (cx, cy, r) in [(38, 44, 20), (64, 34, 26), (92, 44, 18), (54, 48, 16), (78, 48, 16)]:
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 235))
d.rounded_rectangle([18, 44, 110, 58], radius=7, fill=(255, 255, 255, 235))
save(img, "Cloud.png")
