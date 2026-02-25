import pytest
from blog_chat.core.html import minify_html_func


class TestMinifyHtml:
    def test_minify_removes_whitespace(self):
        html = "<html>  <body>  <p>  Hello  </p>  </body>  </html>"
        result = minify_html_func(html)
        assert "  " not in result
        assert "Hello" in result

    def test_minify_removes_comments(self):
        html = "<html><body><!-- comment --><p>Hello</p></body></html>"
        result = minify_html_func(html)
        assert "comment" not in result
        assert "Hello" in result

    def test_minify_preserves_opening_tags(self):
        html = "<html><body><p>Hello</p></body></html>"
        result = minify_html_func(html)
        assert "<html>" in result
        assert "<body>" in result

    def test_minify_empty_string(self):
        result = minify_html_func("")
        assert result == ""
