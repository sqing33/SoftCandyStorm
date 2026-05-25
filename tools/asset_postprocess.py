#!/usr/bin/env python3
"""Post-process generated asset candidates.

The tool only writes to candidate directories. It is meant to make AI-generated
sprites auditable before any human-approved asset promotion.
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from pathlib import Path
from typing import Iterable

from PIL import Image


def parse_grid(value: str) -> tuple[int, int]:
    if "x" not in value:
        raise argparse.ArgumentTypeError("grid must use COLSxROWS, for example 5x5")
    cols_text, rows_text = value.lower().split("x", 1)
    cols = int(cols_text)
    rows = int(rows_text)
    if cols <= 0 or rows <= 0:
        raise argparse.ArgumentTypeError("grid dimensions must be positive")
    return cols, rows


def average_corner_color(image: Image.Image, sample_size: int = 12) -> tuple[int, int, int]:
    rgb = image.convert("RGB")
    width, height = rgb.size
    points: list[tuple[int, int, int]] = []
    boxes = [
        (0, 0, sample_size, sample_size),
        (width - sample_size, 0, width, sample_size),
        (0, height - sample_size, sample_size, height),
        (width - sample_size, height - sample_size, width, height),
    ]
    for box in boxes:
        crop = rgb.crop(box)
        points.extend(crop.getdata())
    total = len(points)
    return tuple(sum(pixel[index] for pixel in points) // total for index in range(3))


def color_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return sum((a[index] - b[index]) ** 2 for index in range(3)) ** 0.5


def resolve_background_mode(
    mode: str, background_color: tuple[int, int, int]
) -> tuple[str, tuple[int, int, int]]:
    if mode != "auto":
        return mode, background_color
    red, green, blue = background_color
    if green > 150 and green - max(red, blue) > 70:
        return "green", (0, 255, 0)
    return "sampled", background_color


def edge_points(width: int, height: int) -> Iterable[tuple[int, int]]:
    for x in range(width):
        yield x, 0
        yield x, height - 1
    for y in range(1, height - 1):
        yield 0, y
        yield width - 1, y


def connected_background_mask(
    image: Image.Image,
    mode: str,
    threshold: float,
) -> set[tuple[int, int]]:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    sampled_color = average_corner_color(rgba)
    resolved_mode, target_color = resolve_background_mode(mode, sampled_color)

    def is_background(x: int, y: int) -> bool:
        red, green, blue, alpha = pixels[x, y]
        if alpha == 0:
            return True
        if resolved_mode == "green":
            return green > 150 and red < 135 and blue < 135
        return color_distance((red, green, blue), target_color) <= threshold

    queue: deque[tuple[int, int]] = deque()
    visited: set[tuple[int, int]] = set()
    for point in edge_points(width, height):
        if point not in visited and is_background(*point):
            visited.add(point)
            queue.append(point)

    while queue:
        x, y = queue.popleft()
        for next_x, next_y in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
            if not (0 <= next_x < width and 0 <= next_y < height):
                continue
            point = (next_x, next_y)
            if point in visited or not is_background(next_x, next_y):
                continue
            visited.add(point)
            queue.append(point)

    return visited


def remove_connected_background(
    image: Image.Image,
    mode: str,
    threshold: float,
) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    for x, y in connected_background_mask(rgba, mode, threshold):
        red, green, blue, _ = pixels[x, y]
        pixels[x, y] = (red, green, blue, 0)
    return rgba


def trim_alpha(image: Image.Image, padding: int) -> Image.Image | None:
    alpha = image.getchannel("A")
    bbox = alpha.getbbox()
    if bbox is None:
        return None
    left, top, right, bottom = bbox
    left = max(0, left - padding)
    top = max(0, top - padding)
    right = min(image.width, right + padding)
    bottom = min(image.height, bottom + padding)
    return image.crop((left, top, right, bottom))


def extract_sprites(args: argparse.Namespace) -> dict:
    source = Path(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    image = Image.open(source)
    cols, rows = args.grid
    cell_width = image.width // cols
    cell_height = image.height // rows

    outputs = []
    for row in range(rows):
        for col in range(cols):
            left = col * cell_width
            top = row * cell_height
            right = image.width if col == cols - 1 else (col + 1) * cell_width
            bottom = image.height if row == rows - 1 else (row + 1) * cell_height
            cell = image.crop((left, top, right, bottom))
            transparent = remove_connected_background(cell, args.background, args.threshold)
            trimmed = trim_alpha(transparent, args.padding)
            if trimmed is None:
                continue
            output_path = out_dir / f"{args.prefix}_r{row + 1:02}_c{col + 1:02}.png"
            trimmed.save(output_path)
            outputs.append(
                {
                    "grid": {"row": row + 1, "col": col + 1},
                    "path": str(output_path),
                    "width": trimmed.width,
                    "height": trimmed.height,
                }
            )

    summary = {
        "source": str(source),
        "out_dir": str(out_dir),
        "grid": {"cols": cols, "rows": rows},
        "background": args.background,
        "threshold": args.threshold,
        "padding": args.padding,
        "output_count": len(outputs),
        "outputs": outputs,
        "qa_notes": [
            "Outputs remain generated candidates and are not accepted runtime assets.",
            "Connected background removal avoids deleting internal white highlights.",
            "Human review is still required for shadows, readability, and sprite identity.",
        ],
    }
    if args.manifest:
        manifest_path = Path(args.manifest)
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    extract = subparsers.add_parser(
        "extract-sprites", help="split a generated spritesheet into PNG candidates"
    )
    extract.add_argument("input", help="input generated spritesheet")
    extract.add_argument("--grid", type=parse_grid, required=True, help="grid as COLSxROWS")
    extract.add_argument("--out-dir", required=True, help="candidate output directory")
    extract.add_argument("--prefix", default="sprite", help="output filename prefix")
    extract.add_argument(
        "--background",
        choices=("auto", "sampled", "green"),
        default="auto",
        help="background keying mode",
    )
    extract.add_argument(
        "--threshold",
        type=float,
        default=42.0,
        help="color distance threshold for sampled backgrounds",
    )
    extract.add_argument("--padding", type=int, default=4, help="transparent padding in pixels")
    extract.add_argument("--manifest", help="optional JSON summary output")
    extract.set_defaults(func=extract_sprites)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    summary = args.func(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
