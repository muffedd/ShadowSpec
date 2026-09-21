# ShadowSpec Design

## Intent

ShadowSpec is a judge-facing proof that an AI development partner can make one narrow legacy-code change reviewable. It freezes observed behavior, rejects an over-broad patch, accepts the narrow patch, and exports the evidence behind that verdict.

## Winning demo

The bundled `legacy_orders` fixture applies discount codes and writes an audit row to SQLite. The approved request is: accept surrounding whitespace in a discount code while preserving case sensitivity, pricing, error behavior, and persistence.

The demo shows three states:

1. Baseline characterization: named fixtures capture return values and database effects.
2. Bad candidate: trimming and uppercasing breaks the preserved lowercase behavior and is rejected.
3. Narrow candidate: trimming only passes preserved-behavior checks and the new acceptance check.

## Architecture

- `src/shadowspec/analyzer.py`: Python AST inventory, calls, side-effect signals, and bounded blast-radius graph.
- `src/shadowspec/scenarios.py`: deterministic fixture definitions and expected observations.
- `src/shadowspec/validator.py`: isolated per-run workspaces, patch selection, subprocess pytest with timeout, normalized results.
- `src/shadowspec/evidence.py`: reviewer-ready Markdown and JSON evidence packs.
- `src/shadowspec/service.py`: orchestration API used by CLI and Streamlit.
- `app.py`: accessible, responsive judge UI with a single golden path.
- `fixtures/legacy_orders`: audited standard-library-only legacy service and prepared candidate patches.

## Security boundary

Hosted execution is restricted to the bundled fixture. Public GitHub URLs, if exposed, are validated and analysis-only. No uploaded or fetched code is imported, installed, or executed. Paths are canonicalized beneath a fixed root. Subprocesses have a timeout, bounded output, a temporary working directory, and no secrets passed explicitly. The UI never claims OS-level sandboxing.

## IBM Bob centrality

Repository artifacts define five Bob roles: mapper, characterization-test designer, implementer, critic/security reviewer, and release reviewer. The checked-in workflow explains how Bob full-repository context connects the behavior map, tests, patch, and release evidence. Exported Bob sessions must be placed in `bob_sessions/` when run in the actual IBM Bob IDE. The zero-key public demo runs deterministic local analysis and never impersonates live Bob inference.

## Non-goals

- General autonomous legacy modernization
- Executing arbitrary repositories on the hosted demo
- Proving semantic equivalence beyond named fixtures
- Autonomous merge or deployment
- Dynamic call-graph completeness

## Accessibility and failure behavior

The UI uses semantic headings, visible focus states, high contrast, text labels in addition to color, responsive columns, and actionable errors. Every run has an ID and source hash. Unsupported sources and execution failures are explicit.

## Success criteria

- A fresh install runs without API keys.
- The bad candidate fails for the intended preserved behavior.
- The narrow candidate passes characterization and acceptance checks.
- Evidence export includes source hashes, changed files, intended delta, preserved behavior, risks, reviewer checklist, rollback notes, and raw test summaries.
- The full test suite is green and the demo completes in under three minutes.

