#!/usr/bin/env python3
"""
Interactive helper to build regions JSON for annotate_review.py.

Example:
  python3 scripts/regions_builder.py --image "path/to/image.png" --output regions.json
Then:
  python3 scripts/annotate_review.py --input "path/to/image.png" --output "DESIGN REVIEW REPORT/annotated-YYYYMMDD-HHMM.png" --regions-json "$(cat regions.json)" --output-scale 2
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    val = input(f"{prompt}{suffix}: ").strip()
    if not val and default is not None:
        return default
    return val


def as_float(v: str) -> float:
    return float(v.replace(",", "."))


def px_to_norm(value: float, size: int) -> float:
    if size <= 0:
        return 0.0
    return round(value / size, 6)


def add_box(image_w: int, image_h: int, kind: str) -> dict:
    print("Введите координаты в пикселях")
    x = as_float(ask("x (левый край)"))
    y = as_float(ask("y (верхний край)"))
    w = as_float(ask("w (ширина)"))
    h = as_float(ask("h (высота)"))
    return {
        "kind": kind,
        "x": px_to_norm(x, image_w),
        "y": px_to_norm(y, image_h),
        "w": px_to_norm(w, image_w),
        "h": px_to_norm(h, image_h),
    }


def add_point(image_w: int, image_h: int) -> dict:
    print("Введите координаты точки в пикселях")
    cx = as_float(ask("cx"))
    cy = as_float(ask("cy"))
    radius = as_float(ask("radius (пиксели)", "24"))
    return {
        "kind": "point-circle",
        "cx": px_to_norm(cx, image_w),
        "cy": px_to_norm(cy, image_h),
        # radius оставляем в пикселях для удобной визуальной настройки
        "radius": round(radius, 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build regions JSON interactively")
    parser.add_argument("--image", required=True, type=Path, help="Image path used for coordinate normalization")
    parser.add_argument("--output", required=True, type=Path, help="Output JSON file")
    parser.add_argument("--append", action="store_true", help="Append to existing JSON array")
    args = parser.parse_args()

    if not args.image.is_file():
        raise SystemExit(f"Image not found: {args.image}")

    im = Image.open(args.image)
    image_w, image_h = im.size
    print(f"Image size: {image_w}x{image_h}")

    regions: list[dict] = []
    if args.append and args.output.exists():
        try:
            regions = json.loads(args.output.read_text(encoding="utf-8"))
            if not isinstance(regions, list):
                regions = []
        except Exception:
            regions = []

    print("
Добавляй зоны. Пустой id завершает ввод.
")
    while True:
        rid = ask("id зоны (например A1), Enter для завершения")
        if not rid:
            break

        kind = ask("тип (box / corner-circles / point-circle)", "corner-circles")
        if kind not in {"box", "corner-circles", "point-circle"}:
            print("Неизвестный тип, используем corner-circles")
            kind = "corner-circles"

        severity = ask("критичность (critical / major / minor)", "major")
        note = ask("комментарий", "")

        if kind == "point-circle":
            payload = add_point(image_w, image_h)
        else:
            payload = add_box(image_w, image_h, kind)

        zone = {
            "id": rid,
            **payload,
            "severity": severity,
        }
        if note:
            zone["note"] = note

        regions.append(zone)
        print(f"Добавлено: {zone}
")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(regions, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved {len(regions)} zones to: {args.output}")
    print("Use with annotate_review.py:")
    print(
        f'python3 scripts/annotate_review.py --input "{args.image}" --output "DESIGN REVIEW REPORT/annotated-YYYYMMDD-HHMM.png" --regions-json "$(cat {args.output})" --output-scale 2'
    )


if __name__ == "__main__":
    main()
