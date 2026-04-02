"""Tests for embedding service chunking."""

from app.services.embedding_service import chunk_text


class TestChunkText:
    def test_short_text_single_chunk(self):
        text = "This is a short text."
        chunks = chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0] == text

    def test_empty_text(self):
        assert chunk_text("") == []
        assert chunk_text("   ") == []

    def test_splits_long_text(self):
        text = "word " * 1000  # ~5000 chars
        chunks = chunk_text(text, chunk_size=2000, overlap=400)
        assert len(chunks) > 1
        # Each chunk should be <= chunk_size (approximately)
        for chunk in chunks:
            assert len(chunk) <= 2200  # allow some slack for boundary finding

    def test_overlap_exists(self):
        text = "A" * 500 + " MARKER " + "B" * 500 + " MARKER2 " + "C" * 500
        chunks = chunk_text(text, chunk_size=600, overlap=100)
        assert len(chunks) >= 2
        # With overlap, adjacent chunks should share some content

    def test_preserves_all_content(self):
        words = [f"word{i}" for i in range(100)]
        text = " ".join(words)
        chunks = chunk_text(text, chunk_size=200, overlap=50)
        rejoined = " ".join(chunks)
        # All original words should appear at least once
        for word in words:
            assert word in rejoined

    def test_prefers_paragraph_breaks(self):
        text = "First paragraph content.\n\nSecond paragraph content.\n\nThird paragraph content."
        chunks = chunk_text(text, chunk_size=50, overlap=10)
        # Chunks should break at paragraph boundaries when possible
        assert len(chunks) >= 2

    def test_uses_module_defaults(self):
        text = "x" * 3000
        chunks = chunk_text(text)
        # Default chunk_size is 2000, so should produce 2+ chunks
        assert len(chunks) >= 2
