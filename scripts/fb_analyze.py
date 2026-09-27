#!/usr/bin/env python3
"""Analyze and score all Facebook draft posts for quality and categorization.

Reads content/_drafts/fb/*.md, scores each post, and generates a ranked
report with categories, quality scores, and recommendations.

Usage:
    python scripts/fb_analyze.py
    python scripts/fb_analyze.py --json   # JSON only, no table
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

DRAFTS_DIR = Path("content/_drafts/fb")
REPORT_FILE = DRAFTS_DIR / "_analysis_report.json"
BAD_POSTS_FILE = DRAFTS_DIR / "_bad_posts.txt"

# --- Patterns for categorization ---

TECHNICAL_KEYWORDS = re.compile(
    r"(linux|debian|ubuntu|python|javascript|css|html|programaci[oó]n|"
    r"desarrollo|servidor|git|github|docker|api|código|code|hack|"
    r"software|hardware|computadora|pc|windows|mac|android|ios|"
    r"tecnolog[ií]a|tech|internet|red|wifi|router|servidor|data|"
    r"machine learning|ia|ai|inteligencia artificial|blockchain|"
    r"open source|foss|gnu|kernel|terminal|bash|shell|vim|neovim|"
    r"emacs|arch|gentoo|fedora|centos|manjaro|pop.os|mint|"
    r"framework|librería|api|rest|graphql|database|sql|mongo|"
    r"frontend|backend|devops|cloud|aws|azure|gcp|"
    r"videojuego|gamer|minecraft|steam|playstation|xbox|nintendo)",
    re.IGNORECASE,
)

LIFE_EVENT_KEYWORDS = re.compile(
    r"(started school|graduated|new job|moved|birthday|anniversary|"
    r"se casó|casamiento|boda|nacimiento|cumpleaños|"
    r"life event|evento de vida|universidad|escuela|trabajo nuevo)",
    re.IGNORECASE,
)

SHARED_LINK_RE = re.compile(
    r"^(Christian Camacho )?compartió (un enlace|una publicación|una foto|un video|una publicación de)",
    re.IGNORECASE,
)

ACTION_TITLE_RE = re.compile(
    r"^(Christian Camacho|You|Crow Systems|Tijuana PC|Facebook|)"
    r" (shared|updated|added|created|creó|actualizó|compartió)\b",
    re.IGNORECASE,
)

FACEBOOK_NOISE_RE = re.compile(
    r"(notifications|menu|allunread|comment as|view more|like\ncomment|"
    r"reply\n|all reactions|see more comments)",
    re.IGNORECASE,
)


# --- Helpers ---

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body_text)."""
    match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}, content
    fm: dict[str, str] = {}
    for line in match.group(1).split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            fm[key.strip()] = val.strip().strip('"')
    return fm, content[match.end() :].strip()


def strip_media(body: str) -> str:
    """Remove image/video/link markdown, return plain text only."""
    text = re.sub(r"!\[.*?\]\(.*?\)", "", body)
    text = re.sub(r"<video[^>]*>.*?</video>", "", text, flags=re.DOTALL)
    text = re.sub(r"<iframe[^>]*>.*?</iframe>", "", text, flags=re.DOTALL)
    text = re.sub(r"\[.*?\]\(https?://[^\)]+\)", "", text)
    text = re.sub(r"<[^>]+>", "", text)
    return text.strip()


def count_images(body: str) -> int:
    return len(re.findall(r"!\[.*?\]\(.*?\)", body))


def description_quality(desc: str, title: str, body_text: str) -> float:
    """Score description quality: 0=terrible, 1=bad, 2=ok, 3=good."""
    if not desc or desc.strip() == "":
        return 0.0
    desc_lower = desc.lower().strip()
    title_lower = title.lower().strip()
    body_lower = body_text.lower().strip()[:200]
    # Same as title
    if desc_lower == title_lower:
        return 0.5
    # Contains title or title contains it
    if title_lower in desc_lower or desc_lower in title_lower:
        return 1.0
    # Very similar to body start
    if desc_lower[:50] == body_lower[:50]:
        return 1.0
    # Too short
    if len(desc) < 10:
        return 1.0
    # Looks like UI noise
    if FACEBOOK_NOISE_RE.search(desc):
        return 0.0
    # Looks like a real description
    if len(desc) > 20:
        return 3.0
    return 2.0


