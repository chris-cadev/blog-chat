import pytest
import tempfile
from pathlib import Path
from blog_chat.features.posts.parser import parse_markdown_file


class TestParseMarkdownFile:
    def test_parse_file_with_frontmatter(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("---\ntitle: Test Post\nslug: test-post\ntags: [python, test]\ncreated: 2024-01-01\n---\n\nThis is the content.")
            f.flush()
            try:
                result = parse_markdown_file(Path(f.name))
                assert result["title"] == "Test Post"
                assert result["slug"] == "test-post"
                assert result["tags"] == ["python", "test"]
                assert str(result["created"]) == "2024-01-01"
                assert result["content"] == "This is the content."
            finally:
                Path(f.name).unlink()

    def test_parse_file_without_frontmatter(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Just some content without frontmatter.")
            f.flush()
            try:
                result = parse_markdown_file(Path(f.name))
                assert result["title"] == Path(f.name).stem
                assert result["slug"] == Path(f.name).stem
                assert result["tags"] == []
                assert result["content"] == "Just some content without frontmatter."
            finally:
                Path(f.name).unlink()

    def test_parse_file_uses_filename_stem_as_default(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("---\ntitle: My Title\n---\nContent here")
            f.flush()
            try:
                result = parse_markdown_file(Path(f.name))
                assert result["title"] == "My Title"
                assert result["slug"] == Path(f.name).stem
            finally:
                Path(f.name).unlink()

    def test_parse_file_with_empty_title(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("---\ntitle: \n---\n\nContent")
            f.flush()
            try:
                result = parse_markdown_file(Path(f.name))
                assert result["content"] == "Content"
            finally:
                Path(f.name).unlink()
