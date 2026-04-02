"""Tests for editor node parsers."""

from app.agents.nodes.editor import _parse_approved, _parse_feedback, _parse_scores


class TestParseScores:
    def test_parses_all_dimensions(self):
        content = """SCORES:
readability: 0.90
coherence: 0.85
depth: 0.80
originality: 0.75
factual_accuracy: 0.88
overall: 0.84

APPROVED: true"""
        scores = _parse_scores(content)
        assert scores.readability == 0.90
        assert scores.coherence == 0.85
        assert scores.depth == 0.80
        assert scores.originality == 0.75
        assert scores.factual_accuracy == 0.88
        assert scores.overall == 0.84

    def test_clamps_values_to_0_1(self):
        content = "readability: 1.5\ncoherence: -0.3\noverall: 0.50"
        scores = _parse_scores(content)
        assert scores.readability == 1.0
        assert scores.coherence == 0.0
        assert scores.overall == 0.50

    def test_handles_missing_fields(self):
        content = "readability: 0.90\noverall: 0.85"
        scores = _parse_scores(content)
        assert scores.readability == 0.90
        assert scores.coherence == 0.0  # default
        assert scores.overall == 0.85

    def test_handles_garbage_input(self):
        scores = _parse_scores("this is not a valid output")
        assert scores.overall == 0.0


class TestParseApproved:
    def test_approved_true(self):
        assert _parse_approved("APPROVED: true") is True

    def test_approved_false(self):
        assert _parse_approved("APPROVED: false") is False

    def test_case_insensitive(self):
        assert _parse_approved("approved: True") is True

    def test_missing_returns_false(self):
        assert _parse_approved("no approved field here") is False


class TestParseFeedback:
    def test_extracts_feedback(self):
        content = """SCORES:
readability: 0.90

APPROVED: false

FEEDBACK:
The article needs more code examples.
Also improve the conclusion."""
        feedback = _parse_feedback(content)
        assert "code examples" in feedback
        assert "conclusion" in feedback

    def test_returns_full_content_if_no_marker(self):
        content = "Just some general feedback without a marker"
        assert _parse_feedback(content) == content
