#!/usr/bin/env python3
"""Open Facebook in a browser for manual login.

Session is saved to facebook_chrome_profile/ and reused by other fb_ scripts.

Usage:
    python scripts/fb_login.py
"""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright

CHROME_PROFILE = Path("facebook_chrome_profile")


def main() -> int:
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(CHROME_PROFILE),
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            no_viewport=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
        print("Log in in the browser. Close the window when done.")
        try:
            page.wait_for_event("close", timeout=0)
        except Exception:
            pass
        ctx.close()
    return 0


raise SystemExit(main())
