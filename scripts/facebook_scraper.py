#!/usr/bin/env python3
"""Scrape Facebook posts into blog-chat markdown drafts.

Resumable — saves progress to facebook_progress.json. Safe to interrupt.

Usage:
    python scripts/facebook_scraper.py --login     # first time only
    python scripts/facebook_scraper.py --scrape    # runs until done
    python scripts/facebook_scraper.py --scrape --limit 50
"""

from __future__ import annotations

import argparse
import json
import random
import re
import unicodedata
import time
from datetime import datetime
from pathlib import Path

import dateparser
import requests
from playwright.sync_api import sync_playwright

PROGRESS_FILE = Path("facebook_progress.json")
OUTPUT_DIR = Path("content/_drafts/fb")
IMAGES_DIR = Path("content/_drafts/fb/assets")
CHROME_PROFILE = Path("facebook_chrome_profile")

FB_ACTIVITY_URL = (
    "https://www.facebook.com/100001701638652/allactivity"
    "?activity_history=false&category_key=MANAGEPOSTSPHOTOSANDVIDEOS"
    "&manage_mode=false&should_load_landing_page=false"
)


def human_delay(min_s: float = 0.5, max_s: float = 2.5) -> None:
    """Gaussian-distributed delay — humans cluster around a mean, not uniform."""
    mean = (min_s + max_s) / 2
    std = (max_s - min_s) / 4
    delay = max(min_s, min(max_s, random.gauss(mean, std)))
    time.sleep(delay)


def human_scroll(page) -> None:
    """Burst scroll with acceleration/deceleration, like a human reading a feed."""
    ticks = random.randint(2, 4)
    for i in range(ticks):
        delta = random.randint(150, 400)
        # Direct scroll via JS — more reliable than mouse.wheel for FB's containers
        page.evaluate("""(d) => {
            window.scrollBy(0, d);
            const main = document.querySelector('[role=main]');
            if (main) main.scrollTop += d;
        }""", delta)
        time.sleep(random.uniform(0.06, 0.15))

    human_delay(0.8, 3.0)


def human_move(page) -> None:
    """Random mouse movement to a non-critical area, like a human glancing around."""
    x = random.randint(100, 900)
    y = random.randint(100, 600)
    steps = random.randint(10, 30)
    page.mouse.move(x, y, steps=steps)
    time.sleep(random.uniform(0.1, 0.4))


