#!/usr/bin/env python3
"""Re-scrape bad Facebook posts using render-type-aware extraction strategies.

Reads content/_drafts/fb/_rescrape_list.json (list of filenames), visits each
URL, classifies the render type, then applies the best extraction strategy for
that type.

Usage:
    python scripts/fb_rescrape_bad.py          # process all
    python scripts/fb_rescrape_bad.py --batch 5 # process 5 at a time
"""

from __future__ import annotations

import argparse
import json
import random
import re
import time
from datetime import datetime
from pathlib import Path

import dateparser
from playwright.sync_api import sync_playwright

RESCRAPE_LIST = Path("content/_drafts/fb/_rescrape_list.json")
OUTPUT_DIR = Path("content/_drafts/fb")
IMAGES_DIR = Path("content/_drafts/fb/assets")
CHROME_PROFILE = Path("facebook_chrome_profile")


# ---------------------------------------------------------------------------
# Helpers (shared pattern with fb_reextract.py)
# ---------------------------------------------------------------------------

def parse_date(raw: str, reference: datetime | None = None) -> str | None:
    raw = raw.strip()
    if not raw:
        return None
    settings = {"RELATIVE_BASE": reference or datetime.now()}
    dt = dateparser.parse(raw, languages=["en", "es"], settings=settings)
    return dt.strftime("%Y-%m-%d") if dt else None


def human_delay(min_s: float = 0.5, max_s: float = 2.5) -> None:
    mean = (min_s + max_s) / 2
    std = (max_s - min_s) / 4
    delay = max(min_s, min(max_s, random.gauss(mean, std)))
    time.sleep(delay)


def human_move(page) -> None:
    x = random.randint(100, 900)
    y = random.randint(100, 600)
    steps = random.randint(10, 30)
    page.mouse.move(x, y, steps=steps)
    time.sleep(random.uniform(0.1, 0.4))


def download_image(request, url: str, name: str) -> str | None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    if "rsrc.php" in url or "emoji.php" in url:
        return None
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


def download_video(request, url: str, name: str) -> str | None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{name}.mp4"
    dest = IMAGES_DIR / filename
    if dest.exists() and dest.stat().st_size > 1000:
        return filename
    try:
        resp = request.get(url, headers={
            "Referer": "https://www.facebook.com/",
        })
        if resp.ok and len(resp.body()) > 1000:
            dest.write_bytes(resp.body())
            return filename
    except Exception:
        pass
    return None


def parse_frontmatter(filepath: Path) -> dict:
    content = filepath.read_text(encoding="utf-8")
    match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            val = val.strip().strip('"')
            if key.strip() == "tags" and val.startswith("[") and val.endswith("]"):
                val = val[1:-1]
            fm[key.strip()] = val
    return fm


# ---------------------------------------------------------------------------
# Render type detection
# ---------------------------------------------------------------------------

def detect_render_type(page, url: str) -> str:
    """Classify the page into a render type for extraction strategy selection."""
    # URL-based hints first
    if "/photo.php" in url or "/photo/" in url:
        return "photo_viewer"
    if "/media/set/" in url:
        return "album_page"
    if "/videos/" in url:
        return "video_page"

    return page.evaluate(r"""() => {
        const dialog = document.querySelector('[role=dialog]');
        const story = document.querySelector('[data-ad-rendering-role="story_message"]');
        const article = document.querySelector('[role=article]');
        const video = document.querySelector('video[src]:not([src^="blob:"])');

        // Video element present
        if (video) return 'video_page';

        // Dialog with post content
        if (dialog) {
            const innerArticle = dialog.querySelector('[role=article]');
            const dialogText = (dialog.innerText || '').trim();
            if (innerArticle || dialogText.length > 20) return 'dialog_post';
        }

        // Page-level story or article = full page render
        if (story || article) return 'full_page';

        return 'unknown';
    }""")


# ---------------------------------------------------------------------------
# Extraction strategies — one per render type
# ---------------------------------------------------------------------------

