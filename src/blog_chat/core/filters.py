import markdown


def parse_to_markdown(text: str) -> str:
    return markdown.markdown(text or "")


def add_filter(templates, name: str, func):
    templates.env.filters[name] = func


def add_markdown_filter(templates):
    add_filter(templates, "markdown", parse_to_markdown)
