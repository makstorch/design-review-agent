#!/usr/bin/env python3
from playwright.sync_api import sync_playwright
from pathlib import Path
import argparse

p=argparse.ArgumentParser()
p.add_argument('--url',required=True)
p.add_argument('--output',required=True)
args=p.parse_args()

out=Path(args.output)
out.parent.mkdir(parents=True, exist_ok=True)
with sync_playwright() as pw:
    browser=pw.chromium.launch()
    page=browser.new_page(viewport={"width":1920,"height":1080})
    page.goto(args.url, wait_until='networkidle', timeout=120000)
    page.screenshot(path=str(out), full_page=True)
    browser.close()
print(f'Wrote {out}')
