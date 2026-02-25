import minify_html


def minify_html_func(html: str) -> str:
    return minify_html.minify(
        html,
        keep_comments=False,
        keep_html_and_head_opening_tags=True,
        minify_css=False,
        minify_js=False,
        remove_processing_instructions=True
    )
