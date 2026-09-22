#!/usr/bin/env python3
"""Re-extract 73 bad Facebook posts from content/_drafts/fb/_bad_posts.txt.

Each bad post has a Facebook URL in origin_link. This script visits each URL,
detects the post type, extracts content with the appropriate extractor, and
rewrites the markdown file.

Usage:
    python scripts/fb_reextract.py          # process all 73
    python scripts/fb_reextract.py --batch 5 # process 5 at a time
"""

from __future__ import annotations

import argparse
import random
import re
import time
from datetime import datetime
from pathlib import Path

import dateparser
from playwright.sync_api import sync_playwright

BAD_POSTS_FILE = Path("content/_drafts/fb/_bad_posts.txt")
OUTPUT_DIR = Path("content/_drafts/fb")
IMAGES_DIR = Path("content/_drafts/fb/assets")
ASSETS_DIR = IMAGES_DIR
CHROME_PROFILE = Path("facebook_chrome_profile")


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


def detect_post_type(page, url: str = "") -> str:
    # URL-based detection is more reliable than DOM for many types
    if "/videos/" in url:
        return "video"
    if "/photo.php" in url or "/photo/" in url:
        return "photo"
    if "/media/set/" in url:
        return "album"

    return page.evaluate("""() => {
        const dialog = document.querySelector('[role=dialog]');
        const story = document.querySelector('[data-ad-rendering-role="story_message"]');
        const article = document.querySelector('[role=article]');

        // Check for video element first (even inside dialog)
        const video = document.querySelector('video[src]:not([src^="blob:"])');
        if (video) {
            const vh = video.videoHeight || 0;
            const vw = video.videoWidth || 0;
            if (vh > vw) return 'reel';
            return 'video';
        }

        // Dialog posts — find the actual post content
        if (dialog) {
            const innerArticle = dialog.querySelector('[role=article]');
            if (innerArticle) return 'shared_post';
            return 'shared_post';
        }

        // story_message with text = status
        if (story && story.innerText.trim().length > 0) {
            return 'status';
        }

        // Article = feed post
        if (article) return 'shared_post';

        return 'unknown';
    }""")


def extract_status(page) -> dict:
    return page.evaluate("""() => {
        const story = document.querySelector('[data-ad-rendering-role="story_message"]');
        let text = '';
        if (story) {
            text = story.innerText || '';
        } else {
            const article = document.querySelector('[role=article]');
            if (article) text = article.innerText || '';
            else {
                const body = document.body;
                if (body) text = body.innerText || '';
            }
        }
        text = text.replace(/\\nAll reactions:[\\s\\S]*$/, '');
        text = text.replace(/\\nLike\\nComment\\nShare.*$/, '');
        text = text.replace(/\\nComments\\n.*$/, '');
        text = text.trim();
        return { text, images: [], videos: [], links: [] };
    }""")


def extract_shared_post(page) -> dict:
    return page.evaluate("""() => {
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
        document.querySelectorAll('video[src]:not([src^="blob:"])').forEach(v => {
            if (seenVids.has(v.src)) return;
            seenVids.add(v.src);
            videos.push({ src: v.src, poster: v.poster || '' });
        });

        const links = [];
        const seenLinks = new Set();

        // Strategy 1: page-level story_message (most reliable)
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

        // Strategy 2: page-level article
        if (!text.trim()) {
            const article = document.querySelector('[role=article]');
            if (article) {
                text = article.innerText || '';
                article.querySelectorAll('img').forEach(addImg);
            }
        }

        // Strategy 3: find the RIGHT dialog (skip notifications)
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

        images.sort((a, b) => (b.width * b.height) - (a.width * a.height));

        return { text, images, videos, links };
    }""")


