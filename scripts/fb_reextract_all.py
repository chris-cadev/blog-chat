#!/usr/bin/env python3
"""Re-extract all existing Facebook draft posts using Playwright.

Visits each post's origin_link, extracts clean content, generates unique slugs,
and rewrites the markdown files.

Usage:
    python scripts/fb_reextract_all.py              # process all
    python scripts/fb_reextract_all.py --batch 10   # process 10 at a time
    python scripts/fb_reextract_all.py --dry-run     # show what would change
    python scripts/fb_reextract_all.py --skip-scrape # just fix slugs, no Playwright
"""

from __future__ import annotations

import argparse
import hashlib
import random
import re
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("content/_drafts/fb")
IMAGES_DIR = OUTPUT_DIR / "assets"
ASSETS_DIR = IMAGES_DIR
CHROME_PROFILE = Path("facebook_chrome_profile")

# ── Slugs ──────────────────────────────────────────────────────────────────


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


def make_unique_slug(base_slug: str, created: str, all_slugs: set) -> str:
    """Ensure slug is unique by appending date suffix if needed."""
    candidate = base_slug
    if candidate not in all_slugs:
        all_slugs.add(candidate)
        return candidate
    # Append date (YYYY-MM-DD) to make unique
    date_suffix = created.replace("-", "")[:8] if created else ""
    if date_suffix:
        candidate = f"{base_slug}-{date_suffix}"
    if candidate not in all_slugs:
        all_slugs.add(candidate)
        return candidate
    # Append short hash
    h = hashlib.md5(f"{base_slug}{created}".encode()).hexdigest()[:6]
    candidate = f"{base_slug}-{h}"
    all_slugs.add(candidate)
    return candidate


# ── Delays ─────────────────────────────────────────────────────────────────


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


# ── Downloads ──────────────────────────────────────────────────────────────


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


# ── Post type detection ────────────────────────────────────────────────────


