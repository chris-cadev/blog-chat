import pytest
from blog_chat.core.filters import parse_to_markdown, add_filter


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
        assert '<a href="https://example.com">link</a>' in result

    def test_parse_none_becomes_empty_string(self):
        result = parse_to_markdown(None)
        assert result == ""

    def test_parse_none_becomes_empty_string(self):
        result = parse_to_markdown(None)
        assert result == ""


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
