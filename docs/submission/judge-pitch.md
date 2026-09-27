# ShadowSpec judge pitch

## The one-line pitch

ShadowSpec makes one narrow legacy-code change reviewable by freezing observed
behavior, rejecting an over-broad patch, accepting the minimal patch, and exporting
the evidence behind both verdicts.

The short version: Bob writes the patch; ShadowSpec proves it changed nothing
else. The more of a codebase an AI partner produces, the more a team needs a
gate that checks behavior rather than the diff.

## The proof judges can see

The audited `legacy_orders` fixture applies a discount code and writes an audit row
to SQLite. The requested change is precise: accept surrounding whitespace in a
discount code while preserving case sensitivity, pricing, error behavior, and
persistence.

The demo makes the safety argument concrete:

1. Baseline characterization names the existing return values and database effects.
2. The plausible bad patch trims and uppercases the code. It passes the new
   whitespace case but is rejected because lowercase `save10` must remain invalid.
3. The narrow patch trims only. It preserves the named behavior and passes the new
   acceptance case, so it is accepted.

This reject-bad/accept-narrow sequence is the product’s signature proof. The
characterization and acceptance checks remain separate, so “the new example works”
cannot hide a regression in preserved behavior.

## Why it is safe enough to review

The hosted boundary is deliberately narrow: execution is restricted to the
bundled fixture. Public GitHub URLs, if exposed, are validated and analysis-only;
uploaded or fetched code is not imported, installed, or executed. Paths are
canonicalized beneath a fixed root. Subprocesses have a timeout, bounded output, a
temporary working directory, and no secrets passed explicitly. The UI does not
claim OS-level sandboxing.

## Why IBM Bob is central

Bob’s role is made inspectable through checked-in workflow artifacts defining five
roles: mapper, characterization-test designer, implementer, critic/security
reviewer, and release reviewer. The workflow connects the behavior map, tests,
patch, and release evidence. If a workflow is run in the actual IBM Bob IDE, its
exported sessions belong in `bob_sessions/`; the zero-key public demo itself runs
deterministic local analysis and makes no claim of live Bob inference.

## What the evidence pack adds

The export is reviewer-ready: source hashes, changed files, intended delta,
preserved behavior, risks, reviewer checklist, rollback notes, and raw test
summaries travel with the verdict. Every run has an ID and source hash, while
unsupported sources and execution failures are explicit.

## Honest limitations

The verdict is scoped to named fixtures and observed behavior. ShadowSpec does not
prove semantic equivalence beyond those fixtures, provide a complete dynamic
call-graph, modernize arbitrary legacy repositories, execute arbitrary hosted
repositories, autonomously merge or deploy, or provide an OS-level sandbox.