# --- Scoring ---

def score_post(filepath: Path, bad_posts: set[str]) -> dict:
    """Score a single post. Returns full analysis dict."""
    content = filepath.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)
    title = fm.get("title", filepath.stem)
    desc = fm.get("description", "")
    origin_url = fm.get("origin_link", "")
    tags = fm.get("tags", "")

    body_text = strip_media(body)
    n_images = count_images(body)
    has_video = "<video" in body.lower()
    has_iframe = "<iframe" in body.lower()
    body_len = len(body_text)

    # --- Category ---
    category = categorize(title, body_text, origin_url, has_video, has_iframe)

    # --- Score (0-10) ---
    score = 0.0

    # Body length (max 3 pts)
    if body_len >= 200:
        score += 3.0
    elif body_len >= 100:
        score += 2.0
    elif body_len >= 30:
        score += 1.0

    # Has original text content (max 2 pts)
    if body_len > 0 and not is_only_media(body, n_images, has_video, has_iframe):
        score += 2.0
    elif n_images > 0 and body_len < 10:
        score += 0.5  # solo foto

    # Description quality (max 2 pts)
    desc_score = description_quality(desc, title, body_text)
    score += desc_score * 0.67  # normalize to ~2

    # Title quality (max 1.5 pts)
    if ACTION_TITLE_RE.match(title):
        score += 0.0
    elif len(title) > 10 and not title.startswith("christian-camacho-shared"):
        score += 1.5
    elif len(title) > 5:
        score += 0.75

    # Penalties
    if filepath.name in bad_posts:
        score -= 3.0
    if FACEBOOK_NOISE_RE.search(body):
        score -= 2.0
    if body_text.count("\n") > 5 and body_len < 50:
        # lots of empty lines, likely garbage
        score -= 1.0

    # Bonuses for content type
    if category == "técnico":
        score += 1.5
    elif category == "personal":
        score += 1.0
    elif category == "frase_reflexión":
        score += 0.8

    score = max(0.0, min(10.0, score))

    # --- Recommendation ---
    if score >= 9.0:
        recommendation = "excelente"
    elif score >= 8.0:
        recommendation = "bueno"
    elif score >= 7.5:
        recommendation = "mejorable"
    else:
        recommendation = "eliminar"

    return {
        "filename": filepath.name,
        "title": title,
        "category": category,
        "score": round(score, 2),
        "recommendation": recommendation,
        "body_length": body_len,
        "n_images": n_images,
        "has_video": has_video,
        "description_quality": desc_score,
        "origin_url": origin_url,
    }


def is_only_media(body: str, n_images: int, has_video: bool, has_iframe: bool) -> bool:
    text = strip_media(body)
    return len(text) < 10 and (n_images > 0 or has_video or has_iframe)


def categorize(title: str, body_text: str, origin_url: str, has_video: bool, has_iframe: bool) -> str:
    combined = f"{title} {body_text}"

    if LIFE_EVENT_KEYWORDS.search(combined):
        return "evento_vida"
    if SHARED_LINK_RE.match(title):
        return "link_compartido"
    if origin_url and "/media/set/" in origin_url:
        return "álbum"
    if origin_url and "/videos/" in origin_url:
        return "video"
    if has_iframe and not body_text.strip():
        return "embed_solo"
    if has_video and not body_text.strip():
        return "video_solo"
    if is_only_media("", count_images(body_text), has_video, has_iframe):
        return "solo_foto"
    if TECHNICAL_KEYWORDS.search(combined):
        return "técnico"
    if is_conversation(body_text):
        return "conversación"
    if is_meme_humor(combined):
        return "meme_humor"
    if is_phrase(combined):
        return "frase_reflexión"
    return "personal"


