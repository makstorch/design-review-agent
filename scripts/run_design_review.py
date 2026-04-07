#!/usr/bin/env python3
"""
One-command design review pipeline for image-vs-image comparison.

Inputs:
- actual image (implementation screenshot)
- design image (reference mockup)

Outputs to DESIGN REVIEW REPORT/:
- review-YYYYMMDD-HHMM.md
- annotated-YYYYMMDD-HHMM.png
- review-YYYYMMDD-HHMM.pdf
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from collections import deque
from pathlib import Path

from PIL import Image, ImageChops, ImageOps


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "DESIGN REVIEW REPORT"


def ensure_report_dir() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    keep = REPORT_DIR / ".gitkeep"
    if not keep.exists():
        keep.write_text("", encoding="utf-8")


def timestamp_now() -> str:
    return dt.datetime.now().strftime("%Y%m%d-%H%M")


def add_suffix_if_exists(path: Path) -> Path:
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    i = 1
    while True:
        candidate = parent / f"{stem}-{i:02d}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def resize_to_common(actual: Image.Image, design: Image.Image) -> tuple[Image.Image, Image.Image]:
    # Prefer design resolution as canonical layout target.
    target = design.size
    if actual.size != target:
        actual = actual.resize(target, Image.Resampling.LANCZOS)
    return actual, design


def connected_components(mask: Image.Image, min_area: int) -> list[tuple[int, int, int, int, int]]:
    """
    Returns components as tuples: (x0, y0, x1, y1, area)
    """
    w, h = mask.size
    px = mask.load()
    visited = bytearray(w * h)
    comps: list[tuple[int, int, int, int, int]] = []

    def idx(x: int, y: int) -> int:
        return y * w + x

    for y in range(h):
        for x in range(w):
            if px[x, y] == 0:
                continue
            i = idx(x, y)
            if visited[i]:
                continue
            visited[i] = 1
            q = deque([(x, y)])
            min_x = max_x = x
            min_y = max_y = y
            area = 0
            while q:
                cx, cy = q.popleft()
                area += 1
                if cx < min_x:
                    min_x = cx
                if cx > max_x:
                    max_x = cx
                if cy < min_y:
                    min_y = cy
                if cy > max_y:
                    max_y = cy
                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):
                    if nx < 0 or ny < 0 or nx >= w or ny >= h:
                        continue
                    ni = idx(nx, ny)
                    if visited[ni] or px[nx, ny] == 0:
                        continue
                    visited[ni] = 1
                    q.append((nx, ny))
            if area >= min_area:
                comps.append((min_x, min_y, max_x + 1, max_y + 1, area))
    return comps


def build_regions(
    actual: Image.Image,
    design: Image.Image,
    threshold: int,
    min_area: int,
    max_regions: int,
) -> list[dict]:
    # Difference mask in grayscale.
    diff = ImageChops.difference(actual, design).convert("L")
    # Slight blur replacement via autocontrast to emphasize structural diffs.
    diff = ImageOps.autocontrast(diff)
    mask = diff.point(lambda p: 255 if p >= threshold else 0)

    comps = connected_components(mask, min_area=min_area)
    if not comps:
        return []

    # Keep largest regions, then order selected zones top-to-bottom for readable IDs.
    comps.sort(key=lambda c: c[4], reverse=True)
    top = comps[:max_regions]
    top.sort(key=lambda c: (c[1], c[0]))
    w, h = actual.size

    def infer_title_and_component(x0: int, y0: int, x1: int, y1: int, w: int, h: int) -> tuple[str, str]:
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        rw = max(1, x1 - x0)
        rh = max(1, y1 - y0)
        ratio = rw / rh

        y_rel = cy / h
        x_rel = cx / w
        area_rel = (rw * rh) / max(1, w * h)

        if y_rel < 0.12:
            return ("Расхождение в верхнем блоке", "шапка / верхняя навигация")
        if 0.12 <= y_rel < 0.34:
            return ("Расхождение в hero-секции", "hero / основной первый экран")
        if y_rel > 0.74 and 0.25 <= x_rel <= 0.75:
            return ("Расхождение в блоке цены и CTA", "цена / финальная кнопка")
        if ratio > 2.4 and area_rel > 0.02:
            return ("Расхождение в горизонтальном контент-блоке", "галерея / список карточек")
        if area_rel < 0.004:
            return ("Локальное расхождение элемента", "локальный UI-элемент")
        if y_rel > 0.88:
            return ("Расхождение в нижнем блоке", "футер / нижняя часть страницы")
        return ("Расхождение в контентном блоке", "контентная секция")

    regions_raw: list[dict] = []
    for (x0, y0, x1, y1, area) in top:
        # Pad a little for readability.
        pad_x = max(6, int((x1 - x0) * 0.08))
        pad_y = max(6, int((y1 - y0) * 0.08))
        x0 = max(0, x0 - pad_x)
        y0 = max(0, y0 - pad_y)
        x1 = min(w, x1 + pad_x)
        y1 = min(h, y1 + pad_y)

        severity = "critical" if area > (w * h * 0.02) else ("major" if area > (w * h * 0.008) else "minor")
        title, component = infer_title_and_component(x0, y0, x1, y1, w, h)
        cx = (x0 + x1) / 2
        cy = (y0 + y1) / 2
        radius = max(16, int(max(x1 - x0, y1 - y0) * 0.35))
        regions_raw.append(
            {
                "kind": "point-circle",
                "cx": cx / w,
                "cy": cy / h,
                "radius": radius,
                "severity": severity,
                "note": "",
                "title": title,
                "component": component,
            }
        )
    counters = {"A": 0, "B": 0, "C": 0}
    regions: list[dict] = []
    for r in regions_raw:
        tier = {"critical": "A", "major": "B", "minor": "C"}.get(str(r["severity"]), "C")
        counters[tier] += 1
        r["id"] = f"{tier}{counters[tier]}"
        regions.append(r)
    return regions


def write_report(
    md_path: Path,
    annotated_name: str,
    regions: list[dict],
    score: int,
    actual_path: Path,
    design_path: Path,
) -> None:
    crit = sum(1 for r in regions if r.get("severity") == "critical")
    major = sum(1 for r in regions if r.get("severity") == "major")
    minor = sum(1 for r in regions if r.get("severity") == "minor")
    verdict = "готово" if not regions else "нужны правки"
    top_actions = [
        "Проверить и скорректировать зоны с критичными отличиями",
        "Согласовать отступы, размеры и типографику в отмеченных блоках",
        "Перепроверить экран после правок и перегенерировать отчёт",
    ]
    lines = [
        "# Дизайн-ревью: Скриншот vs Скриншот",
        "",
        "## Краткое резюме",
        f"Вердикт: **{verdict.capitalize()}**",
        f"Процент соответствия: **{score} / 100**",
        f"Ошибки: Критичные – {crit}, Значимые – {major}, Незначительные – {minor}",
        "",
        "Что исправить в первую очередь:",
        f"  1. {top_actions[0]}",
        f"  2. {top_actions[1]}",
        f"  3. {top_actions[2]}",
        "",
        "## Несоответствия",
    ]
    if not regions:
        lines += [
            "",
            "Существенных визуальных отличий по заданным порогам не найдено.",
        ]
    else:
        for idx, r in enumerate(regions, start=1):
            rid = r["id"]
            sev = {"critical": "Критичная", "major": "Значимая", "minor": "Незначительная"}.get(r["severity"], "Значимая")
            title = str(r.get("title", "Авто-детект визуального расхождения"))
            component = str(r.get("component", "уточнить по отмеченной зоне"))
            lines += [
                "",
                f"### {idx}. {title}",
                f"Уровень: {sev} ({rid})",
                f"Компонент: {component}",
                "",
                "- Что должно быть: соответствие референсному дизайну",
                "- Что по факту: обнаружено визуальное расхождение в отмеченной зоне",
                "- Что исправить: сверить размер/позицию/контент в зоне и привести к макету",
            ]
    lines += [
        "",
        "## Артефакты",
        f"- PNG c отмеченными несоответствиями: `DESIGN REVIEW REPORT/{annotated_name}`",
        "- Легенда зон: " + ", ".join(r["id"] for r in regions) if regions else "- Легенда зон: —",
        f"- Отчет в формате pdf и md: `DESIGN REVIEW REPORT/{md_path.stem}`",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_pdf(md_path: Path) -> None:
    script = ROOT / "scripts" / "review_to_pdf.py"
    subprocess.run([sys.executable, str(script), str(md_path)], check=True)


def run_annotate(actual_path: Path, output_path: Path, regions: list[dict], output_scale: float) -> None:
    script = ROOT / "scripts" / "annotate_review.py"
    cmd = [
        sys.executable,
        str(script),
        "--input",
        str(actual_path),
        "--output",
        str(output_path),
        "--regions-json",
        json.dumps(regions, ensure_ascii=False),
        "--output-scale",
        str(output_scale),
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Automatic design review pipeline (image vs image)")
    parser.add_argument("--actual", required=True, type=Path, help="Implementation screenshot image")
    parser.add_argument("--design", required=True, type=Path, help="Design reference image")
    parser.add_argument("--threshold", type=int, default=36, help="Diff threshold 0..255 (default 36)")
    parser.add_argument("--min-area", type=int, default=250, help="Minimum diff component area in pixels")
    parser.add_argument("--max-regions", type=int, default=8, help="Max number of diff zones in report")
    parser.add_argument("--output-scale", type=float, default=2.0, help="Annotated PNG upscale factor")
    args = parser.parse_args()

    if not args.actual.is_file():
        raise SystemExit(f"Actual image not found: {args.actual}")
    if not args.design.is_file():
        raise SystemExit(f"Design image not found: {args.design}")
    if args.threshold < 0 or args.threshold > 255:
        raise SystemExit("--threshold must be in 0..255")

    ensure_report_dir()

    ts = timestamp_now()
    md = add_suffix_if_exists(REPORT_DIR / f"review-{ts}.md")
    # Keep identical timestamp stem for paired files.
    stem = md.stem.replace("review-", "")
    annotated = add_suffix_if_exists(REPORT_DIR / f"annotated-{stem}.png")

    actual_img = Image.open(args.actual).convert("RGB")
    design_img = Image.open(args.design).convert("RGB")
    actual_img, design_img = resize_to_common(actual_img, design_img)

    regions = build_regions(
        actual=actual_img,
        design=design_img,
        threshold=args.threshold,
        min_area=args.min_area,
        max_regions=args.max_regions,
    )
    score = max(0, int(100 - min(70, len(regions) * 8)))

    # Save resized actual temp to ensure same coordinate space in annotation
    tmp_actual = REPORT_DIR / f".tmp-actual-{stem}.png"
    actual_img.save(tmp_actual)
    try:
        if regions:
            run_annotate(tmp_actual, annotated, regions, output_scale=args.output_scale)
        else:
            # produce a clean annotated file even when no issues found
            actual_img.save(annotated)
        write_report(
            md_path=md,
            annotated_name=annotated.name,
            regions=regions,
            score=score,
            actual_path=args.actual,
            design_path=args.design,
        )
        run_pdf(md)
    finally:
        if tmp_actual.exists():
            tmp_actual.unlink()

    print(f"Wrote report: {md}")
    print(f"Wrote image : {annotated}")
    print(f"Wrote pdf   : {md.with_suffix('.pdf')}")


if __name__ == "__main__":
    main()
