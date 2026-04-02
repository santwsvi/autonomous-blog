"""Tests for publisher MDX sanitization and slug generation."""

from app.agents.nodes.publisher import _sanitize_mdx
from app.utils import generate_slug


class TestSanitizeMdx:
    def test_strips_script_tags(self):
        content = "# Hello\n<script>alert('xss')</script>\nWorld"
        assert "<script>" not in _sanitize_mdx(content)
        assert "World" in _sanitize_mdx(content)

    def test_strips_iframe(self):
        content = '<iframe src="http://evil.com"></iframe>Content'
        assert "<iframe" not in _sanitize_mdx(content)
        assert "Content" in _sanitize_mdx(content)

    def test_strips_event_handlers(self):
        content = '<img src="x" onerror="alert(1)">'
        sanitized = _sanitize_mdx(content)
        assert "onerror" not in sanitized

    def test_strips_javascript_urls(self):
        content = '<a href="javascript:alert(1)">click</a>'
        sanitized = _sanitize_mdx(content)
        assert "javascript:" not in sanitized

    def test_strips_frontmatter(self):
        content = "---\ntitle: Test\ndate: 2024-01-01\n---\n\n# Real Content"
        assert "# Real Content" in _sanitize_mdx(content)
        assert "title: Test" not in _sanitize_mdx(content)

    def test_strips_markdown_wrapper(self):
        content = "```markdown\n# Hello World\n\nThis is content.\n```"
        sanitized = _sanitize_mdx(content)
        assert "```markdown" not in sanitized
        assert "# Hello World" in sanitized

    def test_strips_mdx_wrapper(self):
        content = "```mdx\n# Hello World\n\nThis is content.\n```"
        sanitized = _sanitize_mdx(content)
        assert "```mdx" not in sanitized
        assert "# Hello World" in sanitized

    def test_preserves_code_blocks(self):
        content = "# Post\n\n```python\nprint('hello')\n```\n\nMore text"
        sanitized = _sanitize_mdx(content)
        assert "```python" in sanitized
        assert "print('hello')" in sanitized

    def test_preserves_normal_markdown(self):
        content = "# Title\n\n**Bold** and *italic*.\n\n- List item"
        assert _sanitize_mdx(content) == content


class TestGenerateSlug:
    def test_basic_slug(self):
        assert generate_slug("Hello World") == "hello-world"

    def test_accented_characters(self):
        assert generate_slug("Programação em Python") == "programacao-em-python"

    def test_special_characters(self):
        assert generate_slug("What's Next? (2024)") == "whats-next-2024"

    def test_max_length(self):
        long_title = "a " * 100
        assert len(generate_slug(long_title)) <= 80

    def test_strips_leading_trailing_hyphens(self):
        assert generate_slug("  --hello--  ") == "hello"
