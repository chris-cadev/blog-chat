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

ALLOWED_TAGS = nh3.ALLOWED_TAGS | {"iframe"}
ALLOWED_ATTRIBUTES = dict(nh3.ALLOWED_ATTRIBUTES)
ALLOWED_ATTRIBUTES["iframe"] = IFRAME_ATTRIBUTES
ALLOWED_ATTRIBUTES["div"] = {"style"}


def parse_to_markdown(text: str) -> str:
    from blog_chat.app import CSP_NONCE

    html = markdown.markdown(text or "")
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


def add_filter(templates, name: str, func):
    templates.env.filters[name] = func


def add_markdown_filter(templates):
    add_filter(templates, "markdown", parse_to_markdown)
