# Contributing to ai-agents

Thanks for your interest in contributing! This guide covers everything you need to get started.

## Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** package manager
- **[Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)** installed
- **`ANTHROPIC_API_KEY`** environment variable set

## Development Setup

```bash
git clone https://github.com/muradmordukhay/ai-agents.git
cd ai-agents
uv sync
uv run pre-commit install
```

Verify everything works:

```bash
uv run pytest -v
uv run ruff check .
uv run ruff format --check .
```

## Making Changes

### Branch Strategy

- Create a feature branch from `main` (direct commits to `main` are blocked)
- Rebase on `main` before merging — no merge commits

```bash
git checkout -b feat/my-feature
# ... make changes ...
git rebase main
```

### Code Style

- **Formatter:** ruff (`uv run ruff format .`)
- **Linter:** ruff (`uv run ruff check .`)
- **Line length:** 100 characters
- **Python:** 3.13+ features are fine

Pre-commit hooks run ruff automatically on every commit.

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(agents): add new test-writer agent
fix(cli): handle missing target gracefully
docs(readme): update architecture section
test(agents): add edge case for empty input
refactor(base): simplify message extraction
chore(deps): update claude-agent-sdk to 0.2.0
```

Format: `type(scope): description`

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

### Running Tests

```bash
uv run pytest -v           # all tests
uv run pytest tests/test_code_reviewer.py  # specific file
```

### Adding a New Agent

See the [Adding a New Agent](README.md#adding-a-new-agent) section in the README for the step-by-step pattern.

## Pull Request Process

1. Create your feature branch and make your changes
2. Ensure all checks pass:
   - `uv run pytest -v`
   - `uv run ruff check .`
   - `uv run ruff format --check .`
3. Push your branch and open a PR
4. Fill out the PR template checklist
5. Wait for CI to pass and review

## Questions?

Open an [issue](https://github.com/muradmordukhay/ai-agents/issues) if you have questions or run into problems.
