"""ShadowSpec command-line entry point."""

from __future__ import annotations

import argparse
import sys

from shadowspec.service import run_demo


def main(argv=None):
    parser = argparse.ArgumentParser(prog="shadowspec")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="evaluate an audited candidate")
    run_parser.add_argument("candidate", choices=("baseline", "bad", "narrow"))
    run_parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args(argv)
    result = run_demo(args.candidate)
    print(result.evidence_json if args.format == "json" else result.evidence_markdown)
    return 0 if result.validation.verdict == "accepted" else 2


if __name__ == "__main__":
    sys.exit(main())