def _add_img(seen_srcs: set, images: list, img) -> None:
    """Shared image collector (used inside page.evaluate)."""
    # This is called from JS, so it's actually inlined in each strategy.
    pass  # placeholder — actual logic is in JS strings


def extract_dialog_post(page) -> dict:
    """Strategy for posts rendered inside [role=dialog]."""
    return page.evaluate(r"""() => {
        const seenSrcs = new Set();
        const images = [];
        function addImg(img) {
            const src = img.src || img.currentSrc || '';
            if (!src || seenSrcs.has(src)) return;
            if (!(src.includes('scontent') || src.includes('fbcdn'))) return;
            if (src.includes('rsrc.php') || src.includes('emoji.php')) return;
            const w = img.naturalWidth || img.width || 0;
            const h = img.naturalHeight || img.height || 0;
            if (w > 0 && w < 200 && h > 0 && h < 200) return;
            seenSrcs.add(src);
            images.push({ src, alt: img.alt || '', width: w, height: h });
        }

        const videos = [];
        const seenVids = new Set();
        const links = [];
        const seenLinks = new Set();

        // Strategy A: page-level story_message (avoids dialog chrome)
        let text = '';
        const story = document.querySelector('[data-ad-rendering-role="story_message"]');
        if (story) {
            text = story.innerText || '';
            story.querySelectorAll('img').forEach(addImg);
            story.querySelectorAll('a[href]').forEach(a => {
                const href = a.href;
                if (href && href.startsWith('http') && !href.includes('facebook.com') && !seenLinks.has(href)) {
                    seenLinks.add(href);
                    links.push({ href, text: (a.innerText || '').trim() });
                }
            });
        }

        // Strategy B: page-level article
        if (!text.trim()) {
            const article = document.querySelector('[role=article]');
            if (article) {
                text = article.innerText || '';
                article.querySelectorAll('img').forEach(addImg);
            }
        }

        // Strategy C: iterate all dialogs, skip Notifications/Menu
        if (!text.trim()) {
            const dialogs = document.querySelectorAll('[role=dialog]');
            for (const d of dialogs) {
                const t = (d.innerText || '').trim();
                if (t.startsWith('Notifications') || t.startsWith('Menu')) continue;
                if (t.length > 20) {
                    text = t;
                    d.querySelectorAll('img').forEach(addImg);
                    break;
                }
            }
        }

        // Collect videos from dialog
        document.querySelectorAll('video[src]:not([src^="blob:"])').forEach(v => {
            if (seenVids.has(v.src)) return;
            seenVids.add(v.src);
            videos.push({ src: v.src, poster: v.poster || '' });
        });

        images.sort((a, b) => (b.width * b.height) - (a.width * a.height));

        return { text, images, videos, links };
    }""")


def extract_full_page(page) -> dict:
    """Strategy for posts rendered directly on the page (story_message or article)."""
    return page.evaluate(r"""() => {
        const seenSrcs = new Set();
        const images = [];
        function addImg(img) {
            const src = img.src || img.currentSrc || '';
            if (!src || seenSrcs.has(src)) return;
            if (!(src.includes('scontent') || src.includes('fbcdn'))) return;
            if (src.includes('rsrc.php') || src.includes('emoji.php')) return;
            const w = img.naturalWidth || img.width || 0;
            const h = img.naturalHeight || img.height || 0;
            if (w > 0 && w < 200 && h > 0 && h < 200) return;
            seenSrcs.add(src);
            images.push({ src, alt: img.alt || '', width: w, height: h });
        }

        const videos = [];
        const seenVids = new Set();
        const links = [];
        const seenLinks = new Set();

        // story_message is the most reliable
        let text = '';
        const story = document.querySelector('[data-ad-rendering-role="story_message"]');
        if (story) {
            text = story.innerText || '';
            story.querySelectorAll('img').forEach(addImg);
            story.querySelectorAll('a[href]').forEach(a => {
                const href = a.href;
                if (href && href.startsWith('http') && !href.includes('facebook.com') && !seenLinks.has(href)) {
                    seenLinks.add(href);
                    links.push({ href, text: (a.innerText || '').trim() });
                }
            });
        }

        // Fallback to article
        if (!text.trim()) {
            const article = document.querySelector('[role=article]');
            if (article) {
                text = article.innerText || '';
                article.querySelectorAll('img').forEach(addImg);
            }
        }

        document.querySelectorAll('video[src]:not([src^="blob:"])').forEach(v => {
            if (seenVids.has(v.src)) return;
            seenVids.add(v.src);
            videos.push({ src: v.src, poster: v.poster || '' });
        });

        images.sort((a, b) => (b.width * b.height) - (a.width * a.height));

        return { text, images, videos, links };
    }""")


