# ShadowSpec security model

## Security objective

Make a narrow legacy-code verdict reviewable while keeping hosted execution
bounded to an audited fixture. The system is designed to expose regressions and
failures clearly; it is not presented as an OS-level sandbox.

## Trust boundary

The hosted product runs only the bundled `legacy_orders` fixture. Public GitHub
URL input is disabled in this release. Uploaded or fetched code is not imported,
installed, or executed.

An immutable, server-owned SHA-256 manifest pins the exact bytes of
`baseline.py`, `bad.py`, and `narrow.py`. Before starting a child process, the
validator compares both the baseline and the selected candidate with that
manifest. A mismatch produces a structured integrity error and the file is not
executed. These audited hashes are the verdict-integrity boundary: candidate
names alone are not sufficient authorization to execute changed bytes.

## Controls

### Input and path handling

- Public GitHub URL input is not exposed in the current UI.
- Paths are canonicalized beneath a fixed root.
- Baseline and selected-candidate bytes must match their audited SHA-256 values
  before execution.
- Unsupported sources are reported explicitly.

### Execution containment

- Candidate validation runs in an isolated per-run workspace.
- Subprocesses have a timeout and bounded output.
- Temporary working directories limit the lifetime and scope of a run.
- No secrets are passed explicitly to subprocesses.

These controls define bounded fixture execution. They do not constitute an
OS-level security sandbox, and the UI does not claim one. The hash manifest
protects verdict input integrity; it does not isolate an executing process from
the host operating system.

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

The checked-in Markdown guidance defines a proposed critic/security reviewer role
alongside mapper, characterization, implementer, and release roles. No Bob runtime
session or export is included in the current repository. If this workflow is run
in an IBM Bob IDE later, its redacted export belongs in `bob_sessions/`. The
zero-key public demo performs deterministic local analysis and makes no claim of
live Bob inference.

## Out of scope

ShadowSpec does not execute arbitrary repositories on the hosted demo, perform
general autonomous legacy modernization, provide complete dynamic call-graph
coverage, prove semantic equivalence beyond named fixtures, or autonomously merge
or deploy code.
