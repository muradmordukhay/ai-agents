import pytest

from ai_agents.config import get_api_key


def test_get_api_key_raises_when_unset(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY is not set"):
        get_api_key()


def test_get_api_key_raises_when_empty(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY is not set"):
        get_api_key()


def test_get_api_key_raises_when_whitespace_only(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "   ")
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY is not set"):
        get_api_key()


def test_get_api_key_returns_value(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
    assert get_api_key() == "sk-ant-test-key"


def test_get_api_key_strips_whitespace(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "  sk-ant-test-key  ")
    assert get_api_key() == "sk-ant-test-key"
