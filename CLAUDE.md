# ai-agents

> Profile: personal | Language: python

## Project Overview

Personal AI agents powered by Claude Agent SDK. Each agent is a focused tool that automates a specific development task (code review, test generation, documentation, etc.) using Claude's agentic capabilities.

## Development

- **Run tests:** `uv run pytest`
- **Lint:** `uv run ruff check .`
- **Format:** `uv run ruff format .`

## Conventions

- Follow global engineering standards (see ~/.claude/CLAUDE.md)
- Use conventional commits: `feat|fix|docs|refactor|test|chore(scope): description`
- All PRs require CI to pass before merge
- Handle errors explicitly — no silent catches
- Never commit secrets, tokens, or credentials

## Python Specifics

- Package manager: **uv** (never use pip directly)
- Formatter: `uv run ruff format`
- Linter: `uv run ruff check`
- Virtual env: managed by uv (`.venv/` in project root)
- Minimum Python version: see `pyproject.toml`
- Add dependencies: `uv add <package>`
- Run scripts: `uv run <script>`

## Agent Development

- All agents live in `src/ai_agents/agents/`
- Each agent module exports an async function and an `AGENT_CONFIG` dict
- Use `run_agent()` from `base.py` to execute — never call `query()` directly
- Define Pydantic models for structured output in each agent module
- Register new agents in `cli.py` by adding a subcommand
- Run agents: `uv run agent <agent-name> [args]`
- `ANTHROPIC_API_KEY` must be set in the environment
