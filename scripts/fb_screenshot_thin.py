#!/usr/bin/env python3
"""Take screenshots of empty/thin Facebook posts and rebuild them with screenshot + link.

These posts have no meaningful text content (just a name, timestamp, or nothing).
Instead of showing empty content, we take a screenshot of the Facebook post/dialog
and show it as an image with a 'ver post completo' link.
"""

from __future__ import annotations

import random
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("content/_drafts/fb")
ASSETS_DIR = OUTPUT_DIR / "assets"
CHROME_PROFILE = Path("facebook_chrome_profile_screenshot")

# Posts that need screenshots (empty or near-empty body)
THIN_POSTS = [
    "2011-07-19-christian-camacho-15y-esta-atrasado-el-sonido-u-u.md",
    "2012-04-28-christian-camacho-14y-grasias-c.md",
    "2016-03-19-christian-camacho-added-a-new-video-d-154.md",
    "2016-05-07-the-kingdom-150.md",
    "2021-08-02-victor-gutierrez-5y-a-ver-tocame-una-reply.md",
    "2021-12-24-juditg-rodriguez-4y-reply.md",
    "2022-05-03-alondra-portilla-4y-propiedad-de-alondra-marca-registrad.md",
    "2023-09-30-christian-said-2y-fresco-pa-reply.md",
    "2025-03-28-christian-camacho-1y-https-x-com-raphael-erba-status-1.md",
    "2025-10-05-jorge-luis-avila-madrigal-50w-juegas-mine-reply.md",
]


def human_delay(min_s: float = 0.5, max_s: float = 2.5) -> None:
    mean = (min_s + max_s) / 2
    std = (max_s - min_s) / 4
    delay = max(min_s, min(max_s, random.gauss(mean, std)))
    time.sleep(delay)


def human_move(page) -> None:
    x = random.randint(100, 900)
    y = random.randint(100, 600)
    page.mouse.move(x, y, steps=random.randint(10, 30))
    time.sleep(random.uniform(0.1, 0.4))


def parse_frontmatter(filepath: Path) -> dict:
    content = filepath.read_text(encoding="utf-8")
    match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            fm[key.strip()] = val.strip().strip('"')
    return fm