def extract_photo_viewer(page) -> dict:
    """Strategy for photo viewer pages — find the largest image."""
    return page.evaluate(r"""() => {
        const seenSrcs = new Set();
        const images = [];
        function addImg(img) {
            const src = img.src || img.currentSrc || '';
            if (!src || seenSrcs.has(src)) return;
            if (!(src.includes('scontent') || src.includes('fbcdn'))) return;
            if (src.includes('rsrc.php') || src.includes('emoji.php')) return;
            const w = img.naturalWidth || img.width || 0;
            const h = img.naturalHeight || img.height || 0;
            if (w > 0 && w < 200 && h > 0 && h < 200) return;
            seenSrcs.add(src);
            images.push({ src, alt: img.alt || '', width: w, height: h });
        }

        // Check dialog first (photo viewer often opens in dialog)
        const dialog = document.querySelector('[role=dialog]');
        if (dialog) {
            dialog.querySelectorAll('img').forEach(addImg);
            images.sort((a, b) => (b.width * b.height) - (a.width * a.height));
            const mainImg = images.length > 0 ? [images[0]] : [];
            const text = dialog.innerText || '';
            return { text: text.trim(), images: mainImg, videos: [], links: [] };
        }

        // Standalone page with large image
        const article = document.querySelector('[role=article]');
        if (article) {
            article.querySelectorAll('img').forEach(addImg);
            images.sort((a, b) => (b.width * b.height) - (a.width * a.height));
            const mainImg = images.length > 0 ? [images[0]] : [];
            const storyMsg = article.querySelector('[data-ad-rendering-role="story_message"]');
            const text = storyMsg ? storyMsg.innerText || '' : '';
            return { text: text.trim(), images: mainImg, videos: [], links: [] };
        }

        // Fallback: find biggest image on page
        document.querySelectorAll('img').forEach(addImg);
        images.sort((a, b) => (b.width * b.height) - (a.width * a.height));
        const mainImg = images.length > 0 ? [images[0]] : [];
        return { text: '', images: mainImg, videos: [], links: [] };
    }""")


def extract_video_page(page) -> dict:
    """Strategy for video pages — find the MP4 URL and post text."""
    return page.evaluate(r"""() => {
        const videos = [];
        const seenVids = new Set();
        document.querySelectorAll('video[src]:not([src^="blob:"])').forEach(v => {
            if (seenVids.has(v.src)) return;
            seenVids.add(v.src);
            videos.push({ src: v.src, poster: v.poster || '' });
        });

        let text = '';
        const story = document.querySelector('[data-ad-rendering-role="story_message"]');
        if (story) {
            text = story.innerText || '';
        } else {
            const article = document.querySelector('[role=article]');
            if (article) text = article.innerText || '';
        }
        text = text.replace(/\nAll reactions:[\s\S]*$/, '');
        text = text.replace(/\nLike\nComment\nShare.*$/, '');
        text = text.replace(/\nComments\n.*$/, '');
        text = text.trim();

        return { text, images: [], videos, links: [] };
    }""")


