"""Optional, local-only IBM Bob MCP adapter for audited ShadowSpec fixtures.

Install the MCP Python SDK separately; the zero-key demo does not need it.
The JSON-RPC protocol uses stdout. Diagnostics belong on stderr only.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).resolve().parents[2]
mcp = FastMCP("ShadowSpec audited behavior gate")


@mcp.tool()
def validate_fixture(candidate: str) -> dict:
    """Run the real ShadowSpec CLI on one audited fixture: bad, narrow, or baseline.

    This does not evaluate arbitrary patches. A rejected verdict is a valid
    result, not an MCP error. The full evidence remains in the CLI's JSON.
    """
    if candidate not in {"baseline", "bad", "narrow"}:
        return {"error": "candidate must be baseline, bad, or narrow"}

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "shadowspec.cli", "run", candidate, "--format", "json"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=12,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"candidate": candidate, "error": "validator timed out"}

    if result.returncode not in (0, 2):
        return {"candidate": candidate, "error": "validator failed", "exit_code": result.returncode,
                "stderr": result.stderr[-1000:]}
    try:
        evidence = json.loads(result.stdout)
        validation = evidence["validation"]
    except (ValueError, KeyError, TypeError):
        return {"candidate": candidate, "error": "validator returned invalid evidence",
                "exit_code": result.returncode}
    verdict = validation.get("verdict")
    if verdict not in ("accepted", "rejected") or (result.returncode == 0) != (verdict == "accepted"):
        return {"candidate": candidate, "error": "validator exit code and verdict disagree"}
    return {
        "candidate": candidate,
        "verdict": verdict,
        "characterization_passed": validation.get("characterization_passed"),
        "acceptance_passed": validation.get("acceptance_passed"),
        "failed_checks": validation.get("failed_checks"),
        "provenance": {key: validation.get(key) for key in ("source_sha256", "baseline_sha256", "validator_sha256", "runner_sha256")},
        "scope": "Only the three bundled, integrity-checked fixtures; not arbitrary patches",
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
