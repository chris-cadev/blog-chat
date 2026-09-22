#!/usr/bin/env python3
"""Fix wrong dates in Facebook markdown files by extracting creation_time from page HTML.

Usage:
    python scripts/fb_fix_dates.py                      # fix all files with 2026-09-21
    python scripts/fb_fix_dates.py --batch-file FILE N   # process batch file with profile N
"""
from __future__ import annotations
import json, re, sys, random, time
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("content/_drafts/fb")
CHROME_PROFILE = Path("facebook_chrome_profile")

# Extract creation_time from the page's embedded JSON
TIMESTAMP_JS = """() => {
    const scripts = document.querySelectorAll('script[type="application/json"]');
    for (const s of scripts) {
        const t = s.textContent || '';
        const match = t.match(/"creation_time":\\s*(\d{10,13})/);
        if (match) return match[1];
    }
    return '';
}"""


def human_delay(a=0.5, b=2.5):
    mean = (a + b) / 2
    std = (b - a) / 4
    time.sleep(max(a, min(b, random.gauss(mean, std))))


def fix_date(filepath: Path, page) -> bool:
    content = filepath.read_text(encoding="utf-8")
    m = re.search(r'origin_link:\s*"([^"]+)"', content)
    if not m:
        return False
    url = m.group(1)

    try:
        page.goto(url, wait_until="domcontentloaded")
        human_delay(2, 4)
        ts = page.evaluate(TIMESTAMP_JS)
    except Exception as e:
        print(f"    Error: {e}")
        return False

    if not ts or not ts.isdigit():
        print(f"    No timestamp found")
        return False

    try:
        dt = datetime.fromtimestamp(int(ts))
        new_date = dt.strftime("%Y-%m-%d")
    except (ValueError, OSError):
        print(f"    Invalid timestamp: {ts}")
        return False

    new_content = re.sub(r"created: \d{4}-\d{2}-\d{2}", f"created: {new_date}", content, count=1)
    new_content = re.sub(r"updated: \d{4}-\d{2}-\d{2}", f"updated: {new_date}", new_content, count=1)
    filepath.write_text(new_content, encoding="utf-8")
    print(f"    {new_date} (from {ts})")
    return True


def main():
    # Parse args
    batch_file = None
    profile_num = "0"
    if len(sys.argv) > 2 and sys.argv[1] == "--batch-file":
        batch_file = Path(sys.argv[2])
        profile_num = sys.argv[3] if len(sys.argv) > 3 else "0"

    chrome_dir = Path(f"facebook_chrome_profile_{profile_num}") if batch_file else CHROME_PROFILE

    # Find files to fix
    if batch_file:
        filenames = [f.strip() for f in batch_file.read_text().splitlines() if f.strip()]
        files = [OUTPUT_DIR / fn for fn in filenames if (OUTPUT_DIR / fn).exists()]
    else:
        files = []
        for f in sorted(OUTPUT_DIR.glob("*.md")):
            content = f.read_text()
            m = re.search(r"created:\s*(\d{4}-\d{2}-\d{2})", content)
            if m and m.group(1) == "2026-09-21":
                o = re.search(r'origin_link:\s*"([^"]+)"', content)
                if o:
                    files.append(f)

    print(f"Files to fix: {len(files)}")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(chrome_dir),
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            no_viewport=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        fixed = 0
        for i, f in enumerate(files):
            print(f"[{i+1}/{len(files)}] {f.name}")
            if fix_date(f, page):
                fixed += 1
            human_delay(1, 2)

        ctx.close()

    print(f"\nFixed {fixed}/{len(files)} dates.")


if __name__ == "__main__":
    raise SystemExit(main())