def extract_shared_link(page) -> dict:
    return page.evaluate("""() => {
        const seenSrcs = new Set();
        const images = [];
        function addImg(img) {
            const src = img.src || img.currentSrc || '';
            if (!src || seenSrcs.has(src)) return;
            if (!(src.includes('scontent') || src.includes('fbcdn'))) return;
            if (src.includes('rsrc.php') || src.includes('emoji.php')) return;
            seenSrcs.add(src);
            images.push({ src, alt: img.alt || '' });
        }

        const links = [];
        const seenLinks = new Set();

        // Find link preview card
        const linkShim = document.querySelector('[data-testid="linkshim_attachment"]');
        let card = null;
        if (linkShim) {
            card = linkShim;
        } else {
            const fbLink = document.querySelector('a[href*="l.facebook.com/l.php"]');
            if (fbLink) card = fbLink.closest('[role=article]') || fbLink.parentElement;
        }

        let cardText = '';
        if (card) {
            // Extract title and description from the card
            const titleEl = card.querySelector('[data-testid="post_message"] strong, h3, [class*="title"]');
            const descEl = card.querySelector('[class*="description"], [class*="subtitle"]');
            if (titleEl) cardText += titleEl.innerText.trim() + '\\n';
            if (descEl) cardText += descEl.innerText.trim() + '\\n';
            card.querySelectorAll('img').forEach(addImg);
        }

        // Get any user text above the card
        const article = document.querySelector('[role=article]');
        let userText = '';
        if (article) {
            const story = article.querySelector('[data-ad-rendering-role="story_message"]');
            if (story) userText = story.innerText.trim();
        }

        const text = (userText + '\\n' + cardText).trim();

        if (card) {
            card.querySelectorAll('a[href]').forEach(a => {
                const href = a.href;
                if (href && href.startsWith('http') && !href.includes('facebook.com') && !seenLinks.has(href)) {
                    seenLinks.add(href);
                    links.push({ href, text: (a.innerText || '').trim() });
                }
            });
        }

        return { text, images, videos: [], links };
    }""")


def extract_photo(page) -> dict:
    return page.evaluate("""() => {
        const seenSrcs = new Set();
        const images = [];
        function addImg(img) {
            const src = img.src || img.currentSrc || '';
            if (!src || seenSrcs.has(src)) return;
            if (!(src.includes('scontent') || src.includes('fbcdn'))) return;
            if (src.includes('rsrc.php') || src.includes('emoji.php')) return;
            const w = img.naturalWidth || img.width || 0;
            const h = img.naturalHeight || img.height || 0;
            if (w > 0 && h > 0 && w < 200 && h < 200) return;
            seenSrcs.add(src);
            images.push({ src, alt: img.alt || '', width: w, height: h });
        }

        // Check dialog first
        const dialog = document.querySelector('[role=dialog]');
        if (dialog) {
            dialog.querySelectorAll('img').forEach(addImg);
            // Sort by size, keep biggest
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
            const text = article.querySelector('[data-ad-rendering-role="story_message"]')?.innerText || '';
            return { text: text.trim(), images: mainImg, videos: [], links: [] };
        }

        // Fallback: find biggest image on page
        document.querySelectorAll('img').forEach(addImg);
        images.sort((a, b) => (b.width * b.height) - (a.width * a.height));
        const mainImg = images.length > 0 ? [images[0]] : [];
        return { text: '', images: mainImg, videos: [], links: [] };
    }""")


def extract_video(page) -> dict:
    return page.evaluate("""() => {
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
        text = text.replace(/\\nAll reactions:[\\s\\S]*$/, '');
        text = text.replace(/\\nLike\\nComment\\nShare.*$/, '');
        text = text.replace(/\\nComments\\n.*$/, '');
        text = text.trim();

        return { text, images: [], videos, links: [] };
    }""")


def extract_reel(page) -> dict:
    return page.evaluate("""() => {
        const videos = [];
        const seenVids = new Set();
        document.querySelectorAll('video[src]:not([src^="blob:"])').forEach(v => {
            if (seenVids.has(v.src)) return;
            seenVids.add(v.src);
            videos.push({ src: v.src, poster: v.poster || '' });
        });

        let text = '';
        const story = document.querySelector('[data-ad-rendering-role="story_message"]');
        if (story) text = story.innerText || '';
        else {
            const article = document.querySelector('[role=article]');
            if (article) text = article.innerText || '';
        }
        text = text.replace(/\\nAll reactions:[\\s\\S]*$/, '');
        text = text.replace(/\\nLike\\nComment\\nShare.*$/, '');
        text = text.trim();

        return { text, images: [], videos, links: [] };
    }""")


def extract_life_event(page) -> dict:
    return page.evaluate("""() => {
        const article = document.querySelector('[role=article]');
        if (!article) return { text: '', images: [], videos: [], links: [] };

        const seenSrcs = new Set();
        const images = [];
        article.querySelectorAll('img').forEach(img => {
            const src = img.src || img.currentSrc || '';
            if (!src || seenSrcs.has(src)) return;
            if (!(src.includes('scontent') || src.includes('fbcdn'))) return;
            if (src.includes('rsrc.php') || src.includes('emoji.php')) return;
            seenSrcs.add(src);
            images.push({ src, alt: img.alt || '' });
        });

        let text = article.innerText || '';
        text = text.replace(/\\nAll reactions:[\\s\\S]*$/, '');
        text = text.replace(/\\nLike\\nComment\\nShare.*$/, '');
        text = text.trim();

        return { text, images, videos: [], links: [] };
    }""")


