# ShadowSpec submission copy

## Project name

ShadowSpec

## Tagline

Reject the broad patch. Accept the narrow one. Export the proof.

## Short description

ShadowSpec is a zero-key behavior-contract maintenance gate for one audited legacy
Python service. It characterizes existing behavior, rejects a plausible
over-broad patch, accepts the minimal patch, and exports reviewer-ready evidence.

## Long description

Legacy changes are risky when “the new example works” says nothing about what was
preserved. ShadowSpec turns that risk into a visible, bounded proof.

The bundled `legacy_orders` fixture applies discount codes and records an audit row
in SQLite. The maintenance request is to accept surrounding whitespace in a
discount code while preserving case sensitivity, pricing, error behavior, and
persistence. ShadowSpec first records named baseline observations. It then
evaluates two prepared candidates:

- **Bad:** trims and uppercases the code. It accepts the new whitespace case, but
  is rejected because lowercase `save10` must remain invalid.
- **Narrow:** trims only. It preserves the named behavior and passes the new
  acceptance case, so it is accepted.

Characterization checks and acceptance checks stay separate. The result is not a
black-box “looks good” score: it is an explainable verdict with evidence behind the
preserved contract and the intended delta.

## What is included

- Deterministic baseline, bad-candidate, and narrow-candidate fixture states.
- Python AST inventory, call and side-effect signals, and a bounded blast-radius
  graph.
- Isolated per-run workspaces, subprocess timeouts, bounded output, and normalized
  validation results.
- Markdown and JSON evidence packs with source hashes, changed files, intended
  delta, preserved behavior, risks, reviewer checklist, rollback notes, and raw
  test summaries.
- An accessible, responsive judge UI with semantic headings, visible focus states,
  high contrast, text labels in addition to color, and actionable errors.
- Bob workflow artifacts for mapper, characterization-test designer, implementer,
  critic/security reviewer, and release reviewer.

## Safety boundary

Hosted execution is restricted to the bundled fixture. Public GitHub URLs, if
exposed, are validated and analysis-only. Uploaded or fetched code is never
imported, installed, or executed. Paths are canonicalized beneath a fixed root.
Subprocesses use a timeout, bounded output, a temporary working directory, and no
secrets passed explicitly. The UI does not claim OS-level sandboxing.

## IBM Bob workflow

The checked-in workflow shows how Bob full-repository context connects the behavior
map, tests, patch, and release evidence. When the workflow is run in the actual IBM
Bob IDE, exported sessions are placed in `bob_sessions/`. The zero-key public demo
runs deterministic local analysis and does not impersonate live Bob inference.

## Limitations

Verdicts are scoped to named fixtures and observed behavior. ShadowSpec does not
prove semantic equivalence beyond those fixtures, provide complete dynamic
call-graph coverage, execute arbitrary hosted repositories, perform general
autonomous legacy modernization, or autonomously merge or deploy.

## Links

Public live-demo and source links are intentionally omitted here until they are
verified. No unverified URL is part of this submission copy.

