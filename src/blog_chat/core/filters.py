import markdown
import nh3

ALLOWED_URL_SCHEMES = {"http", "https", "mailto"}


def parse_to_markdown(text: str) -> str:
    html = markdown.markdown(text or "")
    return nh3.clean(
        html,
        url_schemes=ALLOWED_URL_SCHEMES,
        link_rel="noopener noreferrer nofollow",
    )


def add_filter(templates, name: str, func):
    templates.env.filters[name] = func


def add_markdown_filter(templates):
    add_filter(templates, "markdown", parse_to_markdown)