def extract_album_creation(page) -> dict:
    return page.evaluate("""() => {
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

        let text = document.body?.innerText || '';
        const match = text.match(/You created the album:.+?(?=\\n|$)/);
        text = match ? match[0] : 'Album created';

        return { text, images, videos: [], links: [] };
    }""")


def extract_unknown(page) -> dict:
    return page.evaluate("""() => {
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

        let text = document.body?.innerText || '';
        text = text.replace(/\\nAll reactions:[\\s\\S]*$/, '');
        text = text.replace(/\\nLike\\nComment\\nShare.*$/, '');
        text = text.replace(/\\nComments\\n.*$/, '');
        text = text.trim();

        const links = [];
        document.querySelectorAll('a[href]').forEach(a => {
            const href = a.href;
            if (href && href.startsWith('http') && !href.includes('facebook.com')) {
                links.push({ href, text: (a.innerText || '').trim() });
            }
        });

        return { text, images, videos: [], links };
    }""")


EXTRACTORS = {
    "status": extract_status,
    "shared_post": extract_shared_post,
    "shared_link": extract_shared_link,
    "photo": extract_photo,
    "video": extract_video,
    "reel": extract_reel,
    "life_event": extract_life_event,
    "album": extract_album_creation,
    "unknown": extract_unknown,
}


def read_bad_posts() -> list[tuple[str, str]]:
    lines = BAD_POSTS_FILE.read_text(encoding="utf-8").strip().split("\n")
    result = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t", 1)
        filename = parts[0].strip()
        problem = parts[1].strip() if len(parts) > 1 else ""
        result.append((filename, problem))
    return result


