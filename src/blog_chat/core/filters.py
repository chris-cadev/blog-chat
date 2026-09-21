import re

import markdown
import nh3

ALLOWED_URL_SCHEMES = {"http", "https", "mailto"}

IFRAME_ATTRIBUTES = {
    "src",
    "width",
    "height",
    "style",
    "loading",
    "title",
    "allow",
    "allowfullscreen",
    "frameborder",
    "scrolling",
    "referrerpolicy",
}

ALLOWED_STYLE_PROPERTIES = {
    "position",
    "top",
    "left",
    "right",
    "bottom",
    "width",
    "height",
    "max-width",
    "max-height",
    "padding",
    "padding-bottom",
    "margin",
    "margin-bottom",
    "border",
    "border-radius",
    "overflow",
    "display",
    "flex",
    "flex-direction",
    "flex-wrap",
    "gap",
    "justify-content",
    "align-items",
    "align-content",
    "aspect-ratio",
    "background-color",
    "font-family",
    "font-size",
    "font-weight",
    "font-style",
    "line-height",
    "color",
    "text-align",
    "text-decoration",
    "white-space",
    "word-break",
    "line-break",
    "text-overflow",
}

ALLOWED_TAGS = nh3.ALLOWED_TAGS | {"iframe", "audio", "source", "img", "figure", "figcaption", "picture", "section", "input", "button", "label"}
ALLOWED_ATTRIBUTES = dict(nh3.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES["iframe"] = IFRAME_ATTRIBUTES
ALLOWED_ATTRIBUTES["audio"] = {"src", "controls", "preload", "type", "style", "controlslist"}
ALLOWED_ATTRIBUTES["source"] = {"src", "type"}
ALLOWED_ATTRIBUTES["img"] = {"src", "alt", "title", "loading", "width", "height", "style", "class"}
ALLOWED_ATTRIBUTES["figure"] = {"style", "class"}
ALLOWED_ATTRIBUTES["figcaption"] = {"style", "class"}
ALLOWED_ATTRIBUTES["picture"] = {"style", "class"}
ALLOWED_ATTRIBUTES["div"] = {"style", "class", "id"}
ALLOWED_ATTRIBUTES["span"] = {"style", "class", "id"}
ALLOWED_ATTRIBUTES["input"] = {"type", "placeholder", "style", "class", "id", "inputmode", "aria-label", "value"}
ALLOWED_ATTRIBUTES["button"] = {"type", "style", "class", "id"}
ALLOWED_ATTRIBUTES["label"] = {"style", "class", "for"}
ALLOWED_ATTRIBUTES["section"] = {"style", "class", "id", "aria-label", "data-expected"}

YT_ID_RE = re.compile(r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})")
# raw markdown link wrapped in <p> that markdown won't convert (e.g. <p> [▶️ text](youtube) </p>)
MARKDOWN_YT_P_RE = re.compile(
    r"<p>\s*\[([^\]]*)\]\(\s*(https?://(?:www\.)?(?:youtube\.com/watch\?v=[^\s\)]+|youtu\.be/[^\s\)]+))\s*\)\s*</p>",
    re.IGNORECASE | re.DOTALL,
)
# after markdown: <p><a href="youtube">...</a></p> as standalone paragraph
HTML_YT_P_RE = re.compile(
    r'<p>\s*<a\s[^>]*href="(https?://[^"]*(?:youtube\.com/watch\?v=[^"]+|youtu\.be/[^"]+))"[^>]*>(.*?)</a>\s*</p>',
    re.IGNORECASE | re.DOTALL,
)


def _yt_id(url: str) -> str | None:
    m = YT_ID_RE.search(url)
    return m.group(1) if m else None


def _yt_embed(url: str, label: str) -> str:
    vid = _yt_id(url)
    if not vid:
        return f"[{label}]({url})"
    safe_label = (label.strip() or "YouTube video player").replace('"', "&quot;")
    return (
        f'<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;margin-bottom:1rem;">'
        f'<iframe src="https://www.youtube-nocookie.com/embed/{vid}" '
        f'style="position:absolute;top:0;left:0;width:100%;height:100%;border:0;" '
        f'title="{safe_label}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
        f"allowfullscreen loading=\"lazy\" referrerpolicy=\"strict-origin-when-cross-origin\"></iframe></div>"
    )


def parse_to_markdown(text: str) -> str:
    from blog_chat.app import CSP_NONCE

    if text:
        # pre-process: markdown links inside raw <p> blocks that markdown ignores
        def _repl_raw(m):
            label, url = m.group(1), m.group(2)
            vid = _yt_id(url)
            if vid:
                return _yt_embed(url, label)
            return m.group(0)

        text = MARKDOWN_YT_P_RE.sub(_repl_raw, text)

    html = markdown.markdown(
        text or "",
        extensions=["fenced_code", "codehilite"],
        extension_configs={"codehilite": {"css_class": "highlight", "guess_lang": False}},
    )
    # post-process: standalone <p><a href="youtube">...</a></p> -> embed
    def _repl_html(m):
        url, inner = m.group(1), m.group(2)
        plain = re.sub(r"<[^>]+>", "", inner).strip()
        vid = _yt_id(url)
        if vid:
            return _yt_embed(url, plain or inner)
        return m.group(0)

    html = HTML_YT_P_RE.sub(_repl_html, html)
    cleaned = nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_URL_SCHEMES,
        link_rel="noopener noreferrer nofollow",
        filter_style_properties=ALLOWED_STYLE_PROPERTIES,
        set_tag_attribute_values={"a": {"target": "_blank"}},
    )

    nonce = CSP_NONCE.get(None)
    if nonce:
        cleaned = re.sub(
            r"<iframe\b",
            f'<iframe nonce="{nonce}"',
            cleaned,
        )

    return cleaned


def plain_excerpt(text: str, length: int = 160) -> str:
    if not text:
        return ""
    # Remove YouTube music blocks entirely from excerpt
    cleaned = MARKDOWN_YT_P_RE.sub("", text)
    cleaned = re.sub(
        r"\[([^\]]*)\]\(\s*https?://(?:www\.)?(?:youtube\.com/watch\?v=[^\s\)]+|youtu\.be/[^\s\)]+)\s*\)",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    # Remove markdown images
    cleaned = re.sub(r"!\[.*?\]\(.*?\)", "", cleaned)
    # Remove HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    # Convert markdown links [text](url) -> text
    cleaned = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", cleaned)
    # Remove bold/italic markers
    cleaned = re.sub(r"(\*\*|__)(.*?)\1", r"\2", cleaned)
    cleaned = re.sub(r"(\*|_)(.*?)\1", r"\2", cleaned)
    # Remove inline code
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    # Remove markdown headers
    cleaned = re.sub(r"^\s{0,3}#{1,6}\s+", "", cleaned, flags=re.MULTILINE)
    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) > length:
        truncated = cleaned[:length]
        # avoid cutting mid-word
        if " " in truncated:
            truncated = truncated.rsplit(" ", 1)[0]
        return truncated + "…"
    return cleaned


def add_filter(templates, name: str, func):
    templates.env.filters[name] = func


def add_markdown_filter(templates):
    add_filter(templates, "markdown", parse_to_markdown)
    add_filter(templates, "plain_excerpt", plain_excerpt)
