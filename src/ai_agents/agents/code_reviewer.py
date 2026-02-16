from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import BaseModel

from ai_agents.agents.base import AgentResult, run_agent

AGENT_CONFIG = {
    "name": "code-reviewer",
    "description": (
        "Reviews code for bugs, style issues, security vulnerabilities, and improvements"
    ),
    "allowed_tools": ["Read", "Glob", "Grep"],  # read-only — no writes
}

FOCUS_INSTRUCTIONS = {
    "bugs": "Focus on logical errors, edge cases, null/undefined handling, and potential crashes.",
    "style": "Focus on code style, naming, readability, and adherence to Python best practices.",
    "security": (
        "Focus on security vulnerabilities: injection, secrets, input validation, auth issues."
    ),
    "all": "Review for bugs, style, security, and performance issues.",
}


class Finding(BaseModel):
    file: str
    line: int | None = None
    severity: str  # "error" | "warning" | "info"
    category: str  # "bug" | "style" | "security" | "performance"
    message: str
    suggestion: str | None = None


class CodeReviewResult(BaseModel):
    findings: list[Finding]
    summary: str
    files_reviewed: int


def _build_prompt(target_path: Path, focus: str) -> str:
    return f"""Review the code at: {target_path}

{FOCUS_INSTRUCTIONS[focus]}

Read the files, analyze them, and respond with ONLY a JSON object matching this schema:
{{
  "findings": [
    {{
      "file": "relative/path.py",
      "line": 42,
      "severity": "error|warning|info",
      "category": "bug|style|security|performance",
      "message": "Description of the issue",
      "suggestion": "How to fix it"
    }}
  ],
  "summary": "Brief overall assessment",
  "files_reviewed": 3
}}

If there are no issues, return an empty findings array with a positive summary.
Respond ONLY with the JSON — no markdown fences, no explanation."""


def _parse_result(raw: str) -> CodeReviewResult | None:
    """Parse the agent's JSON response into a validated Pydantic model."""
    text = raw.strip()

    # Handle markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

    # Find the JSON object boundaries
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        return None

    try:
        data = json.loads(text[start:end])
        return CodeReviewResult.model_validate(data)
    except (json.JSONDecodeError, ValueError):
        return None


def _print_findings(target: Path, result: CodeReviewResult) -> None:
    """Pretty-print code review findings."""
    print(f"\n{'=' * 60}")
    print(f"Code Review: {target}")
    print(f"Files reviewed: {result.files_reviewed}")
    print(f"Findings: {len(result.findings)}")
    print(f"{'=' * 60}\n")

    severity_icons = {"error": "❌", "warning": "⚠️ ", "info": "ℹ️ "}  # noqa: RUF001

    for finding in result.findings:
        icon = severity_icons.get(finding.severity, "•")
        location = finding.file
        if finding.line:
            location += f":{finding.line}"
        print(f"{icon} [{finding.severity.upper()}] {location}")
        print(f"  {finding.message}")
        if finding.suggestion:
            print(f"  → {finding.suggestion}")
        print()

    print(f"Summary: {result.summary}")


def _print_agent_metadata(agent_result: AgentResult) -> None:
    """Print agent run metadata (cost, duration, turns) to stderr."""
    parts = []
    if agent_result.cost_usd is not None:
        parts.append(f"${agent_result.cost_usd:.4f}")
    if agent_result.duration_ms is not None:
        seconds = agent_result.duration_ms / 1000
        parts.append(f"{seconds:.1f}s")
    if agent_result.num_turns is not None:
        parts.append(f"{agent_result.num_turns} turns")
    if parts:
        print(f"  [meta] {' | '.join(parts)}", file=sys.stderr)


async def review(target: str, focus: str = "all") -> None:
    """Review code at the given path and print structured findings."""
    target_path = Path(target).resolve()
    if not target_path.exists():
        raise FileNotFoundError(f"Target not found: {target}")

    prompt = _build_prompt(target_path, focus)

    agent_result: AgentResult = await run_agent(
        prompt=prompt,
        allowed_tools=AGENT_CONFIG["allowed_tools"],
        system_prompt="You are a senior code reviewer. Be thorough but concise.",
    )

    _print_agent_metadata(agent_result)

    result = _parse_result(agent_result.text)
    if result is None:
        # Structured parsing failed — print raw output
        print(agent_result.text)
        return

    _print_findings(target_path, result)