def download_image(request, url: str, name: str) -> str | None:
    """Download image using Playwright's request API (inherits browser cookies)."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    ext = ".jpg"
    clean_url = url.split("?")[0]
    for e in [".png", ".webp", ".gif"]:
        if e in clean_url:
            ext = e
            break
    filename = f"{name}{ext}"
    dest = IMAGES_DIR / filename
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


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFC", text).strip().lower()
    text = re.sub(r"[^a-z0-9\u00e0-\u00ff]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-")[:80]


def parse_date(raw: str, reference: datetime | None = None) -> str | None:
    raw = raw.strip()
    if not raw:
        return None
    settings = {"RELATIVE_BASE": reference or datetime.now()}
    dt = dateparser.parse(raw, languages=["en", "es"], settings=settings)
    return dt.strftime("%Y-%m-%d") if dt else None


def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return {"scrolled": False, "seen": [], "exported": 0}


def scan_existing_posts() -> set[str]:
    """Scan markdown files for origin_link to avoid re-fetching."""
    urls = set()
    if not OUTPUT_DIR.exists():
        return urls
    for f in OUTPUT_DIR.glob("*.md"):
        content = f.read_text(encoding="utf-8")
        match = re.search(r'origin_link:\s*"([^"]+)"', content)
        if match:
            urls.add(match.group(1))
    return urls


def save_progress(data: dict) -> None:
    PROGRESS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def post_key(url: str) -> str:
    """Dedup by post URL — much shorter than storing text."""
    return url.strip()


def extract_entries(page) -> list[dict]:
    """Extract post entries from the Activity Log page.

    Each entry has: date, action text, privacy, time, and a View link.
    The date is in a header div *above* the entry container.
    """
    return page.evaluate("""() => {
        const viewLinks = [...document.querySelectorAll('a')]
            .filter(a => a.innerText.trim() === 'View' && a.href);

        return viewLinks.map(a => {
            // Entry container: 5 levels up from View link
            let entry = a;
            for (let i = 0; i < 5; i++) entry = entry.parentElement || entry;

            const entryText = entry.innerText || '';

            // Date header: sibling div before this entry with class x1e56ztr
            let dateStr = '';
            let prev = entry.parentElement;
            if (prev) {
                const children = [...prev.children];
                const idx = children.indexOf(entry);
                // Look backwards for the date header
                for (let i = idx - 1; i >= 0; i--) {
                    const ch = children[i];
                    if (ch.querySelector && ch.querySelector('.x1e56ztr')) {
                        dateStr = ch.querySelector('.x1e56ztr').innerText.trim();
                        break;
                    }
                    // Direct date text
                    const t = ch.innerText.trim();
                    if (/^(January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d{1,2},\\s+\\d{4}$/.test(t)) {
                        dateStr = t;
                        break;
                    }
                }
            }

            return {
                url: a.href,
                date_raw: dateStr,
                entry_text: entryText
            };
        });
    }""")


def parse_entry(entry: dict, scrape_time: datetime) -> dict | None:
    """Parse an activity log entry into structured post data."""
    text = entry["entry_text"]
    if not text:
        return None

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    action = ""
    content = ""
    privacy = ""
    time_str = ""

    privacy_values = {"Friends", "Only me", "Public", "Specific friends", "Friends except...", "Acquaintances"}
    time_re = re.compile(r"^\d{1,2}:\d{2}\s*(AM|PM)$", re.IGNORECASE)

    for line in lines:
        if line == "View":
            continue
        if line in privacy_values:
            privacy = line
            continue
        if time_re.match(line):
            time_str = line
            continue
        if not action:
            action = line
        elif not content:
            content = line

    date_str = parse_date(entry["date_raw"], reference=scrape_time)

    return {
        "text": f"{action}\n\n{content}".strip() if content else action,
        "date": date_str,
        "date_raw": entry["date_raw"],
        "url": entry["url"],
        "privacy": privacy,
        "time": time_str,
        "images": [],
        "links": [],
    }


def fetch_post_detail(page, url: str) -> dict:
    """Visit a post URL and extract post-specific images, links, videos, and full text."""
    result = {"images": [], "links": [], "videos": [], "full_text": ""}
    try:
        page.goto(url, wait_until="domcontentloaded")
        human_delay(1.5, 3.0)
        human_move(page)

        data = page.evaluate("""() => {
            const images = [];
            const seen_srcs = new Set();

            function addImg(img) {
                const src = img.src || img.currentSrc || '';
                if (!src || seen_srcs.has(src)) return;
                if (!(src.includes('scontent') || src.includes('fbcdn'))) return;
                if (src.includes('rsrc.php') || src.includes('emoji.php')) return;
                const w = img.naturalWidth || img.width || 0;
                const h = img.naturalHeight || img.height || 0;
                if (w > 0 && w < 200 && h > 0 && h < 200) return;
                seen_srcs.add(src);
                images.push({ src: src, alt: img.alt || '', width: w, height: h });
            }

            // Videos
            const videos = [];
            const seen_vids = new Set();
            document.querySelectorAll('video').forEach(v => {
                const src = v.src || '';
                if (!src || seen_vids.has(src)) return;
                if (src.startsWith('blob:')) return; // blob URLs can't be downloaded
                seen_vids.add(src);
                videos.push({
                    src: src,
                    poster: v.poster || '',
                    width: v.videoWidth || 0,
                    height: v.videoHeight || 0,
                    inDialog: !!v.closest('[role=dialog]'),
                    inArticle: !!v.closest('[role=article]')
                });
            });

            // Post content container
            const dialog = document.querySelector('[role=dialog]');
            const postEl = document.querySelector('[data-ad-rendering-role="story_message"]')
                || document.querySelector('[data-testid="post_message"]')
                || document.querySelector('[role=article]');

            // Collect images from post containers
            if (dialog) dialog.querySelectorAll('img').forEach(addImg);
            if (postEl) postEl.querySelectorAll('img').forEach(addImg);
            if (images.length === 0) document.querySelectorAll('img').forEach(addImg);
            images.sort((a, b) => (b.width * b.height) - (a.width * a.height));

            // Links
            const links = [];
            const postContainer = dialog || postEl;
            if (postContainer) {
                postContainer.querySelectorAll('a[href]').forEach(a => {
                    const href = a.href;
                    if (href && href.startsWith('http') && !href.includes('facebook.com')) {
                        links.push({ href: href, text: (a.innerText || '').trim() });
                    }
                });
            }

            // Post text — extract from story_message, skip metadata/noise
            let fullText = '';
            const storyEl = document.querySelector('[data-ad-rendering-role="story_message"]');
            if (storyEl) {
                fullText = storyEl.innerText || '';
            } else if (postEl) {
                fullText = postEl.innerText || '';
            } else if (dialog) {
                // Walk dialog children to find the text node, skip nav/header
                const children = dialog.children;
                for (let i = 0; i < children.length; i++) {
                    const child = children[i];
                    const text = child.innerText || '';
                    if (text.length > 10 && !text.startsWith('Facebook Menu')) {
                        fullText = text;
                        break;
                    }
                }
            }

            // Clean up: remove trailing noise (reactions, "Like", "Comment", etc.)
            fullText = fullText.replace(/\\nAll reactions:[\\s\\S]*$/, '');
            fullText = fullText.replace(/\\nLike\\nComment\\nShare.*$/, '');
            fullText = fullText.replace(/\\nComments\\n.*$/, '');

            return { images, links, videos, fullText };
        }""")

        result["images"] = data.get("images", [])
        result["links"] = data.get("links", [])
        result["videos"] = data.get("videos", [])
        result["full_text"] = data.get("fullText", "")
    except Exception as e:
        print(f"  Error fetching {url}: {e}")

    return result


def post_to_markdown(post: dict, index: int) -> tuple[str, str]:
    text = post["text"]
    date = post["date"] or datetime.now().strftime("%Y-%m-%d")
    slug = slugify(text[:60]) or f"fb-post-{index}"
    filename = f"{date}-{slug}-{index}.md"

    lines = []

    # Videos
    for vid in post.get("videos", []):
        lines.append(f'<video controls src="{vid["src"]}" style="width:100%; max-height:600px; border-radius:4px;"></video>')
        lines.append("")

    # Local downloaded images
    for img in post.get("local_images", []):
        alt = img["alt"] or "Facebook image"
        lines.append(f"![{alt}](assets/{img['file']})")
        lines.append("")

    # Main text
    if text:
        lines.append(re.sub(r"\n{3,}", "\n\n", text))

    # External links
    for link in post.get("links", []):
        href = link["href"]
        link_text = link["text"] or href
        if any(d in href for d in ["youtube.com", "youtu.be"]):
            lines.append("")
            lines.append(f'<iframe loading="lazy" src="{href}" title="{link_text}" style="width:100%; height:500px; border:0; border-radius:4px;"></iframe>')
        elif link_text and href:
            lines.append(f"\n[{link_text}]({href})")

    body = "\n".join(lines).strip() + "\n"

    title = text[:80].replace('"', '\\"').replace('\n', ' ').strip()
    if len(text) > 80:
        title += "..."

    tags = ["facebook-import"]
    if post.get("privacy"):
        tags.append(post["privacy"].lower().replace(" ", "-"))

    frontmatter_lines = [
        "---",
        f'title: "{title}"',
        f"created: {date}",
        f"updated: {date}",
    ]
    if post.get("url"):
        frontmatter_lines.append(f'origin_link: "{post["url"]}"')
    frontmatter_lines.append(f'description: "{title}"')
    frontmatter_lines.append(f"slug: {slug}")
    frontmatter_lines.append(f"tags: [{', '.join(tags)}]")
    frontmatter_lines.append(f"lang: es")
    frontmatter_lines.append(f"lang_group: {slug}")
    frontmatter_lines.append("---")

    return "\n".join(frontmatter_lines) + "\n\n" + body, filename


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--login", action="store_true", help="Open Facebook to log in (first time)")
    parser.add_argument("--scrape", action="store_true", help="Scrape posts (resumable)")
    parser.add_argument("--limit", type=int, default=200, help="Max posts to export (default: 200)")
    args = parser.parse_args()

    if not args.login and not args.scrape:
        parser.print_help()
        return 1

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE),
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            no_viewport=True,
        )

        if args.login:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
            print("Log in in the browser. Close the window when done.")
            try:
                page.wait_for_event("close", timeout=0)
            except Exception:
                pass
            ctx.close()
            return 0

        if args.scrape:
            progress = load_progress()
            scrape_time = datetime.now()

            # Tab 1: activity log (stays open)
            log_tab = ctx.pages[0] if ctx.pages else ctx.new_page()
            # Tab 2: post fetcher
            fetch_tab = ctx.new_page()

            # Scroll + extract entries as we go (virtual scrolling — only ~25 in DOM at a time)
            all_entries = []
            seen_urls = set(progress["seen"])
            # Also mark already-exported URLs so we don't re-fetch
            exported_urls = scan_existing_posts()
            seen_urls.update(exported_urls)

            if not progress["scrolled"]:
                print("--- Scrolling & extracting entries ---")
                log_tab.goto(FB_ACTIVITY_URL, wait_until="domcontentloaded")
                human_delay(2.0, 4.0)
                human_move(log_tab)

                prev, stable = 0, 0
                no_new_count = 0
                while stable < 10:
                    human_scroll(log_tab)
                    h = log_tab.evaluate("document.body.scrollHeight")

                    batch = extract_entries(log_tab)
                    new_in_batch = 0
                    for e in batch:
                        if e["url"] not in seen_urls:
                            seen_urls.add(e["url"])
                            all_entries.append(e)
                            new_in_batch += 1

                    if new_in_batch > 0:
                        no_new_count = 0
                    else:
                        no_new_count += 1

                    if h == prev:
                        stable += 1
                        print(f"  Stable ({stable}/10) — {len(all_entries)} entries (+{new_in_batch})")
                    else:
                        stable = 0
                        print(f"  Scrolled — {len(all_entries)} entries (+{new_in_batch})")
                    prev = h

                    # If height stable but no new entries for 3 rounds, try harder scrolling
                    if no_new_count >= 3:
                        log_tab.evaluate("window.scrollTo(0, 0)")
                        human_delay(1.0, 2.0)
                        for _ in range(3):
                            log_tab.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                            log_tab.evaluate("""() => {
                                const main = document.querySelector('[role=main]');
                                if (main) main.scrollTop = main.scrollHeight;
                            }""")
                            human_delay(2.0, 4.0)
                        no_new_count = 0

                    if random.random() < 0.08:
                        log_tab.mouse.wheel(0, -random.randint(100, 300))
                        human_delay(0.5, 1.5)

                progress["scrolled"] = True
                progress["seen"] = list(seen_urls)
                save_progress(progress)
            else:
                print("Already scrolled. Reloading page...")
                log_tab.goto(FB_ACTIVITY_URL, wait_until="domcontentloaded")
                human_delay(2.0, 4.0)
                batch = extract_entries(log_tab)
                for e in batch:
                    if e["url"] not in seen_urls:
                        seen_urls.add(e["url"])
                        all_entries.append(e)

            print(f"\n{len(all_entries)} total unique entries collected")

            # Parse entries
            new_posts = []
            for entry in all_entries:
                post = parse_entry(entry, scrape_time)
                if post and post["text"]:
                    new_posts.append(post)

            print(f"{len(new_posts)} posts to fetch\n")

            # Fetch each post in the second tab, save immediately
            if new_posts:
                OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
                saved = 0
                for i, post in enumerate(new_posts):
                    if saved >= args.limit:
                        break
                    url_short = post["url"][:70]
                    print(f"  [{i+1}/{len(new_posts)}] {url_short}...")

                    human_move(fetch_tab)
                    human_delay(1.0, 2.5)
                    detail = fetch_post_detail(fetch_tab, post["url"])
                    if detail["full_text"]:
                        post["text"] = detail["full_text"]
                    post["links"] = detail["links"]
                    post["videos"] = detail["videos"]

                    # Download post images locally
                    local_images = []
                    for j, img in enumerate(detail["images"]):
                        img_name = f"{slugify(post['text'][:40])}_{j}"
                        local = download_image(fetch_tab.request, img["src"], img_name)
                        if local:
                            local_images.append({"file": local, "alt": img["alt"]})
                    post["local_images"] = local_images

                    md, filename = post_to_markdown(post, progress["exported"])
                    (OUTPUT_DIR / filename).write_text(md, encoding="utf-8")
                    progress["exported"] += 1
                    saved += 1
                    save_progress(progress)

                    human_delay(2.0, 4.0)
                    if random.random() < 0.1:
                        human_delay(4.0, 7.0)

                print(f"\nSaved {saved} posts to {OUTPUT_DIR}/")
            else:
                print("Nothing new to fetch.")

            print(f"Total exported: {progress['exported']}")
            fetch_tab.close()
            ctx.close()
            return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
