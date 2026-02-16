import argparse
import asyncio
import sys


def main() -> None:
    """CLI entry point for running AI agents."""
    parser = argparse.ArgumentParser(
        prog="agent",
        description="Run AI agents powered by Claude Agent SDK",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # code-review subcommand
    review_parser = subparsers.add_parser(
        "code-review",
        help="Review code for bugs, style issues, and improvements",
    )
    review_parser.add_argument("target", help="File or directory to review")
    review_parser.add_argument(
        "--focus",
        choices=["bugs", "style", "security", "all"],
        default="all",
        help="Review focus area (default: all)",
    )

    args = parser.parse_args()

    if args.command == "code-review":
        from ai_agents.agents.code_reviewer import review

        try:
            asyncio.run(review(target=args.target, focus=args.focus))
        except RuntimeError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nInterrupted.", file=sys.stderr)
            sys.exit(130)
    else:
        parser.print_help()
        sys.exit(1)
