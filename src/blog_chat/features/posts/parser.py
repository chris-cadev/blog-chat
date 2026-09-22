
import re
import yaml
from pathlib import Path


def _flatten_tags(raw):
    if not raw:
        return []
    if isinstance(raw, str):
        return [raw]
    result = []
    for item in raw:
        if isinstance(item, list):
            result.extend(_flatten_tags(item))
        else:
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
        "content": body.strip(),
    }
