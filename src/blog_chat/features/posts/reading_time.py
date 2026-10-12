import math
import re

WPM = 200

_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_RE = re.compile(r"`[^`]*`")
_IMAGE_RE = re.compile(r"!\[.*?\]\(.*?\)")
_HTML_RE = re.compile(r"<[^>]+>")
_LINK_RE = re.compile(r"\[([^\]]+)\]\([^\)]+\)")


def strip_for_count(text: str) -> str:
    if not text:
        return ""
    # order matters: fences before inline
    cleaned = _FENCE_RE.sub(" ", text)
    cleaned = _INLINE_RE.sub(" ", cleaned)
    cleaned = _IMAGE_RE.sub("", cleaned)
    cleaned = _HTML_RE.sub(" ", cleaned)
    cleaned = _LINK_RE.sub(r"\1", cleaned)
    return cleaned


def _label(minutes: int, seconds: int) -> str:
    if minutes == 0:
        return f"{seconds}s"
    if seconds == 0:
        return f"{minutes}m"
    return f"{minutes}m {seconds}s"


def _iso(minutes: int, seconds: int) -> str:
    if minutes and seconds:
        return f"PT{minutes}M{seconds}S"
    if minutes:
        return f"PT{minutes}M"
    return f"PT{seconds}S"


def format_aria(minutes: int, seconds: int, lang: str = "en") -> str:
    lang = lang or "en"
    if lang not in ("en", "es", "fr"):
        lang = "en"

    def _min(n):
        if lang == "en":
            return "1 minute" if n == 1 else f"{n} minutes"
        if lang == "es":
            return "1 minuto" if n == 1 else f"{n} minutos"
        return "1 minute" if n == 1 else f"{n} minutes"  # fr

    def _sec(n):
        if lang == "en":
            return "1 second" if n == 1 else f"{n} seconds"
        if lang == "es":
            return "1 segundo" if n == 1 else f"{n} segundos"
        return "1 seconde" if n == 1 else f"{n} secondes"  # fr

    if minutes and seconds:
        return f"{_min(minutes)} {_sec(seconds)}"
    if minutes:
        return _min(minutes)
    return _sec(seconds)


def reading_time_for(text: str, wpm: int = WPM) -> dict:
    cleaned = strip_for_count(text or "")
    words = len(re.findall(r"\w+", cleaned))
    # ceil(words / wpm * 60)
    total = math.ceil(words / wpm * 60) if words else 0
    # no rounding for preview — exact seconds, min 5
    # shortcut: rounding to 5s disabled, when to upgrade: re-enable ((total+2)//5)*5
    rounded = max(5, total)
    minutes, seconds = divmod(rounded, 60)
    return {
        "words": words,
        "total_seconds": rounded,
        "minutes": minutes,
        "seconds": seconds,
        "label": _label(minutes, seconds),
        "iso_duration": _iso(minutes, seconds),
    }
