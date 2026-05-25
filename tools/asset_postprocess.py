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


def parse_size_list(value: str) -> list[int]:
    sizes = [int(part) for part in value.split(",") if part.strip()]
    if not sizes or any(size <= 0 for size in sizes):
        raise argparse.ArgumentTypeError("sizes must be positive integers, for example 64,32")
    return sizes


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


def normalize_sprite(image: Image.Image, canvas_size: int, occupancy: float) -> Image.Image:
    trimmed = trim_alpha(image.convert("RGBA"), padding=0)
    if trimmed is None:
        return Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))

    max_sprite_size = max(1, int(canvas_size * occupancy))
    scale = min(max_sprite_size / trimmed.width, max_sprite_size / trimmed.height)
    width = max(1, int(round(trimmed.width * scale)))
    height = max(1, int(round(trimmed.height * scale)))
    resized = trimmed.resize((width, height), Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    offset = ((canvas_size - width) // 2, (canvas_size - height) // 2)
    canvas.alpha_composite(resized, offset)
    return canvas


def checkerboard(size: int, square: int = 8) -> Image.Image:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 255))
    pixels = image.load()
    light = (238, 238, 238, 255)
    dark = (190, 190, 190, 255)
    for y in range(size):
        for x in range(size):
            pixels[x, y] = light if ((x // square) + (y // square)) % 2 == 0 else dark
    return image


def preview_on_checkerboard(sprite: Image.Image, size: int) -> Image.Image:
    preview = checkerboard(size)
    preview.alpha_composite(sprite.resize((size, size), Image.Resampling.LANCZOS))
    return preview


def alpha_components(
    image: Image.Image, min_alpha: int
) -> list[tuple[int, tuple[int, int, int, int], set[tuple[int, int]]]]:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    pixels = rgba.load()
    visited: set[tuple[int, int]] = set()
    components = []

    for y in range(height):
        for x in range(width):
            point = (x, y)
            if point in visited or pixels[x, y][3] < min_alpha:
                continue

            queue: deque[tuple[int, int]] = deque([point])
            visited.add(point)
            points: set[tuple[int, int]] = set()
            xs = []
            ys = []

            while queue:
                current_x, current_y = queue.popleft()
                points.add((current_x, current_y))
                xs.append(current_x)
                ys.append(current_y)

                for next_y in (current_y - 1, current_y, current_y + 1):
                    for next_x in (current_x - 1, current_x, current_x + 1):
                        if next_x == current_x and next_y == current_y:
                            continue
                        next_point = (next_x, next_y)
                        if (
                            not (0 <= next_x < width and 0 <= next_y < height)
                            or next_point in visited
                            or pixels[next_x, next_y][3] < min_alpha
                        ):
                            continue
                        visited.add(next_point)
                        queue.append(next_point)

            components.append(
                (
                    len(points),
                    (min(xs), min(ys), max(xs) + 1, max(ys) + 1),
                    points,
                )
            )

    components.sort(key=lambda component: component[0], reverse=True)
    return components


def clean_alpha_components(image: Image.Image, min_alpha: int, keep_components: int) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    components = alpha_components(rgba, min_alpha)
    kept_points: set[tuple[int, int]] = set()
    for _, _, points in components[:keep_components]:
        kept_points.update(points)

    for y in range(rgba.height):
        for x in range(rgba.width):
            red, green, blue, alpha = pixels[x, y]
            if (x, y) not in kept_points or alpha < min_alpha:
                pixels[x, y] = (red, green, blue, 0)
    return rgba


def make_contact_sheet(images: list[Image.Image], cols: int, gap: int) -> Image.Image:
    if not images:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    cell_size = images[0].width
    rows = (len(images) + cols - 1) // cols
    width = cols * cell_size + (cols - 1) * gap
    height = rows * cell_size + (rows - 1) * gap
    sheet = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    for index, image in enumerate(images):
        x = (index % cols) * (cell_size + gap)
        y = (index // cols) * (cell_size + gap)
        sheet.alpha_composite(image, (x, y))
    return sheet


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


def key_single_assets(args: argparse.Namespace) -> dict:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    outputs = []
    for source_text in args.inputs:
        source = Path(source_text)
        image = Image.open(source)
        transparent = remove_connected_background(image, args.background, args.threshold)
        trimmed = trim_alpha(transparent, args.padding)
        if trimmed is None:
            continue

        output_path = out_dir / f"{source.stem}.png"
        trimmed.save(output_path)
        outputs.append(
            {
                "source": str(source),
                "path": str(output_path),
                "width": trimmed.width,
                "height": trimmed.height,
            }
        )

    summary = {
        "out_dir": str(out_dir),
        "background": args.background,
        "threshold": args.threshold,
        "padding": args.padding,
        "output_count": len(outputs),
        "outputs": outputs,
        "qa_notes": [
            "Outputs remain generated candidates and are not accepted runtime assets.",
            "Connected background removal only clears edge-connected background color.",
            "Human review is still required for shadow remnants, watermarks, and sprite identity.",
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


def clean_component_assets(args: argparse.Namespace) -> dict:
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    outputs = []
    for source_text in args.inputs:
        source = Path(source_text)
        image = Image.open(source)
        components = alpha_components(image, args.min_alpha)
        cleaned = clean_alpha_components(image, args.min_alpha, args.keep_components)
        trimmed = trim_alpha(cleaned, args.padding)
        if trimmed is None:
            continue

        output_path = out_dir / f"{source.stem}_clean.png"
        trimmed.save(output_path)
        outputs.append(
            {
                "source": str(source),
                "path": str(output_path),
                "width": trimmed.width,
                "height": trimmed.height,
                "component_count": len(components),
                "kept_components": min(args.keep_components, len(components)),
                "largest_components": [
                    {"area": area, "bbox": list(bbox)}
                    for area, bbox, _ in components[: min(6, len(components))]
                ],
            }
        )

    summary = {
        "out_dir": str(out_dir),
        "min_alpha": args.min_alpha,
        "keep_components": args.keep_components,
        "padding": args.padding,
        "output_count": len(outputs),
        "outputs": outputs,
        "qa_notes": [
            "Outputs remain generated candidates and are not accepted runtime assets.",
            "The pass keeps the largest alpha-connected components to remove detached stars, shadows, and noise.",
            "Human review is still required for silhouette quality and art-direction fit.",
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


def make_previews(args: argparse.Namespace) -> dict:
    out_dir = Path(args.out_dir)
    normalized_dir = out_dir / f"normalized_{args.canvas_size}"
    normalized_dir.mkdir(parents=True, exist_ok=True)
    preview_dirs = {}
    runtime_dirs = {}
    for size in args.preview_sizes:
        preview_dir = out_dir / f"preview_{size}"
        preview_dir.mkdir(parents=True, exist_ok=True)
        preview_dirs[size] = preview_dir
        runtime_dir = out_dir / f"runtime_{size}"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        runtime_dirs[size] = runtime_dir

    outputs = []
    contact_previews: dict[int, list[Image.Image]] = {size: [] for size in args.preview_sizes}
    for source_text in args.inputs:
        source = Path(source_text)
        sprite_id = source.stem
        image = Image.open(source)
        normalized = normalize_sprite(image, args.canvas_size, args.occupancy)
        normalized_path = normalized_dir / f"{sprite_id}_normalized_{args.canvas_size}.png"
        normalized.save(normalized_path)

        previews = []
        runtime_candidates = []
        for size in args.preview_sizes:
            runtime_candidate = normalized.resize((size, size), Image.Resampling.LANCZOS)
            runtime_path = runtime_dirs[size] / f"{sprite_id}_runtime_{size}.png"
            runtime_candidate.save(runtime_path)
            preview = preview_on_checkerboard(normalized, size)
            preview_path = preview_dirs[size] / f"{sprite_id}_preview_{size}.png"
            preview.save(preview_path)
            contact_previews[size].append(preview)
            runtime_candidates.append({"size": size, "path": str(runtime_path)})
            previews.append({"size": size, "path": str(preview_path)})

        outputs.append(
            {
                "id": sprite_id,
                "source": str(source),
                "normalized": str(normalized_path),
                "runtime_candidates": runtime_candidates,
                "previews": previews,
            }
        )

    contact_sheets = []
    for size, previews in contact_previews.items():
        sheet = make_contact_sheet(previews, args.contact_cols, args.contact_gap)
        path = out_dir / f"contact_sheet_{size}.png"
        sheet.save(path)
        contact_sheets.append({"size": size, "path": str(path)})

    summary = {
        "out_dir": str(out_dir),
        "canvas_size": args.canvas_size,
        "preview_sizes": args.preview_sizes,
        "occupancy": args.occupancy,
        "output_count": len(outputs),
        "outputs": outputs,
        "contact_sheets": contact_sheets,
        "qa_notes": [
            "Outputs remain generated candidates and are not accepted runtime assets.",
            "Normalized sprites use transparent square canvases for size comparison.",
            "Runtime-size PNGs are transparent review candidates and require human approval before promotion.",
            "Checkerboard previews are for readability review only and should not be used in runtime.",
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

    key_singles = subparsers.add_parser(
        "key-singles", help="remove connected background from single-image candidates"
    )
    key_singles.add_argument("inputs", nargs="+", help="input generated single-image candidates")
    key_singles.add_argument("--out-dir", required=True, help="candidate output directory")
    key_singles.add_argument(
        "--background",
        choices=("auto", "sampled", "green"),
        default="auto",
        help="background keying mode",
    )
    key_singles.add_argument(
        "--threshold",
        type=float,
        default=42.0,
        help="color distance threshold for sampled backgrounds",
    )
    key_singles.add_argument("--padding", type=int, default=8, help="transparent padding in pixels")
    key_singles.add_argument("--manifest", help="optional JSON summary output")
    key_singles.set_defaults(func=key_single_assets)

    clean_components = subparsers.add_parser(
        "clean-components", help="remove detached alpha components from PNG candidates"
    )
    clean_components.add_argument("inputs", nargs="+", help="input transparent PNG candidates")
    clean_components.add_argument("--out-dir", required=True, help="candidate output directory")
    clean_components.add_argument(
        "--min-alpha", type=int, default=24, help="minimum alpha included in components"
    )
    clean_components.add_argument(
        "--keep-components", type=int, default=1, help="number of largest components to keep"
    )
    clean_components.add_argument(
        "--padding", type=int, default=4, help="transparent padding after cleanup"
    )
    clean_components.add_argument("--manifest", help="optional JSON summary output")
    clean_components.set_defaults(func=clean_component_assets)

    previews = subparsers.add_parser(
        "make-previews", help="normalize selected PNG candidates and make review previews"
    )
    previews.add_argument("inputs", nargs="+", help="input PNG candidates")
    previews.add_argument("--out-dir", required=True, help="candidate output directory")
    previews.add_argument(
        "--canvas-size", type=int, default=128, help="square normalized canvas size"
    )
    previews.add_argument(
        "--preview-sizes",
        type=parse_size_list,
        default=[64, 32],
        help="comma-separated preview sizes, for example 64,32",
    )
    previews.add_argument(
        "--occupancy",
        type=float,
        default=0.86,
        help="fraction of the canvas occupied by the longest sprite side",
    )
    previews.add_argument("--contact-cols", type=int, default=4, help="contact sheet columns")
    previews.add_argument("--contact-gap", type=int, default=8, help="contact sheet gap")
    previews.add_argument("--manifest", help="optional JSON summary output")
    previews.set_defaults(func=make_previews)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    summary = args.func(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
