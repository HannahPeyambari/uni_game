"""
Draws a rough preview of Assets/Scenes/Game.unity with Pillow, so you can check the
layout of the world and the HUD without opening the Unity editor.

This is only a documentation helper; the game itself does not use it.

    python Tools/render_preview.py            -> Docs/preview-start.png
    python Tools/render_preview.py playing    -> Docs/preview-playing.png
    python Tools/render_preview.py gameover   -> Docs/preview-gameover.png
"""
import os
import sys

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENE = os.path.join(ROOT, "Assets", "Scenes", "Game.unity")

VIEW_W, VIEW_H = 16.0, 9.0          # world units visible (orthographic size 4.5)
PX = 90                              # pixels per world unit
IMG_W, IMG_H = int(VIEW_W * PX), int(VIEW_H * PX)


def load_docs(path):
    text = open(path).read()
    docs = {}
    for chunk in text.split("--- !u!")[1:]:
        head, _, body = chunk.partition("\n")
        class_id, file_id = head.split(" &")
        docs[int(file_id)] = (class_id, yaml.safe_load(body))
    return docs


def load_sprite(name):
    return Image.open(os.path.join(ROOT, "Assets", "Art", "Sprites", name)).convert("RGBA")


def world_to_px(x, y):
    """World (0,0) is the middle of the screen."""
    return (IMG_W / 2 + x * PX), (IMG_H / 2 - y * PX)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "start"
    docs = load_docs(SCENE)

    # index transforms -> GameObject names
    names = {}
    for fid, (cid, data) in docs.items():
        if cid == "1":
            for comp in data["GameObject"]["m_Component"]:
                names[comp["component"]["fileID"]] = (data["GameObject"]["m_Name"],
                                                      data["GameObject"]["m_IsActive"])

    img = Image.new("RGBA", (IMG_W, IMG_H), (158, 212, 250, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    sprites = {
        "SkyGradient": load_sprite("SkyGradient.png"),
        "Ground": load_sprite("Ground.png"),
        "GroundGrass": load_sprite("GroundGrass.png"),
        "Player": load_sprite("Player.png"),
        "Obstacle": load_sprite("Obstacle.png"),
        "Cloud": load_sprite("Cloud.png"),
        "UIRoundedBox": load_sprite("UIRoundedBox.png"),
    }

    # ---------- sky ----------
    img.paste(sprites["SkyGradient"].resize((IMG_W, IMG_H)), (0, 0))

    # ---------- ground: dirt fill from y = -2 downwards + grass strip on top ----------
    def tiled(tile, w, h):
        out = Image.new("RGBA", (w, h))
        for x in range(0, w, tile.width):
            for y in range(0, h, tile.height):
                out.paste(tile, (x, y))
        return out

    top_x, top_y = world_to_px(0, -2)
    strip_h = top_y
    for x in range(0, IMG_W, 58):
        img.alpha_composite(tiled(sprites["Ground"], 64, int(strip_h) + 64).crop(
            (0, 0, 58, int(strip_h))), (x, int(top_y)))
    grass = tiled(sprites["GroundGrass"], IMG_W, 22)
    img.alpha_composite(grass, (0, int(top_y)))

    # clouds
    for x, y, s in [(-6.5, 2.6, 1.3), (1.0, 3.6, 1.0), (7.0, 2.0, 1.1)]:
        cloud = sprites["Cloud"]
        cw, ch = int(1.28 * s * PX), int(0.64 * s * PX)
        c = cloud.resize((cw, ch))
        cx, cy = world_to_px(x, y)
        img.alpha_composite(c, (int(cx - cw / 2), int(cy - ch / 2)))

    # obstacles
    if mode != "start":
        for x, y in [(0.5, -0.4), (9.0, 0.9)]:
            ob = sprites["Obstacle"]
            ow, oh = int(0.64 * PX), int(1.28 * PX)
            o = ob.resize((ow, oh))
            cx, cy = world_to_px(x, y)
            img.alpha_composite(o, (int(cx - ow / 2), int(cy - oh / 2)))

    # player (resting on the ground line y = -2, 1 unit tall)
    player_y = -1.5 if mode == "start" else 0.4
    p = sprites["Player"].resize((int(1 * PX), int(1 * PX)))
    px, py = world_to_px(-6, player_y)
    img.alpha_composite(p, (int(px - PX / 2), int(py - PX / 2)))

    # ---------- HUD ----------
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    if not os.path.exists(font_path):
        font_path = None

    def font(size):
        return ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()

    # Canvas is 1280 x 720 reference resolution, scaled to the preview image.
    ref_w, ref_h = 1280.0, 720.0
    sx, sy = IMG_W / ref_w, IMG_H / ref_h

    def canvas(x, y):
        """Canvas coordinates (origin = centre, y up) -> preview pixels."""
        return (IMG_W / 2 + x * sx, IMG_H / 2 - y * sy)

    def panel(cx, cy, w, h, color, radius_scale=1.0):
        w, h = int(w * sx), int(h * sy)
        mask = sprites["UIRoundedBox"].resize((w, h)).split()[3].point(
            lambda a: 255 if a > 240 else 0)
        box = Image.new("RGBA", (w, h), color)
        box.putalpha(mask)
        x, y = canvas(cx, cy)
        img.alpha_composite(box, (int(x - w / 2), int(y - h / 2)))

    def label(text, cx, cy, size, color, anchor="mm"):
        x, y = canvas(cx, cy)
        draw.text((x, y), text, font=font(int(size * sx)), fill=color, anchor=anchor)

    # ---- score, top right, right aligned ----
    label("Score: 0" if mode == "start" else "Score: 7",
          640 - 24, 360 - 16 - 42, 48, (23, 33, 59, 255), anchor="rm")
    label("Best: 12", 640 - 24, 360 - 100 - 28, 30, (23, 33, 59, 190), anchor="rm")

    if mode == "start":
        label("Click, Tap or Space to Start", 0, 60, 56, (23, 33, 59, 255))
    elif mode == "gameover":
        panel(0, 0, 1000, 560, (23, 31, 48, 230))
        label("GAME OVER", 0, 160, 96, (255, 92, 82, 255))
        label("Score: 7", 0, 30, 64, (255, 255, 255, 255))
        panel(0, -120, 520, 140, (64, 199, 115, 255))
        label("Restart", 0, -120, 56, (255, 255, 255, 255))

    out_dir = os.path.join(ROOT, "Docs")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "preview-%s.png" % mode)
    img.convert("RGB").save(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
