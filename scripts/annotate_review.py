#!/usr/bin/env python3
"""
Draw precise review callouts on a reference or screenshot image.

Important:
- By default, annotations are exact only when explicit regions are provided.
- Approximate preset (`long-landing`) is optional and must be enabled explicitly.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def severity_color(severity: str) -> tuple[int, int, int]:
    _ = severity
    # Unified marker color for better visual consistency.
    return (220, 40, 40)


def to_px(value: float | int, size: int) -> int:
    v = float(value)
    if 0.0 <= v <= 1.0:
        return int(v * size)
    return int(v)


def default_regions_long_landing() -> list[dict]:
    return [
        {"id": "A6", "y0": 0.0, "y1": 0.09, "severity": "major", "note": "header"},
        {"id": "A4", "y0": 0.09, "y1": 0.28, "severity": "major", "note": "hero"},
        {"id": "A5", "y0": 0.20, "y1": 0.30, "severity": "major", "note": "cta"},
        {"id": "A2", "y0": 0.28, "y1": 0.52, "severity": "critical", "note": "widget gallery"},
        {"id": "A3", "y0": 0.52, "y1": 0.66, "severity": "major", "note": "feature grid"},
        {"id": "A1", "y0": 0.70, "y1": 0.92, "severity": "critical", "note": "price + final cta"},
    ]


def normalize_rect(r: dict, w: int, h: int) -> tuple[int, int, int, int] | None:
    if all(k in r for k in ("x0", "y0", "x1", "y1")):
        x0 = to_px(r["x0"], w)
        y0 = to_px(r["y0"], h)
        x1 = to_px(r["x1"], w)
        y1 = to_px(r["y1"], h)
    elif all(k in r for k in ("x", "y", "w", "h")):
        x0 = to_px(r["x"], w)
        y0 = to_px(r["y"], h)
        x1 = x0 + to_px(r["w"], w)
        y1 = y0 + to_px(r["h"], h)
    elif all(k in r for k in ("y0", "y1")):
        x0, x1 = 12, w - 12
        y0 = to_px(r["y0"], h)
        y1 = to_px(r["y1"], h)
    else:
        return None

    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    x0 = max(0, min(w - 1, x0))
    x1 = max(1, min(w, x1))
    y0 = max(0, min(h - 1, y0))
    y1 = max(1, min(h, y1))
    if x1 <= x0 or y1 <= y0:
        return None
    return x0, y0, x1, y1


def draw_circle(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, color: tuple[int, int, int]) -> None:
    width = max(2, int(radius * 0.22))
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        outline=color + (255,),
        width=width,
        fill=(255, 255, 255, 10),
    )


def annotate(
    input_path: Path,
    output_path: Path,
    regions: list[dict],
    supersample: int = 2,
    output_scale: float = 1.0,
) -> None:
    img = Image.open(input_path).convert("RGBA")
    base_w, base_h = img.size

    ss = max(1, int(supersample))
    if ss > 1:
        work_img = img.resize((base_w * ss, base_h * ss), Image.Resampling.LANCZOS)
    else:
        work_img = img.copy()

    w, h = work_img.size
    overlay = Image.new("RGBA", work_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22 * ss)
        font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 14 * ss)
    except OSError:
        font = ImageFont.load_default()
        font_small = font

    for r in regions:
        rid = str(r["id"])
        kind = str(r.get("kind", "box"))

        # Scale region coordinates for supersampled canvas
        r_scaled = dict(r)
        for key in ("x", "y", "w", "h", "x0", "x1", "y0", "y1", "cx", "cy", "radius"):
            if key in r_scaled and isinstance(r_scaled[key], (int, float)) and float(r_scaled[key]) > 1:
                r_scaled[key] = float(r_scaled[key]) * ss

        rect = normalize_rect(r_scaled, w, h)
        if kind != "point-circle" and not rect:
            continue

        color = severity_color(str(r.get("severity", "minor")))
        outline = color + (245,)
        fill = color + (26,)

        if kind == "point-circle":
            if "cx" not in r_scaled or "cy" not in r_scaled:
                continue
            cx = to_px(r_scaled["cx"], w)
            cy = to_px(r_scaled["cy"], h)
            radius = int(r_scaled.get("radius", max(12 * ss, min(w, h) * 0.028)))
            draw_circle(draw, cx, cy, radius, color)
            x0, y0 = max(0, cx - radius), max(0, cy - radius)
        else:
            x0, y0, x1, y1 = rect
            if kind == "corner-circles":
                radius = int(r_scaled.get("radius", max(10 * ss, min(w, h) * 0.022)))
                draw_circle(draw, x0, y0, radius, color)
                draw_circle(draw, x1, y0, radius, color)
                draw_circle(draw, x0, y1, radius, color)
                draw_circle(draw, x1, y1, radius, color)
                if bool(r.get("show_box", False)):
                    draw.rectangle([x0, y0, x1, y1], outline=outline, width=max(2, 2 * ss), fill=fill)
            else:
                draw.rectangle([x0, y0, x1, y1], outline=outline, width=max(3, 3 * ss), fill=fill)

        label = f" {rid} "
        tw, th = draw.textbbox((0, 0), label, font=font)[2:4]
        pad = 6 * ss
        lx, ly = x0 + 8 * ss, max(0, y0 + 8 * ss)
        draw.rounded_rectangle(
            [lx, ly, lx + tw + pad * 2, ly + th + pad * 2],
            radius=6 * ss,
            fill=(20, 20, 20, 230),
        )
        draw.text((lx + pad, ly + pad), label, fill=(255, 255, 255, 255), font=font)

        note = str(r.get("note", ""))
        if note:
            draw.text((lx + pad, ly + th + pad * 2 + 4 * ss), note, fill=(35, 35, 35, 255), font=font_small)

    out = Image.alpha_composite(work_img, overlay)

    # Downsample back for anti-aliased look, then optionally upscale output resolution
    if ss > 1:
        out = out.resize((base_w, base_h), Image.Resampling.LANCZOS)

    if output_scale and output_scale > 1.0:
        out = out.resize((int(base_w * output_scale), int(base_h * output_scale)), Image.Resampling.LANCZOS)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    out.convert("RGB").save(output_path, format="PNG", optimize=True, compress_level=1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Annotate design review regions on an image")
    parser.add_argument("--input", required=True, type=Path, help="Source PNG/JPG")
    parser.add_argument("--output", required=True, type=Path, help="Output PNG path")
    parser.add_argument(
        "--regions-json",
        type=str,
        default="",
        help=(
            "JSON array with marker objects. "
            "Supports box regions {id,x,y,w,h|x0,y0,x1,y1,severity?,note?,kind?} "
            "or point circle {id,kind:'point-circle',cx,cy,radius?,...}. "
            "kind: box|corner-circles|point-circle"
        ),
    )
    parser.add_argument(
        "--preset",
        choices=["none", "long-landing"],
        default="none",
        help="Use long-landing ONLY for rough approximation",
    )
    parser.add_argument(
        "--supersample",
        type=int,
        default=2,
        help="Internal draw scale for anti-aliasing (default 2)",
    )
    parser.add_argument(
        "--output-scale",
        type=float,
        default=1.0,
        help="Final output upscale factor (e.g. 2.0 for higher-res PNG)",
    )
    args = parser.parse_args()

    if args.regions_json.strip():
        regions = json.loads(args.regions_json)
    elif args.preset == "long-landing":
        regions = default_regions_long_landing()
    else:
        regions = []

    if not regions:
        raise SystemExit(
            "No explicit mismatch regions provided. Pass --regions-json for exact markers. "
            "Use --preset long-landing only for approximate drafts."
        )

    annotate(
        args.input,
        args.output,
        regions,
        supersample=args.supersample,
        output_scale=args.output_scale,
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
