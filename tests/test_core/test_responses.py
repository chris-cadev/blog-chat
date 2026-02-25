import pytest
import tempfile
import os
from blog_chat.core.responses import MinifiedTemplate, create_templates


class TestMinifiedTemplate:
    def test_render_minifies_html(self):
        template = MinifiedTemplate("<html>  <body>  <p>  Hello  </p>  </body>  </html>")
        result = template.render()
        assert "  " not in result
        assert "Hello" in result


class TestCreateTemplates:
    def test_create_templates_with_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            templates = create_templates(tmpdir)
            assert templates is not None
            assert templates.env.template_class == MinifiedTemplate

    def test_create_templates_adds_minify_filter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            templates = create_templates(tmpdir)
            assert "minify" in templates.env.filters
