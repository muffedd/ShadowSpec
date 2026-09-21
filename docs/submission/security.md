# ShadowSpec security model

## Security objective

Make a narrow legacy-code verdict reviewable while keeping hosted execution
bounded to an audited fixture. The system is designed to expose regressions and
failures clearly; it is not presented as an OS-level sandbox.

## Trust boundary

The hosted product runs only the bundled `legacy_orders` fixture. Public GitHub
URLs, if exposed, are an optional analysis-only input. Uploaded or fetched code is
not imported, installed, or executed.

## Controls

### Input and path handling

- Public GitHub URLs are validated before any analysis path is considered.
- Paths are canonicalized beneath a fixed root.
- Unsupported sources are reported explicitly.

### Execution containment

- Candidate validation runs in an isolated per-run workspace.
- Subprocesses have a timeout and bounded output.
- Temporary working directories limit the lifetime and scope of a run.
- No secrets are passed explicitly to subprocesses.

These controls define bounded fixture execution. They do not constitute an
OS-level security sandbox, and the UI does not claim one.

### Evidence and failure behavior

- Every run has a run ID and source hash.
- Execution failures and unsupported sources are explicit rather than hidden in a
  success state.
- Evidence is scoped to named fixtures and observed behavior.

## Behavioral safety proof

Security is not only process isolation. The demo also checks the change boundary:

- The bad candidate trims and uppercases the discount code. It is rejected because
  the preserved lowercase behavior changes.
- The narrow candidate trims only. It is accepted when characterization and the
  new whitespace acceptance check both pass.

The proof covers the named return values, error behavior, and SQLite audit effects
of the audited fixture. It does not claim semantic equivalence outside those
fixtures.

## Bob and security review

The checked-in Bob workflow includes a critic/security reviewer role alongside the
mapper, characterization-test designer, implementer, and release reviewer. In an
actual IBM Bob IDE run, exported Bob sessions belong in `bob_sessions/`. The
zero-key public demo performs deterministic local analysis and makes no claim of
live Bob inference.

## Out of scope

ShadowSpec does not execute arbitrary repositories on the hosted demo, perform
general autonomous legacy modernization, provide complete dynamic call-graph
coverage, prove semantic equivalence beyond named fixtures, or autonomously merge
or deploy code.

