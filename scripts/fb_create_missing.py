#!/usr/bin/env python3
"""Create markdown for all URLs in facebook_progress.json that don't have a markdown file yet.

Run in background. Saves progress after each post (crash-safe).
"""
from __future__ import annotations
import json, re, random, time, unicodedata
from datetime import datetime
from pathlib import Path
import dateparser
from playwright.sync_api import sync_playwright

OUTPUT_DIR = Path("content/_drafts/fb")
ASSETS_DIR = OUTPUT_DIR / "assets"
CHROME_PROFILE = Path("facebook_chrome_profile")
PROGRESS_FILE = Path("facebook_progress.json")
EXPORT_PROGRESS = OUTPUT_DIR / "_export_progress.json"


def human_delay(a=0.5, b=2.5):
    mean = (a + b) / 2
    std = (b - a) / 4
    time.sleep(max(a, min(b, random.gauss(mean, std))))


def slugify(text):
    text = unicodedata.normalize("NFC", text).strip().lower()
    text = re.sub(r"[^a-z0-9\u00e0-\u00ff]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-")[:80]


def parse_date(raw, reference=None):
    if not raw or not raw.strip():
        return None
    settings = {"RELATIVE_BASE": reference or datetime.now()}
    dt = dateparser.parse(raw.strip(), languages=["en", "es"], settings=settings)
    return dt.strftime("%Y-%m-%d") if dt else None


def download_image(request, url, name):
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    ext = ".jpg"
    for e in [".png", ".webp", ".gif"]:
        if e in url.split("?")[0]:
            ext = e
            break
    filename = f"{name}{ext}"
    dest = ASSETS_DIR / filename
    if dest.exists() and dest.stat().st_size > 500:
        return filename
    try:
        resp = request.get(url, headers={"Referer": "https://www.facebook.com/", "Accept": "image/*"})
        if resp.ok and len(resp.body()) > 500:
            dest.write_bytes(resp.body())
            return filename
    except Exception:
        pass
    return None


def download_video(request, url, name):
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


EXTRACT_JS = """() => {
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

    // Strategy 1: story_message
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
    // Strategy 2: article
    if (!text.trim()) {
        const article = document.querySelector('[role=article]');
        if (article) { text = article.innerText || ''; article.querySelectorAll('img').forEach(addImg); }
    }
    // Strategy 3: right dialog (skip notifications)
    if (!text.trim()) {
        const dialogs = document.querySelectorAll('[role=dialog]');
        for (const d of dialogs) {
            const t = (d.innerText || '').trim();
            if (t.startsWith('Notifications') || t.startsWith('Menu')) continue;
            if (t.length > 20) { text = t; d.querySelectorAll('img').forEach(addImg); break; }
        }
    }
    // Strategy 4: body fallback
    if (!text.trim()) {
        text = document.body?.innerText || '';
    }
    images.sort((a, b) => (b.width * b.height) - (a.width * a.height));
    return { text: text.trim(), images, videos, links };
}"""


def build_markdown(title, date, url, text, local_images, local_videos, links=None):
    slug = slugify(text[:60]) or slugify(title[:60]) or "fb-post"
    filename = f"{date}-{slug}.md"

    lines = []
    for vid in local_videos:
        if vid.get("local_file"):
            lines.append(f'<video controls src="assets/{vid["local_file"]}" style="width:100%; max-height:600px; border-radius:4px;"></video>')
        lines.append("")
    for img in local_images:
        lines.append(f"![{img.get('alt', 'Facebook image')}](assets/{img['file']})")
        lines.append("")
    if text:
        lines.append(text)
    for link in (links or []):
        href = link["href"]
        lt = link.get("text") or href
        if any(d in href for d in ["youtube.com", "youtu.be"]):
            lines.append(f'<iframe loading="lazy" src="{href}" title="{lt}" style="width:100%; height:500px; border:0; border-radius:4px;"></iframe>')
        elif lt:
            lines.append(f"[{lt}]({href})")

    body = "\n".join(lines).strip() + "\n"
    t = title[:80].replace('"', '\\"').replace('\n', ' ').strip()
    if len(title) > 80:
        t += "..."

    fm = f'---\ntitle: "{t}"\ncreated: {date}\nupdated: {date}\norigin_link: "{url}"\ndescription: "{t}"\nslug: {slug}\ntags: [facebook-import]\nlang: es\nlang_group: {slug}\n---'
    return fm + "\n\n" + body, filename


