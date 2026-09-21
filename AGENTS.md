# ShadowSpec agent guide

This repository is a narrow, judge-facing proof for legacy maintenance. The
working example is the bundled `fixtures/legacy_orders` service: accept
surrounding whitespace in a discount code while preserving case sensitivity,
pricing, errors, and the SQLite audit side effect.

## Scope and source of truth

Before proposing or reviewing a change, read the full repository context that
is available in the checkout:

1. this file;
2. `docs/superpowers/specs/2026-09-21-shadowspec-design.md`;
3. `docs/superpowers/plans/2026-09-21-shadowspec.md`;
4. the relevant source, fixtures, tests, and any generated evidence; and
5. the current diff and repository status.

Do not infer behavior from a single function or from a truncated snippet.
Dynamic dispatch and static blast-radius findings must be labeled as
incomplete where applicable.

The files under `bob/` are conservative Markdown role and skill contracts.
They are repository guidance for an IBM Bob session, not a claim that this
checkout contains a particular Bob runtime, parser, or officially executable
mode syntax. Adapt the prose to the actual IBM Bob IDE integration in use.

## Bob roles

The workflow has five bounded roles:

| Role | Primary responsibility | Handoff |
| --- | --- | --- |
| Mapper | Inventory the repository, behavior, calls, and side effects | Context packet to characterization |
| Characterization | Freeze observed behavior and write named checks | Baseline contract to implementer |
| Implementer | Make the smallest requested patch | Diff and test report to critic |
| Critic | Try to falsify the patch, including security and scope claims | Adversarial verdict to release |
| Release | Assemble reproducible evidence and final checklist | Session/evidence export |

Each role must state what it observed, what it did not inspect, and what the
next role is allowed to assume. The actor-critic handoff is explicit: the
implementer is the actor; the critic is an independent reviewer who receives
the full context packet and diff, not just the implementer’s summary.

## Required behavior workflow

- Keep characterization tests separate from the new acceptance check.
- Demonstrate both prepared candidates when available: the over-broad patch
  must fail for a preserved behavior, and the narrow patch must pass the
  named contract.
- Report evidence as scoped to named fixtures and observed behavior. Do not
  claim general semantic equivalence.
- Preserve the source hash, changed-file list, intended delta, preserved
  behavior, risks, reviewer checklist, rollback note, and raw test summary in
  release evidence.
- A failed run is a useful result. Record the failure and its bounded cause;
  do not silently retry with broader permissions.

## Security and zero-key boundary

The public demo is deterministic local analysis of the bundled fixture and
requires no API key. It must not impersonate live Bob inference or imply that
the demo called a model. If a Bob session is used during development, keep
its transcript/export separate from the zero-key demo path.

Hosted execution is restricted to the bundled fixture. Public GitHub URLs, if
supported by the application, are analysis-only; fetched or uploaded code is
not imported, installed, or executed. The immutable server-owned SHA-256 manifest
for the three bundled variants is the verdict-integrity boundary: verify the
baseline and selected source bytes before child-process launch. Canonicalize paths
beneath the fixed fixture root, bound subprocess time and output, use a temporary
workspace, and never pass secrets explicitly. These measures are application
guardrails, not an OS-level sandbox claim; hash validation does not isolate a
running process from the host.

Never place API keys, environment variables, cookies, private source, absolute
host paths, or credentials in Bob session exports or evidence packs.

## Session and artifact handoff

Use `bob_sessions/README.md` for the export checklist and naming convention.
The release role may mark an artifact ready only when the export identifies
the repository revision/source hash, role sequence, bounded verdict, tests,
and known limitations. If an IDE uses a different export format, preserve the
same information in an adjacent Markdown manifest rather than inventing
unsupported syntax.