def is_conversation(text: str) -> bool:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if len(lines) < 2:
        return False
    chat_patterns = sum(
        1 for l in lines
        if re.match(r"^[A-Z][a-z]+:", l) or re.match(r"^- ", l) or "→" in l or ":" in l[:15]
    )
    return chat_patterns >= len(lines) * 0.4


def is_meme_humor(text: str) -> bool:
    humor_signals = ["jaja", "xD", "XD", "XD", "lol", " meme ", "chiste", "gracioso", "risa", "😂", "🤣", "😆"]
    return any(s in text.lower() for s in humor_signals)


def is_phrase(text: str) -> bool:
    if len(text) < 100:
        return False
    sentences = text.split(".")
    return len(sentences) <= 3 and any(
        w in text.lower()
        for w in ["vida", "sueño", "corazón", "alma", "momento", "tiempo", "hoy", "siempre", "nunca"]
    )


# --- Main ---

def main() -> int:
    files = sorted(DRAFTS_DIR.glob("*.md"))
    print(f"Analyzing {len(files)} posts in {DRAFTS_DIR}\n")

    # Load bad posts list
    bad_posts: set[str] = set()
    if BAD_POSTS_FILE.exists():
        for line in BAD_POSTS_FILE.read_text(encoding="utf-8").splitlines():
            if "\t" in line:
                bad_posts.add(line.split("\t")[0])
            elif line.strip():
                bad_posts.add(line.strip())

    results = []
    for f in files:
        results.append(score_post(f, bad_posts))

    # Sort by score descending
    results.sort(key=lambda r: r["score"], reverse=True)

    # Stats
    categories: dict[str, list] = {}
    recommendations: dict[str, int] = {}
    for r in results:
        cat = r["category"]
        rec = r["recommendation"]
        categories.setdefault(cat, []).append(r)
        recommendations[rec] = recommendations.get(rec, 0) + 1

    report = {
        "total_posts": len(results),
        "score_stats": {
            "avg": round(sum(r["score"] for r in results) / len(results), 2) if results else 0,
            "max": results[0]["score"] if results else 0,
            "min": results[-1]["score"] if results else 0,
        },
        "recommendations": recommendations,
        "categories": {cat: len(posts) for cat, posts in categories.items()},
        "posts": results,
    }

    REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    # Print summary
    print("=" * 70)
    print("RESUMEN DE ANÁLISIS")
    print("=" * 70)
    print(f"Total posts: {len(results)}")
    print(f"Promedio score: {report['score_stats']['avg']}/10")
    print(f"Mejor score: {report['score_stats']['max']}/10")
    print(f"Peor score: {report['score_stats']['min']}/10")
    print()

    print("Por recomendación:")
    for rec in ["excelente", "bueno", "mejorable", "eliminar"]:
        count = recommendations.get(rec, 0)
        bar = "█" * count
        print(f"  {rec:12s} {count:3d}  {bar}")
    print()

    print("Por categoría:")
    for cat, posts in sorted(categories.items(), key=lambda x: -len(x[1])):
        avg_score = sum(p["score"] for p in posts) / len(posts)
        print(f"  {cat:20s} {len(posts):3d}  (avg {avg_score:.1f})")
    print()

    # Top 10
    print("=" * 70)
    print("TOP 10 POSTS")
    print("=" * 70)
    for i, r in enumerate(results[:10], 1):
        print(f"  {i:2d}. [{r['score']:4.1f}] {r['category']:15s}  {r['title'][:60]}")
    print()

    # Bottom 10
    print("BOTTOM 10 POSTS (candidatos a eliminar)")
    print("-" * 70)
    for i, r in enumerate(results[-10:], 1):
        print(f"  {i:2d}. [{r['score']:4.1f}] {r['category']:15s}  {r['title'][:60]}")
    print()

    print(f"Reporte completo: {REPORT_FILE}")

    if "--json" in sys.argv:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