def extract_album_page(page) -> dict:
    """Strategy for album pages — scroll to load grid, download all large images."""
    # Scroll to trigger lazy loading
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1.5)
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(0.5)

    return page.evaluate(r"""() => {
        const seenSrcs = new Set();
        const images = [];
        document.querySelectorAll('img').forEach(img => {
            const src = img.src || img.currentSrc || '';
            if (!src || seenSrcs.has(src)) return;
            if (!(src.includes('scontent') || src.includes('fbcdn'))) return;
            if (src.includes('rsrc.php') || src.includes('emoji.php')) return;
            const w = img.naturalWidth || img.width || 0;
            const h = img.naturalHeight || img.height || 0;
            if (w > 0 && w < 200 && h > 0 && h < 200) return;
            seenSrcs.add(src);
            images.push({ src, alt: img.alt || '', width: w, height: h });
        });
        images.sort((a, b) => (b.width * b.height) - (a.width * a.height));

        // Get album title
        let text = '';
        const heading = document.querySelector('h2, h3, [data-testid="album-title"]');
        if (heading) text = heading.innerText || '';
        if (!text) {
            const bodyText = document.body?.innerText || '';
            const match = bodyText.match(/(?:Album|album)\s+.+?(?:\n|$)/);
            text = match ? match[0].trim() : 'Album';
        }

        return { text, images, videos: [], links: [] };
    }""")


def extract_unknown(page) -> dict:
    """Fallback: try everything, return whatever gives the most content."""
    # Try full_page first (most common)
    result = extract_full_page(page)
    if result["text"].strip() and len(result["text"]) > 20:
        return result

    # Try dialog
    result2 = extract_dialog_post(page)
    if len(result2["text"]) > len(result["text"]):
        result = result2

    # Add any images we missed
    more = page.evaluate(r"""() => {
        const seenSrcs = new Set();
        const images = [];
        document.querySelectorAll('img').forEach(img => {
            const src = img.src || img.currentSrc || '';
            if (!src || seenSrcs.has(src)) return;
            if (!(src.includes('scontent') || src.includes('fbcdn'))) return;
            if (src.includes('rsrc.php') || src.includes('emoji.php')) return;
            const w = img.naturalWidth || img.width || 0;
            const h = img.naturalHeight || img.height || 0;
            if (w > 0 && w < 200 && h > 0 && h < 200) return;
            seenSrcs.add(src);
            images.push({ src, alt: img.alt || '', width: w, height: h });
        });
        images.sort((a, b) => (b.width * b.height) - (a.width * a.height));
        return images;
    }""")

    # Merge images (dedup by src)
    existing_srcs = {img["src"] for img in result["images"]}
    for img in more:
        if img["src"] not in existing_srcs:
            result["images"].append(img)
            existing_srcs.add(img["src"])

    return result


STRATEGIES = {
    "dialog_post": extract_dialog_post,
    "full_page": extract_full_page,
    "photo_viewer": extract_photo_viewer,
    "video_page": extract_video_page,
    "album_page": extract_album_page,
    "unknown": extract_unknown,
}


# ---------------------------------------------------------------------------
# Text cleaning and validation
# ---------------------------------------------------------------------------

# Noise patterns to strip from extracted text
ACTION_RE = re.compile(
    r"^(Christian Camacho|You|Crow Systems|Tijuana PC|Facebook)"
    r" (shared|updated|added|created)\b"
)
NOISE_LINES = frozenset({
    "Like", "Comment", "Share", "Write a comment...", "Facebook",
    "Comments", "See all", "Reply", "Comment as Christian Camacho",
})
NOISE_PREFIX_RE = re.compile(
    r"^(All reactions:|Like\n|Comment as |Be the first|No comments|"
    r"View more|Shared with)"
)
COMMENT_SECTION_RE = re.compile(r"^Comment as ")
BARE_NUMBER_RE = re.compile(r"^\d+$")
GARBAGE_PREFIXES = ("Notifications", "Menu", "Facebook", "AllUnread",
                    "See all", "Activity log", "Christian Camacho",
                    "You created", "Crow Systems", "Tijuana PC")
TITLE_GARBAGE_RE = re.compile(
    r"^(Christian Camacho|You|Crow Systems|Tijuana PC|Facebook)"
    r" (shared|updated|added|created)\b"
)


