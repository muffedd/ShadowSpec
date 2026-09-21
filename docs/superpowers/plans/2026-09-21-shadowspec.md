# ShadowSpec Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a zero-key evidence workbench that rejects an over-broad legacy patch, accepts a narrow patch, and exports reviewer-ready proof.

**Architecture:** A pure-Python core analyzes an audited bundled repository and validates prepared candidate variants in isolated temporary workspaces. A Streamlit UI renders the same deterministic service outputs used by tests and evidence export.

**Tech Stack:** Python 3.12, AST, pytest, subprocess, SQLite, Streamlit, Markdown/JSON.

**Spec:** `docs/superpowers/specs/2026-09-21-shadowspec-design.md`

## Global Constraints

- Hosted execution is bundled-fixture-only.
- No API key is required.
- Public GitHub URLs are optional and analysis-only.
- Never call the fixture-safe subprocess mechanism an OS security sandbox.
- Every verdict is scoped to named fixtures and observed behavior.
- Bob artifacts are real configuration/documentation, not a claim of unavailable live inference.

## Review Focus

- Path traversal must be rejected before file access.
- Invalid or private-network URLs must be rejected before fetch.
- Timeouts and oversized output must produce clear bounded failures.
- Lowercase discount codes must remain invalid after the approved change.
- Evidence must never include environment variables or absolute host paths.

---

### Task 1: Fixture and deterministic observations

**Files:** `fixtures/legacy_orders/*`, `tests/test_fixture_contract.py`

**Interfaces:** Produces `process_order(order, db_path) -> dict` and named baseline/acceptance behaviors.

- [ ] Write tests for pricing, case sensitivity, whitespace request, and SQLite audit effects.
- [ ] Run them and verify the approved whitespace case fails while existing behavior is understood.
- [ ] Add baseline, bad, and narrow fixture variants.
- [ ] Verify expected pass/fail matrix.

### Task 2: Repository analyzer

**Files:** `src/shadowspec/analyzer.py`, `tests/test_analyzer.py`

**Interfaces:** Produces `analyze_repository(root: Path) -> AnalysisReport`.

- [ ] Test AST inventory, calls, side-effect signals, reachable nodes, syntax errors, and path bounds.
- [ ] Verify failures.
- [ ] Implement the minimal analyzer.
- [ ] Run analyzer and full suites.

### Task 3: Differential validator

**Files:** `src/shadowspec/validator.py`, `tests/test_validator.py`

**Interfaces:** Produces `validate_candidate(candidate: str) -> ValidationRun`.

- [ ] Test candidate allowlist, isolated workspace, expected bad/narrow verdicts, timeout, source hashes, and bounded output.
- [ ] Verify failures.
- [ ] Implement validation with temporary directories and subprocess timeout.
- [ ] Run validator and full suites.

### Task 4: Evidence pack

**Files:** `src/shadowspec/evidence.py`, `tests/test_evidence.py`

**Interfaces:** Produces Markdown and JSON bytes from analysis and validation records.

- [ ] Test required reviewer fields, redaction, stable ordering, and rollback notes.
- [ ] Verify failures.
- [ ] Implement renderers.
- [ ] Run evidence and full suites.

### Task 5: Service, UI, and CLI

**Files:** `src/shadowspec/service.py`, `src/shadowspec/cli.py`, `app.py`, `tests/test_service.py`

**Interfaces:** Produces a single `run_demo(candidate)` response used by both interfaces.

- [ ] Test orchestration, clear errors, and artifact generation.
- [ ] Verify failures.
- [ ] Implement service, Streamlit golden path, and CLI smoke flow.
- [ ] Run full suites and smoke tests.

### Task 6: Bob artifacts, documentation, and submission materials

**Files:** `bob/*`, `AGENTS.md`, `README.md`, `docs/submission/*`, `docs/architecture/*`, `assets/*`

**Interfaces:** Documents the verified product and exact run/deploy flow.

- [ ] Add five bounded Bob modes, skills, actor-critic workflow, and session-export instructions.
- [ ] Add architecture diagram, demo script, pitch, submission copy, security model, deployment guide, and decision log.
- [ ] Generate screenshots, slide deck, and one-page PDF from verified app state.
- [ ] Validate links, commands, and artifact readability.

### Task 7: Release

**Files:** `.github/workflows/ci.yml`, deployment config, repository metadata.

**Interfaces:** Produces tested public source and public live demo.

- [ ] Run full tests, coverage, compile, CLI smoke, and UI health checks.
- [ ] Conduct fresh adversarial code review and fix important findings test-first.
- [ ] Create the unoccupied public repository without overwriting unrelated work.
- [ ] Push and deploy; verify public URLs.