def detect_post_type(page, url: str = "") -> str:
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

        const video = document.querySelector('video[src]:not([src^="blob:"])');
        if (video) {
            const vh = video.videoHeight || 0;
            const vw = video.videoWidth || 0;
            if (vh > vw) return 'reel';
            return 'video';
        }

        if (story) {
            const storyText = story.innerText.trim();
            const currentPath = window.location.pathname;
            let internalFbLinkCount = 0;
            for (const a of document.querySelectorAll('a[href]')) {
                try {
                    const path = new URL(a.href).pathname;
                    if (path !== currentPath && (path.includes('/photo') || path.includes('/posts/'))) {
                        internalFbLinkCount++;
                    }
                } catch(e) {}
            }
            if (storyText.length > 0 && internalFbLinkCount > 0) {
                return 'memory';
            }
        }

        if (dialog) {
            const innerArticle = dialog.querySelector('[role=article]');
            if (innerArticle) return 'shared_post';
            return 'shared_post';
        }

        if (story && story.innerText.trim().length > 0) {
            return 'status';
        }

        if (article) return 'shared_post';

        return 'unknown';
    }""")


# ── Extractors ─────────────────────────────────────────────────────────────


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

        if (!text.trim()) {
            const article = document.querySelector('[role=article]');
            if (article) {
                text = article.innerText || '';
                article.querySelectorAll('img').forEach(addImg);
            }
        }

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

        const dialog = document.querySelector('[role=dialog]');
        if (dialog) {
            dialog.querySelectorAll('img').forEach(addImg);
            images.sort((a, b) => (b.width * b.height) - (a.width * a.height));
            const mainImg = images.length > 0 ? [images[0]] : [];
            const text = dialog.innerText || '';
            return { text: text.trim(), images: mainImg, videos: [], links: [] };
        }

        const article = document.querySelector('[role=article]');
        if (article) {
            article.querySelectorAll('img').forEach(addImg);
            images.sort((a, b) => (b.width * b.height) - (a.width * a.height));
            const mainImg = images.length > 0 ? [images[0]] : [];
            const text = article.querySelector('[data-ad-rendering-role="story_message"]')?.innerText || '';
            return { text: text.trim(), images: mainImg, videos: [], links: [] };
        }

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


def extract_memory(page) -> dict:
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

        let text = '';
        const story = document.querySelector('[data-ad-rendering-role="story_message"]');
        if (story) {
            text = story.innerText || '';
            story.querySelectorAll('img').forEach(addImg);
        }
        if (!text.trim()) {
            const article = document.querySelector('[role=article]');
            if (article) text = article.innerText || '';
        }

        const fbLinks = [];
        const seenPaths = new Set();
        const currentPath = window.location.pathname;
        document.querySelectorAll('a[href]').forEach(a => {
            try {
                const u = new URL(a.href);
                const path = u.pathname;
                if (path === currentPath) return;
                if (seenPaths.has(path)) return;
                if (path.includes('/photo') || path.includes('/posts/')) {
                    seenPaths.add(path);
                    fbLinks.push({ href: u.href, text: (a.innerText || '').trim() });
                }
            } catch(e) {}
        });
        fbLinks.sort((a, b) => {
            const aPhoto = a.href.includes('/photo') ? 0 : 1;
            const bPhoto = b.href.includes('/photo') ? 0 : 1;
            return aPhoto - bPhoto;
        });

        images.sort((a, b) => (b.width * b.height) - (a.width * a.height));
        return { text: text.trim(), images, videos: [], links: fbLinks };
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
            if (w > 0 && h > 0 && w < 200 && h < 200) return;
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
    "photo": extract_photo,
    "video": extract_video,
    "reel": extract_reel,
    "memory": extract_memory,
    "unknown": extract_unknown,
}


# ── Text cleaning ──────────────────────────────────────────────────────────


def clean_text(text: str, title: str = "") -> tuple[str, str]:
    """Clean extracted text and derive a better title if needed."""
    if not text:
        return "", title

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
        if re.match(r"^(Christian Camacho|You|Crow Systems|Tijuana PC) (shared|updated|added)\b", ls):
            continue
        if re.match(r"^You created the album:", ls):
            continue
        if ls in ("Like", "Comment", "Share", "Write a comment...", "Facebook",
                   "Comments", "See all", "Reply", "Comment as Christian Camacho"):
            continue
        if re.match(r"^(All reactions:|Like\n|Comment as |Be the first|No comments|View more|Shared with)", ls):
            continue
        if re.match(r"^\d+$", ls):
            continue
        if "Comment as " in ls:
            skip_rest = True
            continue
        cleaned.append(line)

    text = "\n".join(cleaned).strip()

    # Reject garbage text
    garbage_prefixes = ("Notifications", "Menu", "Facebook", "AllUnread", "See all", "Activity log")
    if any(text.strip().startswith(p) for p in garbage_prefixes):
        text = ""

    # Derive title from first meaningful line if current title is bad
    title_is_bad = re.match(
        r"^(Christian Camacho|You|Crow Systems|Tijuana PC|Facebook) (shared|updated|added|created)\b", title
    ) or any(title.strip().startswith(p) for p in garbage_prefixes)

    if text and title_is_bad:
        for line in text.split("\n"):
            ls = line.strip()
            if ls and 5 < len(ls) < 120:
                if not re.match(r"^(Christian|Facebook|Notifications|Menu|Friends|See|Shared|No|Comment|Like|Reply|All|View|Write)", ls):
                    title = ls
                    break

    return text, title


# ── Markdown builder ───────────────────────────────────────────────────────


def build_markdown(frontmatter: dict, data: dict, post_type: str) -> str:
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
            lines.append(f'<video controls src="assets/{vid["local_file"]}" style="width:100%; max-height:600px; border-radius:4px;"></video>')
        else:
            lines.append(f'<video controls src="{vid["src"]}" style="width:100%; max-height:600px; border-radius:4px;"></video>')
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
            vid_id = None
            m = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})", href)
            if m:
                vid_id = m.group(1)
            if vid_id:
                lines.append(f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{vid_id}" title="{link_text}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>')
            else:
                lines.append(f'<iframe loading="lazy" src="{href}" title="{link_text}" style="width:100%; height:500px; border:0; border-radius:4px;"></iframe>')
        elif "soundcloud.com" in href:
            sc_path = re.sub(r"https?://soundcloud\.com/", "", href).rstrip("/")
            embed_url = f"https://w.soundcloud.com/player/?url=https%3A//soundcloud.com/{sc_path.replace('/', '%2F')}&color=%23ff5500&auto_play=false&hide_related=true&show_comments=false&show_user=true&show_reposts=false&show_teaser=false&visual=true"
            lines.append(f'<iframe width="100%" height="300" src="{embed_url}" title="SoundCloud player" frameborder="0" allow="autoplay; encrypted-media" scrolling="no" loading="lazy"></iframe>')
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


# ── Main ───────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--batch", type=int, default=0, help="Process only N posts (0 = all)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")
    parser.add_argument("--skip-scrape", action="store_true", help="Only fix slugs, skip Playwright")
    args = parser.parse_args()

    # Collect all existing posts
    all_files = sorted(OUTPUT_DIR.glob("*.md"))
    all_files = [f for f in all_files if not f.name.startswith("_")]
    print(f"Found {len(all_files)} existing posts")

    # First pass: collect all slugs to detect conflicts
    slug_counts: dict[str, list[str]] = {}
    file_data: list[tuple[Path, dict]] = []
    for filepath in all_files:
        fm = parse_frontmatter(filepath)
        slug = fm.get("slug", filepath.stem)
        slug_counts.setdefault(slug, []).append(filepath.name)
        file_data.append((filepath, fm))

    dupes = {s: files for s, files in slug_counts.items() if len(files) > 1}
    if dupes:
        print(f"\n⚠ Found {len(dupes)} duplicate slugs:")
        for s, files in dupes.items():
            print(f"  {s}: {len(files)} files")

    if args.skip_scrape:
        # Just fix slugs
        used_slugs: set[str] = set()
        fixed = 0
        for filepath, fm in file_data:
            slug = fm.get("slug", filepath.stem)
            created = fm.get("created", "")
            unique_slug = make_unique_slug(slug, created, used_slugs)
            if unique_slug != slug:
                content = filepath.read_text("utf-8")
                content = content.replace(f"slug: {slug}", f"slug: {unique_slug}", 1)
                content = content.replace(f"lang_group: {slug}", f"lang_group: {unique_slug}", 1)
                if not args.dry_run:
                    filepath.write_text(content, "utf-8")
                fixed += 1
                print(f"  Fixed: {filepath.name} -> {unique_slug}")
        print(f"\nFixed {fixed} duplicate slugs")
        return 0

    # Re-scrape with Playwright
    processed = 0
    used_slugs: set[str] = set()

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE),
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            no_viewport=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        for filepath, fm in file_data:
            if args.batch > 0 and processed >= args.batch:
                break

            filename = filepath.name
            origin_link = fm.get("origin_link", "")
            created = fm.get("created", datetime.now().strftime("%Y-%m-%d"))
            old_slug = fm.get("slug", filepath.stem)
            title = fm.get("title", "")
            tags = fm.get("tags", "facebook-import")
            lang = fm.get("lang", "es")

            # Generate unique slug
            new_slug = make_unique_slug(old_slug, created, used_slugs)

            if not origin_link:
                print(f"  [{processed+1}] {filename[:60]}... SKIP (no origin_link)")
                # Still fix slug if needed
                if new_slug != old_slug:
                    content = filepath.read_text("utf-8")
                    content = content.replace(f"slug: {old_slug}", f"slug: {new_slug}", 1)
                    content = content.replace(f"lang_group: {old_slug}", f"lang_group: {new_slug}", 1)
                    if not args.dry_run:
                        filepath.write_text(content, "utf-8")
                    print(f"    Fixed slug: {old_slug} -> {new_slug}")
                processed += 1
                continue

            print(f"  [{processed+1}] {filename[:60]}")
            print(f"    URL: {origin_link[:80]}...")

            try:
                page.goto(origin_link, wait_until="domcontentloaded")
                human_delay(2, 4)
                human_move(page)

                post_type = detect_post_type(page, origin_link)
                print(f"    Type: {post_type}")

                extractor = EXTRACTORS.get(post_type, extract_unknown)
                data = extractor(page)

                # Memory posts: follow internal FB links
                if post_type == "memory" and data.get("links"):
                    caption = data.get("text", "")
                    for link in data["links"][:1]:
                        fb_url = link["href"]
                        if "/photo" in fb_url or "/posts/" in fb_url:
                            print(f"    Following memory link...")
                            try:
                                page.goto(fb_url, wait_until="domcontentloaded")
                                human_delay(2, 4)
                                orig_type = detect_post_type(page, fb_url)
                                orig_extractor = EXTRACTORS.get(orig_type, extract_unknown)
                                orig_data = orig_extractor(page)
                                if orig_data.get("images"):
                                    data["images"] = orig_data["images"]
                                if orig_data.get("videos"):
                                    data["videos"] = orig_data["videos"]
                                if orig_data.get("links"):
                                    data["links"] = orig_data["links"]
                                orig_text = orig_data.get("text", "")
                                if caption and orig_text:
                                    data["text"] = f"{caption}\n\n{orig_text}"
                                elif orig_text:
                                    data["text"] = orig_text
                                elif caption:
                                    data["text"] = caption
                            except Exception as e:
                                print(f"    Memory link error: {e}")

                # Clean text
                text, title = clean_text(data.get("text", ""), title)
                data["text"] = text

                # Download images
                local_images = []
                for j, img in enumerate(data.get("images", [])):
                    img_name = f"{new_slug}_{j}"
                    local = download_image(page.request, img["src"], img_name)
                    if local:
                        local_images.append({"file": local, "alt": img.get("alt", "")})
                data["images"] = local_images

                # Download videos
                local_videos = []
                for j, vid in enumerate(data.get("videos", [])):
                    vid_name = f"{new_slug}_v{j}"
                    local = download_video(page.request, vid["src"], vid_name)
                    local_videos.append({"src": vid["src"], "local_file": local})
                data["videos"] = local_videos

                frontmatter = {
                    "title": title,
                    "created": created,
                    "origin_link": origin_link,
                    "slug": new_slug,
                    "tags": tags,
                    "lang": lang,
                    "lang_group": new_slug,
                }

                md = build_markdown(frontmatter, data, post_type)
                if not args.dry_run:
                    filepath.write_text(md, encoding="utf-8")
                print(f"    Saved: {filename} (slug: {new_slug})")
                processed += 1

            except Exception as e:
                print(f"    ERROR: {e}")

            human_delay(2, 4)
            if random.random() < 0.1:
                human_delay(4, 7)

        ctx.close()

    print(f"\nDone. Processed {processed} posts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