def clean_text(text: str) -> str:
    """Remove Facebook UI noise from extracted text."""
    if not text:
        return ""
    lines = text.split("\n")
    cleaned = []
    skip_rest = False
    for line in lines:
        ls = line.strip()
        if not ls:
            cleaned.append("")
            continue
        if skip_rest:
            continue
        if ACTION_RE.match(ls):
            continue
        if ls in NOISE_LINES:
            continue
        if NOISE_PREFIX_RE.match(ls):
            continue
        if BARE_NUMBER_RE.match(ls):
            continue
        if COMMENT_SECTION_RE.search(ls):
            skip_rest = True
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


def is_garbage_text(text: str) -> bool:
    """Reject text that's clearly UI chrome, not post content."""
    t = text.strip()
    if not t:
        return False  # empty is fine, not garbage
    if any(t.startswith(p) for p in GARBAGE_PREFIXES):
        return True
    # More than 5 occurrences of "Facebook" = sidebar noise
    if t.lower().count("facebook") > 5:
        return True
    return False


def derive_title(text: str, old_title: str) -> str:
    """Pick a good title: first non-garbage line of text, or old title if OK."""
    if not TITLE_GARBAGE_RE.match(old_title) and not any(
        old_title.strip().startswith(p) for p in GARBAGE_PREFIXES
    ):
        return old_title

    if text:
        for line in text.split("\n"):
            ls = line.strip()
            if ls and 5 < len(ls) < 120:
                if not re.match(
                    r"^(Christian|Facebook|Notifications|Menu|Friends|"
                    r"See|Shared|No|Comment|Like|Reply|All|View|Write)",
                    ls,
                ):
                    return ls
    return old_title


# ---------------------------------------------------------------------------
# Markdown builder
# ---------------------------------------------------------------------------

