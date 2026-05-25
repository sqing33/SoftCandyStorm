#!/usr/bin/env python3
"""Generate programmatic top-down prototype assets.

These assets are hand-authored placeholders for the Runtime prototype. They are
not AI-generated and can be used to replace geometry blocks while final art is
still moving through candidate review.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path("assets/prototype_topdown")
SPRITES = ROOT / "sprites"
MANIFEST = ROOT / "manifest.json"
CONTACT_SHEET = ROOT / "contact_sheet.png"


def rgba(hex_color: str | tuple[int, int, int, int], alpha: int = 255) -> tuple[int, int, int, int]:
    if isinstance(hex_color, tuple):
        return hex_color
    value = hex_color.lstrip("#")
    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
        alpha,
    )


def canvas(size: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def ellipse(draw: ImageDraw.ImageDraw, box, fill, outline="#4a2b32", width=4):
    draw.ellipse(box, fill=rgba(fill), outline=rgba(outline), width=width)


def polygon(draw: ImageDraw.ImageDraw, points, fill, outline="#4a2b32", width=4):
    draw.polygon(points, fill=rgba(fill), outline=rgba(outline))
    if width > 1:
        draw.line(points + [points[0]], fill=rgba(outline), width=width, joint="curve")


def rounded(draw: ImageDraw.ImageDraw, box, radius, fill, outline="#4a2b32", width=4):
    draw.rounded_rectangle(box, radius=radius, fill=rgba(fill), outline=rgba(outline), width=width)


def save(image: Image.Image, name: str) -> dict:
    SPRITES.mkdir(parents=True, exist_ok=True)
    path = SPRITES / f"{name}.png"
    image.save(path)
    return {
        "id": name.replace("_v001", ""),
        "version": 1,
        "path": str(path.relative_to(ROOT)),
        "dimensions": {"width": image.width, "height": image.height},
        "source": "programmatic_pillow",
    }


def make_contact_sheet(items: list[dict]) -> None:
    cell = 96
    cols = 5
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell, rows * cell), rgba("#f5efd9"))
    for index, item in enumerate(items):
        image = Image.open(ROOT / item["path"]).convert("RGBA")
        scale = min(72 / image.width, 72 / image.height)
        width = max(1, int(image.width * scale))
        height = max(1, int(image.height * scale))
        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        x = (index % cols) * cell + (cell - width) // 2
        y = (index // cols) * cell + (cell - height) // 2
        sheet.alpha_composite(resized, (x, y))
    sheet.save(CONTACT_SHEET)


def player() -> Image.Image:
    image, draw = canvas(64)
    ellipse(draw, (17, 22, 47, 52), "#ffe4ed")
    ellipse(draw, (21, 9, 43, 31), "#fff4dc")
    rounded(draw, (25, 6, 39, 20), 4, "#ff89b5", width=3)
    draw.rectangle((27, 8, 37, 13), fill=rgba("#ffe8f1"))
    ellipse(draw, (11, 31, 23, 43), "#ffd2df", width=3)
    ellipse(draw, (41, 31, 53, 43), "#ffd2df", width=3)
    ellipse(draw, (23, 30, 27, 34), "#4a2b32", outline="#4a2b32", width=1)
    ellipse(draw, (37, 30, 41, 34), "#4a2b32", outline="#4a2b32", width=1)
    draw.arc((25, 30, 39, 43), 25, 155, fill=rgba("#4a2b32"), width=2)
    return image


def bouncy_gummy() -> Image.Image:
    image, draw = canvas(64)
    ellipse(draw, (9, 12, 55, 56), "#90e57f")
    for box in [(17, 17, 25, 25), (39, 18, 48, 27), (26, 39, 35, 48)]:
        ellipse(draw, box, "#baff9e", outline="#6cc45b", width=2)
    ellipse(draw, (23, 29, 27, 33), "#4a2b32", outline="#4a2b32", width=1)
    ellipse(draw, (37, 29, 41, 33), "#4a2b32", outline="#4a2b32", width=1)
    draw.arc((24, 31, 41, 43), 20, 160, fill=rgba("#4a2b32"), width=2)
    return image


def sour_gummy() -> Image.Image:
    image, draw = canvas(64)
    points = [(32, 7), (43, 20), (57, 23), (48, 36), (50, 52), (32, 46), (15, 54), (17, 36), (7, 24), (22, 20)]
    polygon(draw, points, "#ffd94f")
    for point in [(24, 18), (42, 27), (29, 42)]:
        ellipse(draw, (point[0] - 2, point[1] - 2, point[0] + 2, point[1] + 2), "#fff4a7", outline="#fff4a7", width=1)
    ellipse(draw, (23, 28, 27, 32), "#4a2b32", outline="#4a2b32", width=1)
    ellipse(draw, (37, 28, 41, 32), "#4a2b32", outline="#4a2b32", width=1)
    draw.arc((24, 32, 41, 41), 190, 350, fill=rgba("#4a2b32"), width=2)
    return image


def caramel_slime() -> Image.Image:
    image, draw = canvas(64)
    ellipse(draw, (9, 18, 55, 51), "#c87932")
    ellipse(draw, (13, 32, 31, 58), "#a95d2a")
    ellipse(draw, (35, 35, 51, 58), "#a95d2a")
    ellipse(draw, (21, 28, 25, 32), "#4a2b32", outline="#4a2b32", width=1)
    ellipse(draw, (39, 28, 43, 32), "#4a2b32", outline="#4a2b32", width=1)
    draw.arc((23, 30, 42, 43), 20, 160, fill=rgba("#4a2b32"), width=2)
    return image


def sandwich_cookie() -> Image.Image:
    image, draw = canvas(64)
    rounded(draw, (10, 13, 54, 51), 12, "#9a6134")
    rounded(draw, (14, 22, 50, 42), 8, "#fff1cf", outline="#6b3c22", width=3)
    rounded(draw, (13, 16, 51, 33), 9, "#b77740", outline="#6b3c22", width=3)
    for point in [(23, 21), (36, 19), (43, 27), (29, 28)]:
        ellipse(draw, (point[0] - 2, point[1] - 2, point[0] + 2, point[1] + 2), "#5f321c", outline="#5f321c", width=1)
    ellipse(draw, (24, 34, 28, 38), "#4a2b32", outline="#4a2b32", width=1)
    ellipse(draw, (37, 34, 41, 38), "#4a2b32", outline="#4a2b32", width=1)
    return image


def boss_mixer() -> Image.Image:
    image, draw = canvas(128)
    ellipse(draw, (22, 20, 106, 104), "#ff83a8", width=6)
    ellipse(draw, (36, 34, 92, 89), "#ffe6f1", outline="#8c3450", width=4)
    ellipse(draw, (48, 45, 80, 78), "#ffd56b", outline="#8c3450", width=3)
    for angle_box in [(12, 55, 41, 75), (87, 55, 116, 75), (54, 6, 74, 35), (54, 89, 74, 119)]:
        rounded(draw, angle_box, 8, "#d94f7a", outline="#8c3450", width=4)
    draw.line((64, 48, 64, 79), fill=rgba("#8c3450"), width=5)
    draw.line((49, 64, 79, 64), fill=rgba("#8c3450"), width=5)
    ellipse(draw, (54, 54, 74, 74), "#fff7a7", outline="#8c3450", width=3)
    return image


def xp_crystal() -> Image.Image:
    image, draw = canvas(32)
    polygon(draw, [(16, 3), (27, 12), (22, 27), (10, 28), (4, 13)], "#4ed6ff", outline="#146b9b", width=3)
    polygon(draw, [(16, 3), (18, 16), (27, 12)], "#a8f1ff", outline="#146b9b", width=1)
    polygon(draw, [(4, 13), (18, 16), (10, 28)], "#28a9e0", outline="#146b9b", width=1)
    return image


def rainbow_projectile() -> Image.Image:
    image, draw = canvas(32)
    ellipse(draw, (4, 4, 28, 28), "#f7f1d2", width=3)
    draw.arc((6, 6, 26, 26), 95, 275, fill=rgba("#ff4c78"), width=5)
    draw.arc((8, 6, 28, 26), 95, 275, fill=rgba("#ffdd4f"), width=5)
    draw.arc((10, 6, 30, 26), 95, 275, fill=rgba("#4fd66b"), width=5)
    draw.arc((12, 6, 32, 26), 95, 275, fill=rgba("#4f9cff"), width=5)
    draw.ellipse((4, 4, 28, 28), outline=rgba("#4a2b32"), width=3)
    return image


def map_tile() -> Image.Image:
    image, draw = canvas(128)
    draw.rectangle((0, 0, 128, 128), fill=rgba("#bce889"))
    for x, y, color in [(18, 20, "#fff4c7"), (73, 29, "#f7cfdf"), (44, 81, "#fff4c7"), (101, 92, "#d5f5a4")]:
        ellipse(draw, (x - 8, y - 5, x + 8, y + 5), color, outline="#83bd68", width=2)
    draw.line((0, 110, 128, 88), fill=rgba("#e8c47a"), width=10)
    draw.line((0, 110, 128, 88), fill=rgba("#fff0b8"), width=4)
    return image


def main() -> None:
    assets = [
        save(player(), "player_jar_keeper_v001"),
        save(bouncy_gummy(), "enemy_bouncy_gummy_v001"),
        save(sour_gummy(), "enemy_sour_gummy_v001"),
        save(caramel_slime(), "enemy_caramel_slime_v001"),
        save(sandwich_cookie(), "enemy_sandwich_cookie_creep_v001"),
        save(boss_mixer(), "boss_runaway_sugar_mixer_v001"),
        save(xp_crystal(), "pickup_candy_crystal_v001"),
        save(rainbow_projectile(), "projectile_rainbow_candy_shot_v001"),
        save(map_tile(), "map_frosting_grassland_tile_v001"),
    ]
    make_contact_sheet(assets)
    manifest = {
        "pack_id": "prototype_topdown",
        "version": 1,
        "source": "programmatic_pillow",
        "candidate_only": False,
        "runtime_ready": True,
        "runtime_integrated": False,
        "style": "cute candy top-down prototype placeholders",
        "notes": [
            "These are programmatic placeholder assets, not AI-generated final art.",
            "They replace runtime geometry blocks while AI-generated art remains in candidate review.",
            "Final art still needs prompt/source/version/postprocess metadata before promotion.",
        ],
        "contact_sheet": CONTACT_SHEET.name,
        "assets": assets,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
