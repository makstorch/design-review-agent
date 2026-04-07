#!/usr/bin/env python3
"""
Convert design review Markdown to readable black-and-white PDF.
No HTML rendering to avoid color glitches and shifted bullet points.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from fpdf import FPDF


def pick_font_path() -> Path:
    candidates = [
        Path('/System/Library/Fonts/Supplemental/Arial Unicode.ttf'),
        Path('/System/Library/Fonts/Supplemental/Arial.ttf'),
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
    ]
    for font_path in candidates:
        if font_path.is_file():
            return font_path
    raise SystemExit('No suitable TTF font found. Install Arial/DejaVu or pass --font /path/to/font.ttf')


def clean_inline_md(text: str) -> str:
    text = text.replace('**', '').replace('__', '')
    text = text.replace('`', '')
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1 (\2)', text)
    return text.strip()


def add_line(pdf: FPDF, text: str, style: str = '', size: int = 11, indent: int = 0, spacing: int = 6) -> None:
    pdf.set_font('ReviewFont', style=style, size=size)
    x_pos = pdf.l_margin + indent
    pdf.set_x(x_pos)
    pdf.multi_cell(pdf.w - pdf.r_margin - x_pos, spacing, text)


def md_to_pdf(md_path: Path, pdf_path: Path, font_path: Path | None) -> None:
    font = font_path or pick_font_path()
    lines = md_path.read_text(encoding='utf-8').splitlines()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    for style in ('', 'B', 'I'):
        pdf.add_font('ReviewFont', style=style, fname=str(font))
    pdf.set_text_color(0, 0, 0)

    for raw_line in lines:
        line = raw_line.rstrip("\n")
        if not line.strip():
            add_line(pdf, '', size=11, spacing=4)
            continue

        stripped = line.strip()

        # Skip markdown rulers
        if stripped in ('---', '***'):
            continue

        # Render table rows as plain rows
        if stripped.startswith('|') and stripped.endswith('|'):
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            if all(set(c) <= set('-:') for c in cells):
                continue
            row = ' | '.join(clean_inline_md(c) for c in cells)
            add_line(pdf, row, size=10, indent=6, spacing=5)
            continue

        text = clean_inline_md(stripped)

        if text.startswith('### '):
            add_line(pdf, text[4:], style='B', size=12, spacing=7)
        elif text.startswith('## '):
            add_line(pdf, text[3:], style='B', size=13, spacing=8)
        elif text.startswith('# '):
            add_line(pdf, text[2:], style='B', size=15, spacing=9)
        elif re.match(r'^\d+\)\s+', text):
            add_line(pdf, text, size=11, indent=2, spacing=6)
        elif re.match(r'^\d+\.\s+', text):
            add_line(pdf, text, size=11, indent=2, spacing=6)
        elif text.startswith('- '):
            add_line(pdf, '• ' + text[2:], size=11, indent=4, spacing=6)
        else:
            add_line(pdf, text, size=11, spacing=6)

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(pdf_path))


def main() -> None:
    parser = argparse.ArgumentParser(description='Markdown design review to PDF (plain text renderer)')
    parser.add_argument('input', type=Path, help='Path to review-*.md')
    parser.add_argument('-o', '--output', type=Path, default=None, help='Output PDF path')
    parser.add_argument('--font', type=Path, default=None, help='TTF font path (UTF-8)')
    args = parser.parse_args()

    if not args.input.is_file():
        sys.exit(f'Not found: {args.input}')

    output = args.output or args.input.with_suffix('.pdf')
    md_to_pdf(args.input, output, args.font)
    print(f'Wrote {output}')


if __name__ == '__main__':
    main()
