import pytest
from blog_chat.core.filters import parse_to_markdown, add_filter
from blog_chat.app import CSP_NONCE


class TestParseToMarkdown:
    def test_parse_plain_text(self):
        result = parse_to_markdown("Hello World")
        assert result == "<p>Hello World</p>"

    def test_parse_markdown_headers(self):
        result = parse_to_markdown("# Header\n\nParagraph")
        assert "<h1>Header</h1>" in result
        assert "<p>Paragraph</p>" in result

    def test_parse_markdown_bold(self):
        result = parse_to_markdown("**bold**")
        assert "<strong>bold</strong>" in result

    def test_parse_markdown_italic(self):
        result = parse_to_markdown("*italic*")
        assert "<em>italic</em>" in result

    def test_parse_markdown_link(self):
        result = parse_to_markdown("[link](https://example.com)")
        assert '<a href="https://example.com" rel="noopener noreferrer nofollow">link</a>' in result

    def test_parse_none_becomes_empty_string(self):
        result = parse_to_markdown(None)
        assert result == ""

    def test_strips_script_tags(self):
        result = parse_to_markdown("<script>alert(1)</script>hello")
        assert "<script" not in result
        assert "hello" in result

    def test_strips_event_handler_attributes(self):
        result = parse_to_markdown('<img src=x onerror=alert(1)>')
        assert "onerror" not in result

    def test_strips_javascript_urls(self):
        result = parse_to_markdown("[x](javascript:alert(1))")
        assert "javascript:" not in result
        assert "<a" in result

    def test_keeps_safe_formatting(self):
        result = parse_to_markdown("**bold** [link](https://example.com)")
        assert "<strong>bold</strong>" in result
        assert '<a href="https://example.com"' in result

    def test_adds_rel_noopener_to_links(self):
        result = parse_to_markdown("[x](https://example.com)")
        assert 'rel="noopener noreferrer nofollow"' in result

    def test_preserves_iframe_tags(self):
        result = parse_to_markdown('<iframe src="https://example.com" width="560" height="315"></iframe>')
        assert "<iframe" in result
        assert 'src="https://example.com"' in result
        assert 'width="560"' in result
        assert 'height="315"' in result

    def test_preserves_iframe_with_style_and_loading(self):
        html = '<iframe loading="lazy" src="https://example.com" title="Embedded content" style="width:100%; height:500px;"></iframe>'
        result = parse_to_markdown(html)
        assert "<iframe" in result
        assert 'loading="lazy"' in result
        assert 'src="https://example.com"' in result
        assert 'title="Embedded content"' in result

    def test_strips_iframe_onclick(self):
        result = parse_to_markdown('<iframe src="https://example.com" onclick="alert(1)"></iframe>')
        assert "onclick" not in result
        assert 'src="https://example.com"' in result

    def test_strips_iframe_onload(self):
        result = parse_to_markdown('<iframe src="https://example.com" onload="alert(1)"></iframe>')
        assert "onload" not in result

    def test_strips_unknown_iframe_attributes(self):
        result = parse_to_markdown('<iframe src="https://example.com" data-custom="value"></iframe>')
        assert "data-custom" not in result
        assert 'src="https://example.com"' in result

    def test_preserves_responsive_embed_wrapper(self):
        html = (
            '<div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden;">'
            '<iframe src="https://www.youtube.com/embed/abc" '
            'style="position: absolute; top:0; left:0; width:100%; height:100%; border:0;" '
            'allowfullscreen></iframe></div>'
        )
        result = parse_to_markdown(html)
        assert 'style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden"' in result
        assert 'style="position:absolute;top:0;left:0;width:100%;height:100%;border:0"' in result
        assert "<div" in result
        assert "<iframe" in result

    def test_preserves_styled_standalone_iframe(self):
        html = '<iframe src="https://example.com" style="width:100%; height:500px; border:0; border-radius:4px;"></iframe>'
        result = parse_to_markdown(html)
        assert 'style="width:100%;height:500px;border:0;border-radius:4px"' in result

    def test_preserves_referrerpolicy_and_scrolling(self):
        html = '<iframe src="https://example.com" referrerpolicy="strict-origin-when-cross-origin" scrolling="no"></iframe>'
        result = parse_to_markdown(html)
        assert 'referrerpolicy="strict-origin-when-cross-origin"' in result
        assert 'scrolling="no"' in result

    def test_strips_unsafe_style_properties(self):
        result = parse_to_markdown('<div style="background: url(https://evil.com/x.png)">x</div>')
        assert "evil.com" not in result
        assert "background" not in result

    def test_strips_style_on_unallowed_tag(self):
        result = parse_to_markdown('<p style="color: red">x</p>')
        assert "style=" not in result

    def test_strips_style_url_in_iframe(self):
        result = parse_to_markdown('<iframe src="https://example.com" style="background-image: url(javascript:alert(1)); width: 100%;"></iframe>')
        assert "javascript:" not in result
        assert "url(" not in result
        assert 'style="width:100%"' in result

    def test_adds_nonce_to_iframe_when_available(self):
        token = CSP_NONCE.set("test-nonce-123")
        try:
            result = parse_to_markdown('<iframe src="https://example.com"></iframe>')
            assert 'nonce="test-nonce-123"' in result
        finally:
            CSP_NONCE.reset(token)

    def test_no_nonce_when_not_set(self):
        result = parse_to_markdown('<iframe src="https://example.com"></iframe>')
        assert "nonce=" not in result

    def test_nonce_not_added_to_non_iframe_elements(self):
        token = CSP_NONCE.set("test-nonce-456")
        try:
            result = parse_to_markdown("**bold** and <script>alert(1)</script>")
            assert "nonce=" not in result
        finally:
            CSP_NONCE.reset(token)


class TestAddFilter:
    def test_add_filter(self):
        class MockEnv:
            def __init__(self):
                self.filters = {}

        class MockTemplates:
            def __init__(self):
                self.env = MockEnv()

        templates = MockTemplates()
        add_filter(templates, "test_filter", lambda x: x.upper())
        assert "test_filter" in templates.env.filters
        assert templates.env.filters["test_filter"]("hello") == "HELLO"
