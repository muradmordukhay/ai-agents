import os


def get_api_key() -> str:
    """Validate and return the Anthropic API key from the environment."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. "
            "Export it in ~/.zshrc.local: export ANTHROPIC_API_KEY='sk-ant-...'"
        )
    return key


MODEL = "claude-sonnet-4-20250514"
MAX_TURNS = 10
