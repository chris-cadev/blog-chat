#!/usr/bin/env python3
"""Download missing images for Facebook posts.

Usage: python scripts/fb_download_missing.py --batch-file FILE BATCH_NUM
"""
import sys, re, random, time
from pathlib import Path
from playwright.sync_api import sync_playwright

ASSETS_DIR = Path("content/_drafts/fb/assets")
CHROME_PROFILE = Path("facebook_chrome_profile")

DOWNLOAD_JS = """() => {
    const seen = new Set();
    const images = [];
    document.querySelectorAll('img').forEach(img => {
        const src = img.src || img.currentSrc || '';
        if (!src || seen.has(src)) return;
        if (!(src.includes('scontent') || src.includes('fbcdn'))) return;
        if (src.includes('rsrc.php') || src.includes('emoji.php')) return;
        const w = img.naturalWidth || img.width || 0;
        const h = img.naturalHeight || img.height || 0;
        if (w > 0 && h > 0 && w < 200 && h < 200) return;
        seen.add(src);
        images.push({ src, alt: img.alt || '', width: w, height: h });
    });
    images.sort((a, b) => (b.width * b.height) - (a.width * a.height));
    return images;
}"""


def human_delay(a=0.5, b=2.5):
    mean = (a + b) / 2
    std = (b - a) / 4
    time.sleep(max(a, min(b, random.gauss(mean, std))))


def main():
    if len(sys.argv) < 2 or sys.argv[1] != "--batch-file":
        print("Usage: fb_download_missing.py --batch-file FILE BATCH_NUM")
        return 1

    batch_file = Path(sys.argv[2])
    profile_num = sys.argv[3] if len(sys.argv) > 3 else "0"
    chrome_dir = Path(f"facebook_chrome_profile_{profile_num}")

    lines = batch_file.read_text().strip().split("\n")
    entries = []
    for line in lines:
        parts = line.split("\t", 1)
        if len(parts) == 2:
            entries.append((parts[0].strip(), parts[1].strip()))

    print(f"Entries to process: {len(entries)}")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(chrome_dir),
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            no_viewport=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        downloaded = 0
        for i, (asset_name, url) in enumerate(entries):
            dest = ASSETS_DIR / asset_name
            if dest.exists() and dest.stat().st_size > 500:
                print(f"[{i+1}] SKIP (exists): {asset_name}")
                downloaded += 1
                continue

            print(f"[{i+1}/{len(entries)}] {asset_name}")
            try:
                page.goto(url, wait_until="domcontentloaded")
                human_delay(2, 4)

                images = page.evaluate(DOWNLOAD_JS)
                if not images:
                    # Try unknown fallback
                    images = page.evaluate(DOWNLOAD_JS)

                # Find the largest image
                for img in images:
                    resp = ctx.request.get(img["src"], headers={
                        "Referer": "https://www.facebook.com/",
                        "Accept": "image/*",
                    })
                    if resp.ok and len(resp.body()) > 500:
                        dest.write_bytes(resp.body())
                        print(f"  Downloaded: {len(resp.body())} bytes")
                        downloaded += 1
                        break
                    else:
                        print(f"  Failed: status={resp.status}")
            except Exception as e:
                print(f"  ERROR: {e}")

            human_delay(1, 3)

        ctx.close()

    print(f"\nDownloaded: {downloaded}/{len(entries)}")


if __name__ == "__main__":
    raise SystemExit(main())