def load_export_progress():
    if EXPORT_PROGRESS.exists():
        return set(json.loads(EXPORT_PROGRESS.read_text()))
    return set()


def save_export_progress(done):
    EXPORT_PROGRESS.write_text(json.dumps(list(done)))


def main():
    # Load URLs
    progress = json.loads(PROGRESS_FILE.read_text())
    seen = progress["seen"]

    # Find which already have markdown
    done = load_export_progress()
    for f in OUTPUT_DIR.glob("*.md"):
        content = f.read_text()
        m = re.search(r'origin_link:\s*"([^"]+)"', content)
        if m:
            done.add(m.group(1))
    save_export_progress(done)

    # Support --batch-file for parallel agents
    import sys
    if len(sys.argv) > 1 and sys.argv[1].startswith("--batch-file"):
        batch_file = Path(sys.argv[2])
        missing = [u.strip() for u in batch_file.read_text().splitlines() if u.strip() and u.strip() not in done]
        profile_num = sys.argv[3] if len(sys.argv) > 3 else "0"
        chrome_dir = Path(f"facebook_chrome_profile_{profile_num}")
    else:
        missing = [u for u in seen if u not in done]
        chrome_dir = CHROME_PROFILE

    print(f"Total: {len(seen)}, Done: {len(done)}, Missing: {len(missing)}")

    if not missing:
        print("All posts have markdown!")
        return

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(chrome_dir),
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            no_viewport=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        for i, url in enumerate(missing):
            print(f"[{i+1}/{len(missing)}] {url[:80]}...")
            try:
                page.goto(url, wait_until="domcontentloaded")
                human_delay(2, 4)

                data = page.evaluate(EXTRACT_JS)

                # Clean text
                text = data.get("text", "")
                garbage = ("Notifications", "Menu", "Facebook", "AllUnread", "See all", "Activity log")
                if text and any(text.strip().startswith(p) for p in garbage):
                    text = ""
                lines = text.split("\n")
                cleaned = []
                for line in lines:
                    ls = line.strip()
                    if not ls:
                        cleaned.append("")
                        continue
                    if re.match(r"^(Christian Camacho|You|Crow Systems|Tijuana PC|Facebook) (shared|updated|added|created)\b", ls):
                        continue
                    if ls in ("Like", "Comment", "Share", "Write a comment...", "Facebook", "Comments", "See all", "Reply", "Comment as Christian Camacho"):
                        continue
                    if re.match(r"^(All reactions:|Like\n|Comment as |Be the first|No comments|View more|Shared with)", ls):
                        continue
                    if "Comment as " in ls:
                        break
                    cleaned.append(line)
                text = "\n".join(cleaned).strip()

                # Download images
                local_images = []
                for j, img in enumerate(data.get("images", [])):
                    name = f"{slugify(text[:40] if text else 'fb')}-{i}_{j}"
                    f = download_image(ctx.request, img["src"], name)
                    if f:
                        local_images.append({"file": f, "alt": img.get("alt", "")})

                # Download videos
                local_videos = []
                for j, vid in enumerate(data.get("videos", [])):
                    name = f"{slugify(text[:40] if text else 'fb')}-{i}_v{j}"
                    f = download_video(ctx.request, vid["src"], name)
                    local_videos.append({"src": vid["src"], "local_file": f})

                # Determine date from URL or scrape time
                date = datetime.now().strftime("%Y-%m-%d")
                title = text[:80].split("\n")[0].strip() if text else "Facebook post"
                if not title or len(title) < 3:
                    title = "Facebook post"

                md, filename = build_markdown(title, date, url, text, local_images, local_videos, data.get("links", []))
                filepath = OUTPUT_DIR / filename
                filepath.write_text(md, encoding="utf-8")

                done.add(url)
                save_export_progress(done)
                print(f"  -> {filename}")

            except Exception as e:
                print(f"  ERROR: {e}")

            human_delay(1, 3)

        ctx.close()

    print(f"\nDone! {len(done)} total posts have markdown.")


if __name__ == "__main__":
    main()