def build_markdown(frontmatter: dict, data: dict) -> str:
    title = frontmatter["title"]
    created = frontmatter["created"]
    origin_link = frontmatter.get("origin_link", "")
    slug = frontmatter.get("slug", "")
    tags = frontmatter.get("tags", "facebook-import")
    lang = frontmatter.get("lang", "es")
    lang_group = frontmatter.get("lang_group", slug)

    lines = []

    for vid in data.get("videos", []):
        if vid.get("local_file"):
            lines.append(
                f'<video controls src="assets/{vid["local_file"]}"'
                f' style="width:100%; max-height:600px; border-radius:4px;"></video>'
            )
        else:
            lines.append(
                f'<video controls src="{vid["src"]}"'
                f' style="width:100%; max-height:600px; border-radius:4px;"></video>'
            )
        lines.append("")

    for img in data.get("images", []):
        alt = img.get("alt", "") or "Facebook image"
        file_key = img.get("file") or img.get("local_file") or ""
        if file_key:
            lines.append(f"![{alt}](assets/{file_key})")
        elif img.get("src"):
            lines.append(f"![{alt}]({img['src']})")
        lines.append("")

    text = data.get("text", "")
    if text:
        lines.append(text)
        lines.append("")

    for link in data.get("links", []):
        href = link["href"]
        link_text = link.get("text") or href
        if any(d in href for d in ["youtube.com", "youtu.be"]):
            lines.append(
                f'<iframe loading="lazy" src="{href}" title="{link_text}"'
                f' style="width:100%; height:500px; border:0; border-radius:4px;"></iframe>'
            )
        elif link_text and href:
            lines.append(f"[{link_text}]({href})")
            lines.append("")

    body = "\n".join(lines).strip() + "\n"

    description = (
        text[:160].replace('"', '\\"').replace("\n", " ").strip()
        if text
        else title
    )

    fm = [
        "---",
        f'title: "{title}"',
        f"created: {created}",
        f"updated: {created}",
        f'origin_link: "{origin_link}"',
        f'description: "{description}"',
        f"slug: {slug}",
        f"tags: {tags}",
        f"lang: {lang}",
        f"lang_group: {lang_group}",
        "---",
    ]

    return "\n".join(fm) + "\n\n" + body


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--batch", type=int, default=0, help="Process only N posts (0 = all)")
    args = parser.parse_args()

    if not RESCRAPE_LIST.exists():
        print(f"Error: {RESCRAPE_LIST} not found")
        return 1

    filenames = json.loads(RESCRAPE_LIST.read_text(encoding="utf-8"))
    print(f"Found {len(filenames)} posts to re-scrape")

    stats = {"fixed": 0, "failed": 0, "skipped": 0, "types": {}}

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE),
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            no_viewport=True,
        )

        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        processed = 0

        for i, filename in enumerate(filenames):
            if args.batch > 0 and processed >= args.batch:
                break

            filepath = OUTPUT_DIR / filename
            if not filepath.exists():
                print(f"  [{i+1}] {filename}... SKIP (file not found)")
                stats["skipped"] += 1
                continue

            fm = parse_frontmatter(filepath)
            origin_link = fm.get("origin_link", "")
            if not origin_link:
                print(f"  [{i+1}] {filename}... SKIP (no origin_link)")
                stats["skipped"] += 1
                continue

            created = fm.get("created", datetime.now().strftime("%Y-%m-%d"))
            slug = fm.get("slug", filename.replace(".md", ""))
            title = fm.get("title", "")
            tags = fm.get("tags", "facebook-import")
            lang = fm.get("lang", "es")
            lang_group = fm.get("lang_group", slug)

            print(f"  [{i+1}] {filename}")
            print(f"    URL: {origin_link[:80]}...")

            try:
                page.goto(origin_link, wait_until="domcontentloaded")
                human_delay(2, 4)
                human_move(page)

                render_type = detect_render_type(page, origin_link)
                print(f"    Render type: {render_type}")
                stats["types"][render_type] = stats["types"].get(render_type, 0) + 1

                strategy = STRATEGIES.get(render_type, extract_unknown)
                data = strategy(page)

                # Clean text
                data["text"] = clean_text(data.get("text", ""))

                # Validate
                text = data.get("text", "")
                if is_garbage_text(text):
                    print(f"    Rejected garbage text ({len(text)} chars)")
                    data["text"] = ""

                # Check if extraction produced anything useful
                has_media = data.get("images") or data.get("videos")
                text_ok = len(data.get("text", "")) >= 10
                if not has_media and not text_ok:
                    print(f"    FAILED: no images, no videos, text too short")
                    stats["failed"] += 1
                    human_delay(2, 4)
                    continue

                # Derive title from first meaningful text line
                title = derive_title(data.get("text", ""), title)

                # Download images
                local_images = []
                for j, img in enumerate(data.get("images", [])):
                    img_name = f"{slug}_{j}"
                    local = download_image(page.request, img["src"], img_name)
                    if local:
                        local_images.append({"file": local, "alt": img.get("alt", "")})
                data["images"] = local_images

                # Download videos
                local_videos = []
                for j, vid in enumerate(data.get("videos", [])):
                    vid_name = f"{slug}_v{j}"
                    local = download_video(page.request, vid["src"], vid_name)
                    local_videos.append({"src": vid["src"], "local_file": local})
                data["videos"] = local_videos

                frontmatter = {
                    "title": title,
                    "created": created,
                    "origin_link": origin_link,
                    "slug": slug,
                    "tags": tags,
                    "lang": lang,
                    "lang_group": lang_group,
                }

                md = build_markdown(frontmatter, data)
                filepath.write_text(md, encoding="utf-8")
                print(f"    Saved ({render_type}, {len(local_images)} imgs, {len(local_videos)} vids)")
                stats["fixed"] += 1
                processed += 1

            except Exception as e:
                print(f"    ERROR: {e}")
                stats["failed"] += 1

            human_delay(2, 4)
            if random.random() < 0.1:
                human_delay(4, 7)

        ctx.close()

    # Summary
    print(f"\n--- Summary ---")
    print(f"Fixed:   {stats['fixed']}")
    print(f"Failed:  {stats['failed']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Render types: {dict(stats['types'])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