def screenshot_post(page, url: str, slug: str) -> str | None:
    """Visit a Facebook post URL and screenshot the post content (not full page)."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    screenshot_name = f"{slug}_post.png"
    dest = ASSETS_DIR / screenshot_name

    try:
        page.goto(url, wait_until="domcontentloaded")
        human_delay(3, 5)
        human_move(page)

        # Try to find the post element and screenshot just that
        # Strategy 1: dialog (most common for photo/video posts)
        dialog = page.query_selector("[role=dialog]")
        if dialog:
            dialog.screenshot(path=str(dest))
            return screenshot_name

        # Strategy 2: article
        article = page.query_selector("[role=article]")
        if article:
            article.screenshot(path=str(dest))
            return screenshot_name

        # Strategy 3: story_message
        story = page.query_selector('[data-ad-rendering-role="story_message"]')
        if story:
            story.screenshot(path=str(dest))
            return screenshot_name

        # Strategy 4: clip to viewport center (600x600)
        page.screenshot(
            path=str(dest),
            clip={"x": 100, "y": 50, "width": 600, "height": 600},
        )
        return screenshot_name

    except Exception as e:
        print(f"    Screenshot error: {e}")
        return None


def download_image(request, url: str, name: str) -> str | None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    if "rsrc.php" in url or "emoji.php" in url:
        return None
    ext = ".jpg"
    clean_url = url.split("?")[0]
    for e in [".png", ".webp", ".gif"]:
        if e in clean_url:
            ext = e
            break
    filename = f"{name}{ext}"
    dest = ASSETS_DIR / filename
    if dest.exists():
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


def download_video(request, url: str, name: str) -> str | None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{name}.mp4"
    dest = ASSETS_DIR / filename
    if dest.exists() and dest.stat().st_size > 1000:
        return filename
    try:
        resp = request.get(url, headers={"Referer": "https://www.facebook.com/"})
        if resp.ok and len(resp.body()) > 1000:
            dest.write_bytes(resp.body())
            return filename
    except Exception:
        pass
    return None


def extract_content(page) -> dict:
    """Extract any available content (images, videos, text)."""
    return page.evaluate("""() => {
        const seenSrcs = new Set();
        const images = [];
        document.querySelectorAll('img').forEach(img => {
            const src = img.src || img.currentSrc || '';
            if (!src || seenSrcs.has(src)) return;
            if (!(src.includes('scontent') || src.includes('fbcdn'))) return;
            if (src.includes('rsrc.php') || src.includes('emoji.php')) return;
            const w = img.naturalWidth || 0;
            const h = img.naturalHeight || 0;
            if (w < 200 && h < 200) return;
            seenSrcs.add(src);
            images.push({ src, w, h });
        });
        images.sort((a, b) => (b.w * b.h) - (a.w * a.h));

        const videos = [];
        const seenVids = new Set();
        document.querySelectorAll('video[src]:not([src^="blob:"])').forEach(v => {
            if (seenVids.has(v.src)) return;
            seenVids.add(v.src);
            videos.push({ src: v.src });
        });

        let text = '';
        const story = document.querySelector('[data-ad-rendering-role="story_message"]');
        if (story) text = story.innerText || '';
        if (!text.trim()) {
            const article = document.querySelector('[role=article]');
            if (article) text = article.innerText || '';
        }
        text = text.replace(/\\nAll reactions:[\\s\\S]*$/, '');
        text = text.replace(/\\nLike\\nComment\\nShare.*$/, '');
        text = text.replace(/\\nComments\\n.*$/, '');
        text = text.trim();

        return { text, images: images.slice(0, 3), videos: videos.slice(0, 1) };
    }""")


def build_markdown(fm: dict, screenshot: str | None, data: dict) -> str:
    lines = []

    # Screenshot first
    if screenshot:
        lines.append(f"![Facebook post](assets/{screenshot})")
        lines.append("")

    # Videos
    for vid in data.get("videos", []):
        local = vid.get("local_file")
        src = f"assets/{local}" if local else vid["src"]
        lines.append(f'<video controls src="{src}" style="width:100%; max-height:600px; border-radius:4px;"></video>')
        lines.append("")

    # Images (if any beyond screenshot)
    for img in data.get("images", []):
        fk = img.get("file") or ""
        if fk:
            lines.append(f"![Facebook image](assets/{fk})")
        elif img.get("src"):
            lines.append(f"![Facebook image]({img['src']})")
        lines.append("")

    # Text (if meaningful)
    text = data.get("text", "")
    # Filter out garbage
    garbage = ("Christian Camacho", "Notifications", "Menu", "Facebook", "See all")
    if text and not any(text.strip().startswith(g) for g in garbage) and len(text.strip()) > 10:
        lines.append(text)
        lines.append("")

    # Link to original post
    origin = fm.get("origin_link", "")
    if origin:
        lines.append(f"[Ver post completo en Facebook]({origin})")
        lines.append("")

    body = "\n".join(lines).strip() + "\n"

    title = fm.get("title", "")
    created = fm.get("created", "")
    slug = fm.get("slug", "")
    tags = fm.get("tags", "facebook-import")
    lang = fm.get("lang", "es")
    desc = text[:160].replace('"', '\\"').replace("\n", " ").strip() if text else title

    return "\n".join([
        "---",
        f'title: "{title}"',
        f"created: {created}",
        f"updated: {created}",
        f'origin_link: "{origin}"',
        f'description: "{desc}"',
        f"slug: {slug}",
        f"tags: {tags}",
        f"lang: {lang}",
        f"lang_group: {slug}",
        "---",
        "",
        body,
    ])


def main() -> int:
    print(f"Processing {len(THIN_POSTS)} thin posts...")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE),
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            no_viewport=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        fixed = 0
        for i, filename in enumerate(THIN_POSTS):
            filepath = OUTPUT_DIR / filename
            if not filepath.exists():
                print(f"  [{i+1}] {filename} NOT FOUND")
                continue

            fm = parse_frontmatter(filepath)
            origin = fm.get("origin_link", "")
            slug = fm.get("slug", filepath.stem)

            if not origin:
                print(f"  [{i+1}] {filename} NO URL")
                continue

            print(f"  [{i+1}] {filename[:55]}...", end=" ", flush=True)

            # Skip if already has screenshot
            existing = filepath.read_text("utf-8")
            if f"assets/{slug}_post.png" in existing:
                print("SKIP (already has screenshot)")
                continue

            try:
                # Check if browser is still alive, relaunch if not
                try:
                    page.goto("about:blank", timeout=3000)
                except Exception:
                    print("(relaunching browser)...", end=" ", flush=True)
                    try:
                        ctx.close()
                    except Exception:
                        pass
                    ctx = p.chromium.launch_persistent_context(
                        user_data_dir=str(CHROME_PROFILE),
                        headless=False,
                        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                        no_viewport=True,
                    )
                    page = ctx.pages[0] if ctx.pages else ctx.new_page()

                # Extract any available content
                page.goto(origin, wait_until="domcontentloaded")
                human_delay(3, 5)
                human_move(page)

                data = extract_content(page)

                # Take screenshot
                screenshot = screenshot_post(page, origin, slug)

                # Download any images/videos found
                local_images = []
                for j, img in enumerate(data.get("images", [])):
                    img_name = f"{slug}_{j}"
                    local = download_image(page.request, img["src"], img_name)
                    if local:
                        local_images.append({"file": local})
                data["images"] = local_images

                local_videos = []
                for j, vid in enumerate(data.get("videos", [])):
                    vid_name = f"{slug}_v{j}"
                    local = download_video(page.request, vid["src"], vid_name)
                    local_videos.append({"src": vid["src"], "local_file": local})
                data["videos"] = local_videos

                md = build_markdown(fm, screenshot, data)
                filepath.write_text(md, encoding="utf-8")

                parts = ["screenshot" if screenshot else "no-screenshot"]
                if local_images:
                    parts.append(f"{len(local_images)} imgs")
                if local_videos:
                    parts.append(f"{len(local_videos)} vids")
                print(f"OK ({', '.join(parts)})")
                fixed += 1

            except Exception as e:
                print(f"ERR: {e}")

            human_delay(2, 4)

        ctx.close()

    print(f"\nDone. Fixed {fixed}/{len(THIN_POSTS)} posts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
