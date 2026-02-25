import htmlmin


def minify_html(html: str) -> str:
    return htmlmin.minify(html, remove_empty_space=True)
