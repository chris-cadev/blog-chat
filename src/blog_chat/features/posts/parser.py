
import re
import yaml
from pathlib import Path


def parse_markdown_file(file_path: Path) -> dict | None:
    content = file_path.read_text(encoding="utf-8")

    frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)

    if frontmatter_match:
        frontmatter = yaml.safe_load(frontmatter_match.group(1))
        body = content[frontmatter_match.end():]
    else:
        frontmatter = {}
        body = content

    return {
        "title": frontmatter.get("title", file_path.stem),
        "slug": frontmatter.get("slug", file_path.stem),
        "tags": frontmatter.get("tags", []),
        "created": frontmatter.get("created", ""),
        "updated": frontmatter.get("updated", ""),
        "content": body.strip(),
    }
