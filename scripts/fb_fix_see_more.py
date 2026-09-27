#!/usr/bin/env python3
"""Fix 42 posts with truncated '… See more' text by clicking to expand."""

from __future__ import annotations

import random
import re
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("content/_drafts/fb")
ASSETS_DIR = OUTPUT_DIR / "assets"
CHROME_PROFILE = Path("facebook_chrome_profile")


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


def click_see_more(page) -> bool:
    """Click all 'See more' buttons to expand truncated text. Returns True if any clicked."""
    clicked = False
    # Try multiple selectors for "See more"
    selectors = [
        'span:text-is("See more")',
        'span:text-is("Ver más")',
        'div[role="button"]:has-text("See more")',
        'div[role="button"]:has-text("Ver más")',
        'a:text-is("See more")',
        'span:text-matches("See more$", "i")',
        'div:text-matches("… See more$", "i")',
    ]
    for sel in selectors:
        try:
            elements = page.query_selector_all(sel)
            for el in elements:
                if el.is_visible():
                    el.click()
                    clicked = True
                    time.sleep(0.5)
        except Exception:
            pass
    return clicked


def extract_full_text(page) -> dict:
    """Extract content after expanding 'See more'."""
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

        const videos = [];
        const seenVids = new Set();
        document.querySelectorAll('video[src]:not([src^="blob:"])').forEach(v => {
            if (seenVids.has(v.src)) return;
            seenVids.add(v.src);
            videos.push({ src: v.src, poster: v.poster || '' });
        });

        // Strategy 1: story_message
        let text = '';
        const story = document.querySelector('[data-ad-rendering-role="story_message"]');
        if (story) {
            text = story.innerText || '';
            story.querySelectorAll('img').forEach(addImg);
        }

        // Strategy 2: article
        if (!text.trim()) {
            const article = document.querySelector('[role=article]');
            if (article) {
                text = article.innerText || '';
                article.querySelectorAll('img').forEach(addImg);
            }
        }

        // Strategy 3: dialog
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

        // Clean
        text = text.replace(/\\nAll reactions:[\\s\\S]*$/, '');
        text = text.replace(/\\nLike\\nComment\\nShare.*$/, '');
        text = text.replace(/\\nComments\\n.*$/, '');

        // Links
        const links = [];
        const seenLinks = new Set();
        const story2 = document.querySelector('[data-ad-rendering-role="story_message"]');
        if (story2) {
            story2.querySelectorAll('a[href]').forEach(a => {
                const href = a.href;
                if (href && href.startsWith('http') && !href.includes('facebook.com') && !seenLinks.has(href)) {
                    seenLinks.add(href);
                    links.push({ href, text: (a.innerText || '').trim() });
                }
            });
        }

        images.sort((a, b) => (b.width * b.height) - (a.width * a.height));
        return { text: text.trim(), images, videos, links };
    }""")


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


def clean_text(text: str) -> str:
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
        if re.match(r"^(Christian Camacho|You|Crow Systems|Tijuana PC) (shared|updated|added)\b", ls):
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
    garbage = ("Notifications", "Menu", "Facebook", "AllUnread", "See all", "Activity log")
    if any(text.strip().startswith(p) for p in garbage):
        text = ""
    return text


def build_markdown(fm: dict, data: dict) -> str:
    lines = []
    for vid in data.get("videos", []):
        local = vid.get("local_file")
        src = f"assets/{local}" if local else vid["src"]
        lines.append(f'<video controls src="{src}" style="width:100%; max-height:600px; border-radius:4px;"></video>')
        lines.append("")
    for img in data.get("images", []):
        alt = img.get("alt", "") or "Facebook image"
        fk = img.get("file") or ""
        if fk:
            lines.append(f"![{alt}](assets/{fk})")
        elif img.get("src"):
            lines.append(f"![{alt}]({img['src']})")
        lines.append("")
    text = data.get("text", "")
    if text:
        lines.append(text)
        lines.append("")
    for link in data.get("links", []):
        href = link["href"]
        lt = link.get("text") or href
        if any(d in href for d in ["youtube.com", "youtu.be"]):
            m = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})", href)
            if m:
                vid = m.group(1)
                lines.append(f'<iframe width="560" height="315" src="https://www.youtube.com/embed/{vid}" title="{lt}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe>')
            else:
                lines.append(f'<iframe loading="lazy" src="{href}" title="{lt}" style="width:100%; height:500px; border:0; border-radius:4px;"></iframe>')
        elif "soundcloud.com" in href:
            sc = re.sub(r"https?://soundcloud\.com/", "", href).rstrip("/")
            eu = f"https://w.soundcloud.com/player/?url=https%3A//soundcloud.com/{sc.replace('/', '%2F')}&color=%23ff5500&auto_play=false&hide_related=true&show_comments=false&show_user=true&show_reposts=false&show_teaser=false&visual=true"
            lines.append(f'<iframe width="100%" height="300" src="{eu}" title="SoundCloud player" frameborder="0" allow="autoplay; encrypted-media" scrolling="no" loading="lazy"></iframe>')
        elif lt and href:
            lines.append(f"[{lt}]({href})")
            lines.append("")
    body = "\n".join(lines).strip() + "\n"
    desc = text[:160].replace('"', '\\"').replace("\n", " ").strip() if text else fm.get("title", "")
    return "\n".join([
        "---",
        f'title: "{fm["title"]}"',
        f"created: {fm['created']}",
        f"updated: {fm['created']}",
        f'origin_link: "{fm["origin_link"]}"',
        f'description: "{desc}"',
        f"slug: {fm['slug']}",
        f"tags: {fm['tags']}",
        f"lang: {fm['lang']}",
        f"lang_group: {fm['slug']}",
        "---",
        "",
        body,
    ])


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


def process_post(page, filepath: Path, fm: dict) -> bool:
    """Process a single post. Returns True on success."""
    origin_link = fm["origin_link"]
    slug = fm.get("slug", filepath.stem)
    title = fm.get("title", "")
    created = fm.get("created", "")
    tags = fm.get("tags", "facebook-import")
    lang = fm.get("lang", "es")

    page.goto(origin_link, wait_until="domcontentloaded")
    human_delay(2, 4)
    human_move(page)

    # Click "See more" to expand text
    clicked = click_see_more(page)
    if clicked:
        human_delay(1, 2)

    # Extract full content
    data = extract_full_text(page)
    text = clean_text(data.get("text", ""))

    # Strip trailing "See more"
    if text.endswith("… See more"):
        text = text[:-len("… See more")].strip()
    elif text.endswith("... See more"):
        text = text[:-len("... See more")].strip()

    data["text"] = text

    # Update title if bad
    title_is_bad = re.match(r"^(Christian Camacho|You|Crow Systems|Tijuana PC|Facebook) (shared|updated|added|created)\b", title)
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
    }

    md = build_markdown(frontmatter, data)
    filepath.write_text(md, encoding="utf-8")
    return True


def main() -> int:
    # Find broken posts
    broken = []
    for f in sorted(OUTPUT_DIR.glob("*.md")):
        if f.name.startswith("_"):
            continue
        c = f.read_text("utf-8")
        if "… See more" in c or "... See more" in c:
            fm = parse_frontmatter(f)
            if fm.get("origin_link"):
                broken.append((f, fm))

    print(f"Found {len(broken)} posts with 'See more'")

    fixed = 0
    for i, (filepath, fm) in enumerate(broken):
        filename = filepath.name
        print(f"  [{i+1}/{len(broken)}] {filename[:60]}")

        # Retry up to 3 times with fresh browser
        for attempt in range(3):
            try:
                with sync_playwright() as p:
                    ctx = p.chromium.launch_persistent_context(
                        user_data_dir=str(CHROME_PROFILE),
                        headless=False,
                        args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                        no_viewport=True,
                    )
                    page = ctx.pages[0] if ctx.pages else ctx.new_page()
                    process_post(page, filepath, fm)
                    ctx.close()
                fixed += 1
                print(f"    FIXED")
                break
            except Exception as e:
                print(f"    Attempt {attempt+1} ERROR: {e}")
                time.sleep(2)
        else:
            print(f"    FAILED after 3 attempts")

        human_delay(1, 2)

    print(f"\nDone. Fixed {fixed}/{len(broken)} posts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
