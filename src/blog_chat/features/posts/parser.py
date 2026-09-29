
import re
import yaml
from pathlib import Path


_MD_IMG_RE = re.compile(r"(!\[[^\]]*\]\()([^)]+)(\))")
_HTML_SRC_RE = re.compile(r'((?:img|source|video|audio)\s[^>]*src=")([^"]+)(")')


_MEDIA_RE = re.compile(r"\.(jpe?g|png|gif|webp|svg|bmp|ico|wav|mp3|ogg|opus|mp4|webm|mov|avi|mkv)$", re.IGNORECASE)


def _rewrite_relative_paths(body: str, file_path: Path) -> str:
    def _resolve(rel: str) -> str:
        if rel.startswith(("/", "http://", "https://", "mailto:")):
            return rel
        resolved = (file_path.parent / rel).resolve()
        try:
            suffix = resolved.relative_to(Path("content").resolve())
        except ValueError:
            return rel
        parts = suffix.parts
        if not parts:
            return rel
        if parts[0] == "_drafts":
            return "/drafts" + "/" + "/".join(parts[1:])
        if len(parts) >= 2 and _MEDIA_RE.search(parts[-1]):
            return "/static/posts/" + parts[-1]
        return rel

    def _replace_md(m: re.Match) -> str:
        alt, ref, close = m.group(1), m.group(2), m.group(3)
        return f"{alt}{_resolve(ref)}{close}"

    def _replace_src(m: re.Match) -> str:
        pre, src, close = m.group(1), m.group(2), m.group(3)
        return f'{pre}{_resolve(src)}{close}'

    body = _MD_IMG_RE.sub(_replace_md, body)
    body = _HTML_SRC_RE.sub(_replace_src, body)
    return body


def _flatten_tags(raw):
    if not raw:
        return []
    if isinstance(raw, str):
        return [raw]
    result = []
    for item in raw:
        if isinstance(item, list):
            result.extend(_flatten_tags(item))
        elif item is not None and item != "":
            result.append(item)
    return result


def parse_markdown_file(file_path: Path) -> dict | None:
    content = file_path.read_text(encoding="utf-8")

    frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)

    if frontmatter_match:
        try:
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
        except yaml.YAMLError:
            frontmatter = {}
        body = content[frontmatter_match.end():]
    else:
        frontmatter = {}
        body = content

    return {
        "title": frontmatter.get("title", file_path.stem),
        "slug": frontmatter.get("slug", file_path.stem),
        "tags": _flatten_tags(frontmatter.get("tags")),
        "created": frontmatter.get("created", ""),
        "updated": frontmatter.get("updated", ""),
        "description": frontmatter.get("description", None),
        "lang": frontmatter.get("lang", None),
        "lang_group": frontmatter.get("lang_group", None),
        "pinned": bool(frontmatter.get("pinned", False)),
        "css_class": frontmatter.get("css_class", None),
        "content": _rewrite_relative_paths(body.strip(), file_path),
    }
