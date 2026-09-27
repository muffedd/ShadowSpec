---
name: shadowspec-behavior-gate
description: Run ShadowSpec's audited behavior-contract validator when reviewing the legacy SAVE10 fixture, a broad normalization patch, a narrow whitespace-only patch, or a behavior gate verdict.
---

# ShadowSpec behavior gate

This skill connects Bob's review workflow to the real repository validator. It does not replace the validator or make Bob's own verdict authoritative.

1. Work from this repository's root. First read `README.md` and `src/shadowspec/cli.py` to confirm the exact audited scope and the CLI command.
2. Run the actual CLI in Bob's terminal, using the project's Python interpreter. For an optional direct tool call, if the local Bob MCP server is configured and connected, call `validate_fixture` for `bad` and `narrow` first, then corroborate the results with the CLI below. If MCP is unavailable, continue with the CLI. On Windows PowerShell:
   ```powershell
   $env:PYTHONPATH = 'src'; python -m shadowspec.cli run bad --format json
   $env:PYTHONPATH = 'src'; python -m shadowspec.cli run narrow --format json
   ```
   On macOS/Linux:
   ```sh
   PYTHONPATH=src python -m shadowspec.cli run bad --format json
   PYTHONPATH=src python -m shadowspec.cli run narrow --format json
   ```
   A rejected candidate exits 2 by design; do not interpret that exit code alone as a failed tool invocation. Parse the emitted JSON.
3. Verify that bad reports `validation.verdict = rejected`, `validation.characterization_passed = false`, `validation.acceptance_passed = true`; narrow reports `accepted`, both booleans true. Quote the actual named failed checks and source/provenance hashes from the output. If command, integrity hash, or execution fails, report that rather than inventing a verdict.
4. Do not claim this validates an arbitrary user patch: the CLI accepts only the server-owned `baseline`, `bad`, and `narrow` fixtures. No merge or deployment is authorized by a fixture verdict.
5. When asked for proof, export the actual Bob task/session with commands and output to `bob_sessions/`, redacting secrets and absolute local paths per `bob_sessions/README.md`. Never handwrite a purported Bob transcript.
