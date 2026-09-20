import hashlib
from pathlib import Path

_CACHE: dict[str, str] = {}
_STATIC_DIR = Path("static")


def _file_hash(path: Path) -> str | None:
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()[:8]
    except FileNotFoundError:
        return None
    except OSError:
        return None


def static_url(path: str) -> str:
    """Return versioned /static URL, e.g. /static/main.css?v=abc12345.
    Hash is first 8 hex of file md5; falls back to unversioned if missing.
    Cached per process to avoid re-hashing on every template render.
    """
    if path in _CACHE:
        return _CACHE[path]
    clean = path.lstrip("/")
    file_path = _STATIC_DIR / clean
    h = _file_hash(file_path)
    url = f"/static/{clean}?v={h}" if h else f"/static/{clean}"
    _CACHE[path] = url
    # also cache the lstrip variant for flexibility
    _CACHE[clean] = url
    return url


def clear_cache() -> None:
    _CACHE.clear()
