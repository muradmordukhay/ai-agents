import sys

from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ResultMessage, query

from ai_agents.config import MAX_TURNS, MODEL, get_api_key


async def run_agent(
    prompt: str,
    allowed_tools: list[str] | None = None,
    max_turns: int = MAX_TURNS,
    model: str = MODEL,
    system_prompt: str | None = None,
) -> str:
    """Execute an agent query and return the final text response.

    All agents should call this function instead of using query() directly.
    It handles API key validation, error handling, and message extraction.
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

    result_parts: list[str] = []

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if hasattr(block, "text"):
                        result_parts.append(block.text)
                    elif hasattr(block, "name"):
                        print(f"  [tool] {block.name}", file=sys.stderr)
            elif isinstance(message, ResultMessage):
                print(f"  [done] {message.subtype}", file=sys.stderr)
    except Exception as exc:
        print(f"Agent error: {exc}", file=sys.stderr)
        raise

    return "\n".join(result_parts)