def download_video(request, url: str, name: str) -> str | None:
    """Download video from Facebook CDN."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{name}.mp4"
    dest = ASSETS_DIR / filename
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


def build_markdown(frontmatter: dict, data: dict, post_type: str) -> str:
    title = frontmatter["title"]
    created = frontmatter["created"]
    origin_link = frontmatter.get("origin_link", "")
    slug = frontmatter.get("slug", "")
    tags = frontmatter.get("tags", "facebook-import")
    lang = frontmatter.get("lang", "es")
    lang_group = frontmatter.get("lang_group", slug)

    lines = []

    # Videos first (downloaded locally)
    for vid in data.get("videos", []):
        if vid.get("local_file"):
            lines.append(f'<video controls src="assets/{vid["local_file"]}" style="width:100%; max-height:600px; border-radius:4px;"></video>')
        else:
            lines.append(f'<video controls src="{vid["src"]}" style="width:100%; max-height:600px; border-radius:4px;"></video>')
        lines.append("")

    # Images
    for img in data.get("images", []):
        alt = img.get("alt", "") or "Facebook image"
        file_key = img.get("file") or img.get("local_file") or ""
        if file_key:
            lines.append(f"![{alt}](assets/{file_key})")
        elif img.get("src"):
            lines.append(f"![{alt}]({img['src']})")
        lines.append("")

    # Text
    text = data.get("text", "")
    if text:
        lines.append(text)
        lines.append("")

    # Links
    for link in data.get("links", []):
        href = link["href"]
        link_text = link.get("text") or href
        if any(d in href for d in ["youtube.com", "youtu.be"]):
            lines.append(f'<iframe loading="lazy" src="{href}" title="{link_text}" style="width:100%; height:500px; border:0; border-radius:4px;"></iframe>')
        elif link_text and href:
            lines.append(f"[{link_text}]({href})")
            lines.append("")

    body = "\n".join(lines).strip() + "\n"

    description = text[:160].replace('"', '\\"').replace("\n", " ").strip() if text else title

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
            # Strip YAML list brackets: [a, b] -> a, b
            if key.strip() == "tags" and val.startswith("[") and val.endswith("]"):
                val = val[1:-1]
            fm[key.strip()] = val
    return fm


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--batch", type=int, default=0, help="Process only N posts (0 = all)")
    args = parser.parse_args()

    bad_posts = read_bad_posts()
    print(f"Found {len(bad_posts)} bad posts")

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE),
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            no_viewport=True,
        )

        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        processed = 0

        for i, (filename, problem) in enumerate(bad_posts):
            if args.batch > 0 and processed >= args.batch:
                break

            filepath = OUTPUT_DIR / filename
            if not filepath.exists():
                continue

            # Skip if already fixed — quick re-check
            content = filepath.read_text(encoding="utf-8")
            body = content.split("---", 2)[-1].strip() if "---" in content else ""
            has_video = "<video" in body.lower()
            has_image = "![" in body
            title_match = re.search(r'title:\s*"([^"]*)"', content)
            t = title_match.group(1) if title_match else ""
            is_action_title = re.match(r"^(Christian Camacho|You|Crow Systems|Tijuana PC|Facebook) (shared|updated|added|created)\b", t)

            if (has_video or has_image) and len(body) > 30:
                print(f"  [{i+1}] {filename[:50]}... SKIP (already good)")
                processed += 1
                continue

            fm = parse_frontmatter(filepath)
            origin_link = fm.get("origin_link", "")
            if not origin_link:
                print(f"  [{i+1}] {filename[:50]}... SKIP (no origin_link)")
                continue

            created = fm.get("created", datetime.now().strftime("%Y-%m-%d"))
            slug = fm.get("slug", filename.replace(".md", ""))
            title = fm.get("title", "")
            tags = fm.get("tags", "facebook-import")
            lang = fm.get("lang", "es")
            lang_group = fm.get("lang_group", slug)

            print(f"  [{i+1}] {filename}")
            print(f"    URL: {origin_link[:80]}...")
            print(f"    Problem: {problem}")

            try:
                page.goto(origin_link, wait_until="domcontentloaded")
                human_delay(2, 4)
                human_move(page)

                post_type = detect_post_type(page, origin_link)
                print(f"    Detected type: {post_type}")

                extractor = EXTRACTORS.get(post_type, extract_unknown)
                data = extractor(page)

                # Clean text aggressively
                text = data.get("text", "")
                if text:
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
                        # Action lines
                        if re.match(r"^(Christian Camacho|You|Crow Systems|Tijuana PC) (shared|updated|added)\b", ls):
                            continue
                        if re.match(r"^You created the album:", ls):
                            continue
                        # Facebook UI noise
                        if ls in ("Like", "Comment", "Share", "Write a comment...", "Facebook", "Comments", "See all", "Reply", "Comment as Christian Camacho"):
                            continue
                        if re.match(r"^(All reactions:|Like\n|Comment as |Be the first|No comments|View more|Shared with)", ls):
                            continue
                        if re.match(r"^\d+$", ls):  # bare numbers (reaction counts)
                            continue
                        # Stop at comment section
                        if "Comment as " in ls:
                            skip_rest = True
                            continue
                        cleaned.append(line)
                    text = "\n".join(cleaned).strip()
                    data["text"] = text

                # Validate extracted text — reject if it's page chrome
                text = data.get("text", "")
                garbage_prefixes = ("Notifications", "Menu", "Facebook", "AllUnread", "See all", "Activity log")
                if text and any(text.strip().startswith(p) for p in garbage_prefixes):
                    # Text is UI garbage — clear it, keep only media
                    data["text"] = ""

                # Update title if old one was an action pattern OR garbage
                text = data.get("text", "")
                garbage_prefixes = ("Notifications", "Menu", "Facebook", "AllUnread", "See all", "Activity log", "Christian Camacho", "You created", "Crow Systems", "Tijuana PC")
                title_is_bad = re.match(r"^(Christian Camacho|You|Crow Systems|Tijuana PC|Facebook) (shared|updated|added|created)\b", title) or any(title.strip().startswith(p) for p in garbage_prefixes)
                if text and title_is_bad:
                    for line in text.split("\n"):
                        ls = line.strip()
                        if ls and 5 < len(ls) < 120:
                            if not re.match(r"^(Christian|Facebook|Notifications|Menu|Friends|See|Shared|No|Comment|Like|Reply|All|View|Write)", ls):
                                title = ls
                                break

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

                md = build_markdown(frontmatter, data, post_type)
                filepath.write_text(md, encoding="utf-8")
                print(f"    Saved: {filename}")
                processed += 1

            except Exception as e:
                print(f"    ERROR: {e}")

            human_delay(2, 4)
            if random.random() < 0.1:
                human_delay(4, 7)

        ctx.close()

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
