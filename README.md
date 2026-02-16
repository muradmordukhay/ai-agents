# ai-agents

Personal AI agents powered by [Claude Agent SDK](https://docs.anthropic.com/en/docs/claude-code/sdk). Each agent is a focused tool that automates a specific development task using Claude's agentic capabilities.

## Prerequisites

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/)** package manager
- **[Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code)** installed and on your PATH
- **`ANTHROPIC_API_KEY`** environment variable set

## Quick Start

```bash
# Clone and install
git clone <repo-url> && cd ai-agents
uv sync

# Set your API key (add to ~/.zshrc.local or equivalent)
export ANTHROPIC_API_KEY="sk-ant-..."

# Run the code review agent
uv run agent code-review src/ai_agents/config.py
```

## Usage

### Code Review Agent

Review a single file:

```bash
uv run agent code-review src/ai_agents/config.py
```

Review an entire directory:

```bash
uv run agent code-review src/ai_agents/
```

Focus on a specific area:

```bash
uv run agent code-review src/ --focus bugs
uv run agent code-review src/ --focus style
uv run agent code-review src/ --focus security
uv run agent code-review src/ --focus all      # default
```

Output includes structured findings with severity levels, file locations, and fix suggestions. Agent metadata (cost, duration, turns) is printed to stderr.

## Architecture

### How Agents Work

Each agent follows a consistent pattern:

1. **AGENT_CONFIG** dict defines the agent's name, description, and allowed tools
2. **Pydantic models** define the structured output schema
3. **Async entry function** builds a prompt, calls `run_agent()`, parses the response
4. **CLI registration** in `cli.py` exposes the agent as a subcommand

All agents call `run_agent()` from `base.py` — never `query()` directly. The base runner handles API key validation, SDK configuration, message iteration, and metadata extraction.

### AgentResult

`run_agent()` returns an `AgentResult` dataclass:

```python
@dataclass
class AgentResult:
    text: str                       # The agent's text response
    cost_usd: float | None          # API cost in USD
    duration_ms: int | None         # Total duration in milliseconds
    num_turns: int | None           # Number of agentic turns taken
```

### Base Runner Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | `str` | required | The task for the agent |
| `allowed_tools` | `list[str]` | `None` | Tool allowlist (e.g., `["Read", "Glob", "Grep"]`) |
| `max_turns` | `int` | `10` | Maximum agentic turns |
| `model` | `str` | `claude-sonnet-4-20250514` | Claude model to use |
| `system_prompt` | `str` | `None` | Custom system prompt |
| `cwd` | `str \| Path` | `None` | Working directory for the agent |
| `permission_mode` | `str` | `"default"` | SDK permission mode (see Security) |

### Tool Sandboxing

Agents are restricted to only the tools listed in their `allowed_tools`. The code reviewer uses `["Read", "Glob", "Grep"]` — read-only access with no ability to write, execute commands, or access the network.

## Project Structure

```
ai-agents/
  src/ai_agents/
    __init__.py
    config.py              # API key validation, MODEL/MAX_TURNS constants
    cli.py                 # argparse entry point with subcommand dispatch
    agents/
      __init__.py
      base.py              # run_agent() — shared agent runner + AgentResult
      code_reviewer.py     # Code review agent with structured JSON output
  tests/
    __init__.py
    test_config.py         # API key validation tests
    test_base.py           # AgentResult dataclass tests
    test_code_reviewer.py  # JSON parsing tests for _parse_result()
  .github/workflows/
    ci.yml                 # Lint + format + test on PR/push
  CLAUDE.md                # AI assistant development conventions
  pyproject.toml           # Project metadata, dependencies, tool config
```

## Adding a New Agent

1. **Create the agent module** at `src/ai_agents/agents/my_agent.py`:

```python
from pydantic import BaseModel
from ai_agents.agents.base import AgentResult, run_agent

AGENT_CONFIG = {
    "name": "my-agent",
    "description": "What this agent does",
    "allowed_tools": ["Read", "Glob", "Grep"],
}

class MyResult(BaseModel):
    # Define your structured output fields
    summary: str

async def run(target: str) -> None:
    agent_result: AgentResult = await run_agent(
        prompt=f"Analyze: {target}",
        allowed_tools=AGENT_CONFIG["allowed_tools"],
        system_prompt="You are a helpful assistant.",
        permission_mode="bypassPermissions",  # only if tools are read-only
    )
    # Parse agent_result.text into your Pydantic model
    print(agent_result.text)
```

2. **Register a subcommand** in `cli.py`:

```python
my_parser = subparsers.add_parser("my-agent", help="Description")
my_parser.add_argument("target", help="File or directory")

# In the dispatch block:
if args.command == "my-agent":
    from ai_agents.agents.my_agent import run
    asyncio.run(run(target=args.target))
```

3. **Run it:**

```bash
uv run agent my-agent path/to/target
```

## Security

The framework applies defense-in-depth:

- **Safe permission default**: `run_agent()` defaults to `permission_mode="default"`, which requires approval for writes. Agents that only use read-only tools (like the code reviewer) can explicitly opt into `"bypassPermissions"` at the call site.
- **Tool allowlisting**: Each agent declares its `allowed_tools`. The code reviewer is restricted to `["Read", "Glob", "Grep"]` — no writes, no shell, no network.
- **Input sanitization**: File paths are escaped with `json.dumps()` before prompt interpolation to prevent prompt injection. Paths are validated to be regular files or directories.
- **Output sanitization**: All agent-provided text is stripped of ANSI escape sequences and control characters before printing, preventing terminal injection.
- **Secret handling**: API keys are read from environment variables only, never hardcoded. Pre-commit hooks (`detect-private-key`, `gitleaks`) block accidental commits of secrets.

## Known Limitations

- **Nested Claude Code sessions**: The SDK spawns Claude Code as a subprocess. Running `uv run agent` from inside an existing Claude Code session will fail. Use a regular terminal instead.
- **One-shot queries**: Each invocation is a single query. There is no multi-turn conversation state between runs.
- **Cost varies**: Agent cost depends on the complexity and size of the target. Review a single file and it's a few cents; review a large directory and it could be more.

## Development

```bash
# Run tests
uv run pytest -v

# Lint
uv run ruff check .

# Format
uv run ruff format .

# All pre-commit hooks
uv run pre-commit run --all-files
```

After cloning, install pre-commit hooks:

```bash
uv run pre-commit install
```
