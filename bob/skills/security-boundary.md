# Bob skill: security boundary

## Purpose

Keep analysis, validation, Bob sessions, and the public zero-key demo inside
their documented trust boundaries.

## Checks

- Hosted execution is limited to the bundled fixture.
- Paths are canonicalized beneath a fixed root before access.
- Public URLs, if accepted, are validated and analysis-only; fetched code is
  never imported, installed, or executed.
- Subprocesses have bounded time, output, and temporary workspaces.
- No secrets are passed explicitly or written to evidence/session exports.
- UI and docs do not call these controls an OS-level sandbox.
- The zero-key demo performs deterministic local analysis and makes no claim
  of live Bob inference.

## Escalation

Any failed boundary check is a release-blocking finding until its scope is
understood and a bounded correction is reviewed.

