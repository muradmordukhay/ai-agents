import os

import pytest

from ai_agents.agents.code_reviewer import CodeReviewResult, _parse_result, _sanitize, review


class TestParseResultValidJSON:
    def test_valid_clean_json(self):
        raw = '{"findings": [], "summary": "Clean code", "files_reviewed": 2}'
        result = _parse_result(raw)
        assert isinstance(result, CodeReviewResult)
        assert result.summary == "Clean code"
        assert result.files_reviewed == 2
        assert result.findings == []

    def test_json_with_findings(self):
        raw = """{
            "findings": [
                {
                    "file": "main.py",
                    "line": 10,
                    "severity": "warning",
                    "category": "style",
                    "message": "Unused import",
                    "suggestion": "Remove it"
                }
            ],
            "summary": "One issue found",
            "files_reviewed": 1
        }"""
        result = _parse_result(raw)
        assert result is not None
        assert len(result.findings) == 1
        assert result.findings[0].file == "main.py"
        assert result.findings[0].line == 10
        assert result.findings[0].severity == "warning"
        assert result.findings[0].category == "style"
        assert result.findings[0].suggestion == "Remove it"

    def test_finding_without_optional_fields(self):
        raw = """{
            "findings": [
                {
                    "file": "app.py",
                    "severity": "info",
                    "category": "performance",
                    "message": "Consider caching"
                }
            ],
            "summary": "Minor suggestion",
            "files_reviewed": 1
        }"""
        result = _parse_result(raw)
        assert result is not None
        assert result.findings[0].line is None
        assert result.findings[0].suggestion is None


class TestParseResultMarkdownFences:
    def test_fenced_with_language_tag(self):
        raw = '```json\n{"findings": [], "summary": "OK", "files_reviewed": 1}\n```'
        result = _parse_result(raw)
        assert result is not None
        assert result.summary == "OK"

    def test_fenced_without_language_tag(self):
        raw = '```\n{"findings": [], "summary": "OK", "files_reviewed": 1}\n```'
        result = _parse_result(raw)
        assert result is not None
        assert result.summary == "OK"


class TestParseResultEmbeddedJSON:
    def test_json_embedded_in_text(self):
        raw = 'Here is the result:\n{"findings": [], "summary": "Good", "files_reviewed": 3}\nDone.'
        result = _parse_result(raw)
        assert result is not None
        assert result.summary == "Good"
        assert result.files_reviewed == 3


class TestParseResultInvalid:
    def test_no_json_returns_none(self):
        assert _parse_result("No JSON here") is None

    def test_empty_string_returns_none(self):
        assert _parse_result("") is None

    def test_whitespace_only_returns_none(self):
        assert _parse_result("   \n  ") is None

    def test_invalid_json_returns_none(self):
        assert _parse_result("{invalid json content}") is None

    def test_missing_required_field_returns_none(self):
        # Missing files_reviewed — Pydantic validation should catch this
        raw = '{"findings": [], "summary": "OK"}'
        assert _parse_result(raw) is None


class TestParseResultRobustness:
    def test_json_with_trailing_text(self):
        """raw_decode should stop at the end of the JSON object."""
        raw = '{"findings": [], "summary": "OK", "files_reviewed": 1} extra text here'
        result = _parse_result(raw)
        assert result is not None
        assert result.summary == "OK"

    def test_multiple_json_objects_takes_first(self):
        """Should parse the first valid JSON object, not span across both."""
        raw = '{"findings": [], "summary": "First", "files_reviewed": 1} {"other": true}'
        result = _parse_result(raw)
        assert result is not None
        assert result.summary == "First"


class TestSanitize:
    def test_strips_ansi_escape(self):
        assert _sanitize("\x1b[31mred\x1b[0m") == "red"

    def test_strips_control_chars(self):
        assert _sanitize("hello\x00world") == "helloworld"

    def test_preserves_normal_text(self):
        assert _sanitize("normal text\nwith newlines") == "normal text\nwith newlines"

    def test_preserves_tabs(self):
        assert _sanitize("col1\tcol2") == "col1\tcol2"

    def test_preserves_unicode(self):
        result = _sanitize("emoji: ❌ ⚠️")
        assert "❌" in result
        assert "⚠" in result


class TestReviewValidation:
    @pytest.mark.asyncio
    async def test_rejects_nonexistent_path(self):
        with pytest.raises(FileNotFoundError):
            await review("/nonexistent/path/to/nowhere")

    @pytest.mark.asyncio
    async def test_rejects_fifo(self, tmp_path):
        """FIFO should be rejected — only files and directories allowed."""
        fifo = tmp_path / "test_fifo"
        try:
            os.mkfifo(fifo)
        except OSError:
            pytest.skip("Cannot create FIFO on this platform")
        with pytest.raises(ValueError, match="must be a file or directory"):
            await review(str(fifo))
