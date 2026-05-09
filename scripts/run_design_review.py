#!/usr/bin/env python3
"""
One-command design review pipeline for image-vs-image comparison.

Inputs:
- actual image (implementation screenshot)
- design image (reference mockup)
- optional --name "Feedback Modal" for contextual filenames

Outputs to DESIGN REVIEW REPORT/ (with --name "Feedback Modal"):
- Feedback-Modal_DD-MM-YYYY-HH-MM.md
- Feedback-Modal-annotated_DD-MM-YYYY-HH-MM.png
- Feedback-Modal_DD-MM-YYYY-HH-MM.pdf
- Feedback-Modal-source-actual_DD-MM-YYYY-HH-MM.<ext>
- Feedback-Modal-source-design_DD-MM-YYYY-HH-MM.<ext>

Without --name, falls back to legacy names: review_*.md, annotated_*.png,
review_*.pdf, source-actual_*, source-design_*.

Originals are copied via shutil.copyfile (no re-encoding); the actual screenshot
is annotated in its native resolution to preserve image quality.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
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
    """Return DD-MM-YYYY-HH-MM, all dash-separated for cross-platform safety.

    Used in filenames where colons/spaces would be unsafe. Inside reports,
    write the human form `DD-MM-YYYY HH:MM` instead.
    """
    return dt.datetime.now().strftime("%d-%m-%Y-%H-%M")


def slugify(name: str) -> str:
    """Convert a free-form screen name into a filesystem-safe slug.

    Rules: keep ASCII letters/digits, collapse runs of other chars into single
    dashes, capitalize each word so Finder shows readable names like
    "Feedback-Modal".
    """
    cleaned = re.sub(r"[^A-Za-z0-9]+", " ", name).strip()
    if not cleaned:
        return ""
    parts = [p for p in cleaned.split(" ") if p]
    return "-".join(p[:1].upper() + p[1:] for p in parts)


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


def _format_design_system_block(notes: str) -> list[str]:
    """Build the 'Соответствие дизайн-системе' block.

    If notes are empty, write the explicit "DS not provided" line so the
    section always exists and the agent can later post-process it.
    """
    header = ["", "## Соответствие дизайн-системе"]
    text = (notes or "").strip()
    if not text:
        return header + [
            "",
            "Дизайн-система не была передана, проверка выполнена только по макету/референсу.",
        ]
    body_lines = [line.rstrip() for line in text.splitlines()]
    return header + ["", *body_lines]


def _image_dims(path: Path) -> str | None:
    """Return image dimensions as `WxH px`, or None if unreadable."""
    try:
        with Image.open(path) as im:
            w, h = im.size
        return f"{w}x{h} px"
    except Exception:
        return None


def _score_breakdown(crit: int, major: int, minor: int) -> tuple[int, str]:
    """Compute score and a human-readable formula breakdown.

    Formula: score = max(0, 100 − critical×10 − major×5 − minor×2)
    """
    score = max(0, 100 - crit * 10 - major * 5 - minor * 2)
    formula = (
        "score = max(0, 100 − критичные×10 − значимые×5 − незначительные×2)"
        f"  →  100 − {crit}×10 − {major}×5 − {minor}×2 = {score}"
    )
    return score, formula


def write_report(
    md_path: Path,
    annotated_name: str,
    regions: list[dict],
    actual_path: Path,
    design_path: Path,
    title: str = "Скриншот vs Скриншот",
    source_actual_name: str | None = None,
    source_design_name: str | None = None,
    design_system_notes: str = "",
) -> None:
    """Write a design-review report skeleton.

    The script auto-detects pixel-level differences but cannot classify them
    by type (typography / color / spacing / …) or assign Impact / Effort —
    that is the agent's job during post-processing. We therefore lay out all
    eight required sections with explicit placeholders so post-processing is
    a fill-in-the-blanks pass rather than a re-write.
    """
    crit = sum(1 for r in regions if r.get("severity") == "critical")
    major = sum(1 for r in regions if r.get("severity") == "major")
    minor = sum(1 for r in regions if r.get("severity") == "minor")
    score, formula = _score_breakdown(crit, major, minor)
    verdict = "готово" if not regions else "нужны правки"

    review_dt = dt.datetime.now().strftime("%d-%m-%Y %H:%M")
    actual_dims = _image_dims(actual_path) or "размер неизвестен"
    design_dims = _image_dims(design_path) or "размер неизвестен"
    actual_label = f"{actual_dims} ({actual_path.name})"
    design_label = f"{design_dims} ({design_path.name})"

    placeholder = "_<заполнит агент>_"
    placeholder_value = "_<точное значение — заполнит агент>_"
    placeholder_fix = "_<императив с числом — заполнит агент>_"

    lines = [
        f"# Дизайн-ревью: {title}",
        "",
        (
            f"_Дата ревью: {review_dt}  ·  Реализация: {actual_label}  ·  "
            f"Макет: {design_label}  ·  Тема: {placeholder}_"
        ),
        "",
        "## Краткое резюме",
        f"Вердикт: **{verdict.capitalize()}**",
        f"Score: **{score} / 100**",
        f"Формула: `{formula}`",
        f"Ошибки: Критичные – {crit}, Значимые – {major}, Незначительные – {minor}",
        "",
        "**Top-3 правки по ROI** (Impact × 1/Effort, не по убыванию severity):",
        "1. _<императив с числом + ссылка на A* — заполнит агент>_",
        "2. _<императив с числом + ссылка на A* — заполнит агент>_",
        "3. _<императив с числом + ссылка на A* — заполнит агент>_",
        "",
        "## Что сделано хорошо",
        (
            "_2–3 буллета с фактическими совпадениями (заполняет агент). "
            "Если совпадений недостаточно — оставь строку «Совпадений недостаточно "
            "для отдельного блока.»_"
        ),
        "",
        "## Ключевые расхождения",
    ]

    if not regions:
        lines += [
            "",
            "Существенных визуальных отличий по заданным порогам не найдено.",
        ]
    else:
        lines += [
            "",
            (
                "_Авто-детект ниже сложен в группу `Other`. Агент в пост-обработке "
                "перераспределяет пункты по группам Typography / Color / Spacing / "
                "Layout / Components и заполняет числовые значения._"
            ),
            "",
            "### Other",
        ]
        for r in regions:
            rid = r["id"]
            sev_ru = {
                "critical": "Критичная",
                "major": "Значимая",
                "minor": "Незначительная",
            }.get(r["severity"], "Значимая")
            head = str(r.get("title", "Авто-детект визуального расхождения"))
            lines += [
                "",
                f"#### {rid}. {head}",
                f"- Уровень: {sev_ru}",
                f"- Impact: {placeholder}   ·   Effort: {placeholder}",
                f"- Что должно быть: {placeholder_value}",
                f"- Что по факту: {placeholder_value}",
                f"- Что исправить: {placeholder_fix}",
            ]

    lines += [
        "",
        "## Accessibility quick-check",
        "- Контраст основного текста: _<ratio vs 4.5:1 — заполнит агент>_",
        "- Контраст вспомогательного текста / caption: _<ratio — заполнит агент>_",
        "- Touch target интерактивных элементов: _<замер — заполнит агент>_",
        "- Visible focus state: _<да / нет / неизвестно — заполнит агент>_",
        (
            "- Текст на изображениях / низкий контраст плашек: "
            "_<если есть проблема — описать; иначе «не выявлено»>_"
        ),
    ]

    lines += _format_design_system_block(design_system_notes)

    lines += [
        "",
        "## Визуальные пометки",
        f"Файл: `DESIGN REVIEW REPORT/{annotated_name}`",
    ]
    if regions:
        for r in regions:
            lines.append(
                f"- {r['id']} — _<тип: typography / color / spacing / layout / "
                "components / other — заполнит агент>_"
            )
    else:
        lines.append("- _нет помеченных зон_")

    lines += [
        "",
        "## Артефакты",
        f"- PNG c пометками: `DESIGN REVIEW REPORT/{annotated_name}`",
    ]
    if source_actual_name:
        lines.append(
            f"- Исходный скриншот реализации: `DESIGN REVIEW REPORT/{source_actual_name}`"
        )
    if source_design_name:
        lines.append(
            f"- Исходный макет дизайна: `DESIGN REVIEW REPORT/{source_design_name}`"
        )
    lines.append(f"- Отчёт md/pdf: `DESIGN REVIEW REPORT/{md_path.stem}`")
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
    parser.add_argument(
        "--name",
        type=str,
        default="",
        help="Screen name for contextual filenames (e.g. 'Feedback Modal'). If empty, falls back to legacy 'review-<ts>' naming.",
    )
    parser.add_argument("--threshold", type=int, default=36, help="Diff threshold 0..255 (default 36)")
    parser.add_argument("--min-area", type=int, default=250, help="Minimum diff component area in pixels")
    parser.add_argument("--max-regions", type=int, default=8, help="Max number of diff zones in report")
    parser.add_argument(
        "--output-scale",
        type=float,
        default=1.0,
        help="Annotated PNG upscale factor (default 1.0 — keeps source resolution, no quality loss)",
    )
    parser.add_argument(
        "--design-system-notes",
        type=str,
        default="",
        help=(
            "Distilled design-system rules to embed in the report under the "
            "'Соответствие дизайн-системе' block. Multiline string. "
            "If empty, the report explicitly states that no DS was provided."
        ),
    )
    args = parser.parse_args()

    if not args.actual.is_file():
        raise SystemExit(f"Actual image not found: {args.actual}")
    if not args.design.is_file():
        raise SystemExit(f"Design image not found: {args.design}")
    if args.threshold < 0 or args.threshold > 255:
        raise SystemExit("--threshold must be in 0..255")

    ensure_report_dir()

    ts = timestamp_now()
    slug = slugify(args.name) if args.name else ""

    # Filename layout: <slug or kind>(-<role>)?_<ts>.<ext>
    # Underscore separates the descriptive part from the timestamp so the
    # eye can quickly locate the date in long names like
    # "Feedback-Modal-source-actual_09-05-2026-13-36.png".
    if slug:
        md = add_suffix_if_exists(REPORT_DIR / f"{slug}_{ts}.md")
        tail = md.stem[len(slug) + 1:]
        annotated = add_suffix_if_exists(REPORT_DIR / f"{slug}-annotated_{tail}.png")
        src_actual_dst = add_suffix_if_exists(
            REPORT_DIR / f"{slug}-source-actual_{tail}{args.actual.suffix.lower() or '.png'}"
        )
        src_design_dst = add_suffix_if_exists(
            REPORT_DIR / f"{slug}-source-design_{tail}{args.design.suffix.lower() or '.png'}"
        )
        title = args.name.strip()
    else:
        md = add_suffix_if_exists(REPORT_DIR / f"review_{ts}.md")
        tail = md.stem[len("review_"):]
        annotated = add_suffix_if_exists(REPORT_DIR / f"annotated_{tail}.png")
        src_actual_dst = add_suffix_if_exists(
            REPORT_DIR / f"source-actual_{tail}{args.actual.suffix.lower() or '.png'}"
        )
        src_design_dst = add_suffix_if_exists(
            REPORT_DIR / f"source-design_{tail}{args.design.suffix.lower() or '.png'}"
        )
        title = "Скриншот vs Скриншот"

    actual_img = Image.open(args.actual).convert("RGB")
    design_img = Image.open(args.design).convert("RGB")
    # In-memory resize ONLY for diff/region detection. Originals stay untouched.
    actual_for_diff, design_for_diff = resize_to_common(actual_img, design_img)

    regions = build_regions(
        actual=actual_for_diff,
        design=design_for_diff,
        threshold=args.threshold,
        min_area=args.min_area,
        max_regions=args.max_regions,
    )

    # Score is now derived from severity counts, not raw region count.
    # See _score_breakdown() inside write_report().

    # Annotate the ORIGINAL implementation screenshot (no resize, no quality loss).
    # build_regions stores fractional coordinates (0..1), so resolution-independent.
    if regions:
        run_annotate(args.actual, annotated, regions, output_scale=args.output_scale)
    else:
        # No regions: copy the original bytes directly to keep 100% quality.
        shutil.copyfile(args.actual, annotated)

    # Persist full-quality copies of both inputs alongside the report so the
    # designer always has access to originals from the same folder.
    shutil.copyfile(args.actual, src_actual_dst)
    shutil.copyfile(args.design, src_design_dst)

    write_report(
        md_path=md,
        annotated_name=annotated.name,
        regions=regions,
        actual_path=args.actual,
        design_path=args.design,
        title=title,
        source_actual_name=src_actual_dst.name,
        source_design_name=src_design_dst.name,
        design_system_notes=args.design_system_notes,
    )
    run_pdf(md)

    print(f"Wrote report: {md}")
    print(f"Wrote image : {annotated}")
    print(f"Wrote pdf   : {md.with_suffix('.pdf')}")
    print(f"Wrote source actual: {src_actual_dst}")
    print(f"Wrote source design: {src_design_dst}")


if __name__ == "__main__":
    main()
