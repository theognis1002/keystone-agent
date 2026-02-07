import pytest

from keystone.config import MAX_OUTPUT
from keystone.tools._helpers import _truncate, _ok, _err, _log_tool


class TestTruncate:
    def test_short_text_unchanged(self):
        assert _truncate("hello") == "hello"

    def test_exact_max_output_unchanged(self):
        text = "x" * MAX_OUTPUT
        assert _truncate(text) == text

    def test_exceeds_max_output_truncated(self):
        text = "x" * (MAX_OUTPUT + 500)
        result = _truncate(text)
        assert result.startswith("x" * MAX_OUTPUT)
        assert "truncated" in result
        assert str(len(text)) in result


class TestOk:
    def test_returns_correct_shape(self):
        result = _ok("hello")
        assert result == {"content": [{"type": "text", "text": "hello"}]}
        assert "is_error" not in result

    def test_truncates_long_text(self):
        long_text = "a" * (MAX_OUTPUT + 100)
        result = _ok(long_text)
        assert "truncated" in result["content"][0]["text"]


class TestErr:
    def test_returns_correct_shape(self):
        result = _err("boom")
        assert result == {
            "content": [{"type": "text", "text": "boom"}],
            "is_error": True,
        }

    def test_truncates_long_text(self):
        long_text = "b" * (MAX_OUTPUT + 100)
        result = _err(long_text)
        assert result["is_error"] is True
        assert "truncated" in result["content"][0]["text"]


class TestLogTool:
    def test_prints_expected_format(self, capsys):
        _log_tool("my_tool", ["line1", "line2"])
        captured = capsys.readouterr().out
        assert "my_tool" in captured
        assert "line1" in captured
        assert "line2" in captured
        assert "┌─" in captured
        assert "└─" in captured

    def test_single_line(self, capsys):
        _log_tool("t", ["only"])
        captured = capsys.readouterr().out
        assert "│ only" in captured
