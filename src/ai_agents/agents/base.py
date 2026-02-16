from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ResultMessage, query

from ai_agents.config import MAX_TURNS, MODEL, get_api_key


@dataclass
class AgentResult:
    """Result returned by run_agent() containing the response text and metadata."""

    text: str
    cost_usd: float | None = None
    duration_ms: int | None = None
    num_turns: int | None = None


async def run_agent(
    prompt: str,
    allowed_tools: list[str] | None = None,
    max_turns: int = MAX_TURNS,
    model: str = MODEL,
    system_prompt: str | None = None,
    cwd: str | Path | None = None,
) -> AgentResult:
    """Execute an agent query and return the result with metadata.

    All agents should call this function instead of using query() directly.
    It handles API key validation, error handling, message extraction, and
    cost tracking.
    """
    get_api_key()  # validate early

    options = ClaudeAgentOptions(
        model=model,
        max_turns=max_turns,
        permission_mode="bypassPermissions",
    )
    if allowed_tools:
        options.allowed_tools = allowed_tools
    if system_prompt:
        options.system_prompt = system_prompt
    if cwd:
        options.cwd = cwd

    result_parts: list[str] = []
    cost_usd: float | None = None
    duration_ms: int | None = None
    num_turns: int | None = None

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text"):
                        result_parts.append(block.text)
                    elif hasattr(block, "name"):
                        print(f"  [tool] {block.name}", file=sys.stderr)
            elif isinstance(message, ResultMessage):
                cost_usd = message.total_cost_usd
                duration_ms = message.duration_ms
                num_turns = message.num_turns
                print(f"  [done] {message.subtype}", file=sys.stderr)
    except Exception as exc:
        print(f"Agent error: {exc}", file=sys.stderr)
        raise

    return AgentResult(
        text="\n".join(result_parts),
        cost_usd=cost_usd,
        duration_ms=duration_ms,
        num_turns=num_turns,
    )
