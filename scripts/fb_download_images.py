#!/usr/bin/env python3
"""Download unique Facebook photos and update all posts that reference them."""

from __future__ import annotations

import random
import re
import time
from collections import defaultdict
from pathlib import Path

from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("content/_drafts/fb")
ASSETS_DIR = OUTPUT_DIR / "assets"
CHROME_PROFILE = Path("facebook_chrome_profile")


def human_delay(min_s: float = 0.5, max_s: float = 2.5) -> None:
    mean = (min_s + max_s) / 2
    std = (max_s - min_s) / 4
    time.sleep(max(min_s, min(max_s, random.gauss(mean, std))))


def download_image(request, url: str, name: str) -> str | None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    if "rsrc.php" in url or "emoji.php" in url:
        return None
    ext = ".jpg"
    clean = url.split("?")[0]
    for e in [".png", ".webp", ".gif"]:
        if e in clean:
            ext = e
            break
    filename = f"{name}{ext}"
    dest = ASSETS_DIR / filename
    if dest.exists() and dest.stat().st_size > 500:
        return filename
    try:
        resp = request.get(url, headers={
            "Referer": "https://www.facebook.com/",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
        })
        if resp.ok and len(resp.body()) > 500:
            dest.write_bytes(resp.body())
            return filename
    except Exception:
        pass
    return None


def get_main_image_from_dialog(page) -> str | None:
    """Get the main (largest) image URL from a Facebook photo dialog."""
    return page.evaluate("""() => {
        // Wait for dialog to be present
        const dialog = document.querySelector('[role=dialog]');
        if (!dialog) return null;

        // Find all images in the dialog
        let best = null;
        let bestArea = 0;
        const imgs = dialog.querySelectorAll('img');
        for (const img of imgs) {
            const src = img.src || img.currentSrc || '';
            if (!src) continue;
            if (!(src.includes('scontent') || src.includes('fbcdn'))) continue;
            if (src.includes('rsrc.php') || src.includes('emoji.php')) continue;
            const w = img.naturalWidth || img.width || 0;
            const h = img.naturalHeight || img.height || 0;
            const area = w * h;
            // Must be reasonably large (not a profile pic or icon)
            if (w >= 300 && h >= 200 && area > bestArea) {
                bestArea = area;
                best = src;
            }
        }
        return best;
    }""")


def main() -> int:
    # Collect unique fbids and which posts reference them
    fbid_pattern = re.compile(r"fbid=(\d+)")
    url_pattern = re.compile(
        r"(\![^\]]*\]|[^\[]*)\]\((https?://www\.facebook\.com/photo/[^\)]+)\)"
    )

    fbid_to_url: dict[str, str] = {}
    fbid_to_posts: dict[str, list[tuple[Path, str]]] = defaultdict(list)

    for f in sorted(OUTPUT_DIR.glob("*.md")):
        if f.name.startswith("_"):
            continue
        content = f.read_text("utf-8")
        body = content.split("---", 2)[-1] if "---" in content else ""

        for match in url_pattern.finditer(body):
            fb_url = match.group(2)
            fbids = fbid_pattern.findall(fb_url)
            for fbid in fbids:
                if fbid not in fbid_to_url:
                    fbid_to_url[fbid] = fb_url
                fbid_to_posts[fbid].append((f, match.group(0)))

    print(f"Unique fbids to download: {len(fbid_to_url)}")
    print(f"Posts affected: {sum(len(v) for v in fbid_to_posts.values())}")

    downloaded = 0
    failed = 0

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE),
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            no_viewport=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        for fbid_idx, (fbid, fb_url) in enumerate(sorted(fbid_to_url.items())):
            posts = fbid_to_posts[fbid]
            slug_hint = posts[0][0].stem[:40]
            print(f"\n  [{fbid_idx+1}/{len(fbid_to_url)}] fbid={fbid} ({len(posts)} posts)")

            # Visit the photo page
            try:
                page.goto(fb_url, wait_until="domcontentloaded")
                human_delay(2, 3)

                img_url = get_main_image_from_dialog(page)
                if not img_url:
                    # Try without dialog - maybe it loaded differently
                    human_delay(1, 2)
                    img_url = get_main_image_from_dialog(page)

                if not img_url:
                    print(f"    No image found")
                    failed += 1
                    continue

                # Download with a descriptive name
                local = download_image(page.request, img_url, f"fb_{fbid}")
                if not local:
                    print(f"    Download failed")
                    failed += 1
                    continue

                print(f"    Downloaded: {local}")

                # Update all posts that reference this fbid
                for filepath, old_match in posts:
                    content = filepath.read_text("utf-8")
                    # Extract alt text from the markdown
                    alt_m = re.match(r"!\[([^\]]*)\]", old_match)
                    alt = alt_m.group(1) if alt_m else "Facebook image"
                    new_markdown = f"![{alt}](assets/{local})"
                    content = content.replace(old_match, new_markdown, 1)
                    filepath.write_text(content, encoding="utf-8")

                downloaded += 1

            except Exception as e:
                print(f"    Error: {e}")
                failed += 1

            human_delay(1, 2)
            if random.random() < 0.1:
                human_delay(3, 5)

        ctx.close()

    print(f"\nDone. Downloaded: {downloaded}, Failed: {failed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
