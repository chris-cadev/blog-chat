#!/usr/bin/env python3
"""Capture comments from a Facebook post/album as a screenshot.

Usage:
    python scripts/fb_comments_screenshot.py <url> [output_name]

Example:
    python scripts/fb_comments_screenshot.py \
        "https://www.facebook.com/media/set/?set=a.114766901923364&type=3" \
        mis-creaciones-2011_comments
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ASSETS_DIR = Path("content/_drafts/fb/assets")
CHROME_PROFILE = Path("facebook_chrome_profile_screenshot")


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


def scroll_to_comments(page) -> bool:
    """Scroll down to find and isolate the comments section."""
    # Try to find comments container
    selectors = [
        "[aria-label*='Comment']",
        "[aria-label*='Comentario']",
        "[data-ad-rendering-role='comment']",
        "div[role='article'] span:has-text('que chidas')",
    ]
    for sel in selectors:
        el = page.query_selector(sel)
        if el:
            el.scroll_into_view_if_needed()
            human_delay(0.5, 1)
            return True
    # Fallback: scroll down a few times
    for _ in range(5):
        page.mouse.wheel(0, 400)
        human_delay(0.3, 0.6)
    return False


def capture_comments(page, url: str, output_name: str) -> str | None:
    """Visit URL, scroll to comments, screenshot that section."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    dest = ASSETS_DIR / f"{output_name}.png"

    try:
        page.goto(url, wait_until="domcontentloaded")
        human_delay(3, 5)
        human_move(page)

        # First, try to click on the album to open it in dialog
        # For album URLs, the comments might be in the dialog
        first_img = page.query_selector("img[data-imgperflogname='profileCoverPhoto']") or \
                    page.query_selector("img[src*='scontent']")
        if first_img:
            first_img.click()
            human_delay(2, 3)

        # Scroll to find comments
        scroll_to_comments(page)
        human_delay(1, 2)

        # Try to screenshot the comments area
        # Strategy 1: find the comments section specifically
        comments_area = page.query_selector("[aria-label*='Comment']") or \
                        page.query_selector("[aria-label*='Comentario']") or \
                        page.query_selector("[data-ad-rendering-role='comment']")

        if comments_area:
            box = comments_area.bounding_box()
            if box:
                # Expand the capture area to include some context above
                page.screenshot(
                    path=str(dest),
                    clip={
                        "x": max(0, box["x"] - 20),
                        "y": max(0, box["y"] - 80),
                        "width": min(box["width"] + 40, 700),
                        "height": min(box["height"] + 160, 800),
                    },
                )
                return f"{output_name}.png"

        # Strategy 2: find the dialog/post and capture lower portion (where comments are)
        dialog = page.query_selector("[role=dialog]")
        if dialog:
            box = dialog.bounding_box()
            if box:
                # Capture the bottom half of the dialog (comments area)
                page.screenshot(
                    path=str(dest),
                    clip={
                        "x": max(0, box["x"]),
                        "y": max(0, box["y"] + box["height"] * 0.4),
                        "width": min(box["width"], 700),
                        "height": min(box["height"] * 0.6, 600),
                    },
                )
                return f"{output_name}.png"

        # Strategy 3: viewport clip around center-bottom
        page.screenshot(
            path=str(dest),
            clip={"x": 50, "y": 300, "width": 650, "height": 500},
        )
        return f"{output_name}.png"

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: fb_comments_screenshot.py <url> [output_name]", file=sys.stderr)
        return 1

    url = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) > 2 else "fb_comments"

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE),
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            no_viewport=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()

        result = capture_comments(page, url, output_name)
        ctx.close()

    if result:
        print(f"Saved: {ASSETS_DIR / result}")
        return 0
    else:
        print("Failed to capture comments", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
