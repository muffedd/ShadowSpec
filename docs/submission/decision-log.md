# ShadowSpec decision log

This log records the product decisions locked by the design and winner-pattern
research.

## 1. Narrow the product to one audited fixture

**Decision:** Use one bundled `legacy_orders` service as the hosted proof.

**Reason:** A bounded, inspectable fixture makes the verdict reproducible and keeps
arbitrary hosted execution out of scope. ShadowSpec is a behavior-contract
maintenance gate, not general autonomous legacy modernization.

## 2. Make reject-bad/accept-narrow the signature proof

**Decision:** Demonstrate a plausible bad patch followed by a minimal accepted
patch.

**Reason:** The bad patch trims and uppercases a discount code, so it appears to
solve whitespace but breaks preserved lowercase behavior. The narrow patch trims
only, preserving case sensitivity while satisfying the request. This makes
regression risk visible instead of hiding it behind a single happy-path example.

## 3. Keep characterization and acceptance separate

**Decision:** Preserve existing observations and test the requested new behavior as
different checks.

**Reason:** The candidate must satisfy both the old contract and the intended delta.
The baseline captures return values and database effects, while acceptance checks
surrounding-whitespace behavior.

## 4. Treat safety as a precise boundary

**Decision:** Restrict hosted execution to the bundled fixture; validate any
exposed public GitHub URL as analysis-only; never import, install, or execute
uploaded or fetched code.

**Reason:** Paths can be canonicalized beneath a fixed root, and validation can use
timeouts, bounded output, temporary workspaces, and no explicitly passed secrets.
The product must not call these controls an OS-level sandbox.

## 5. Keep blast-radius claims bounded

**Decision:** Provide Python AST inventory, call and side-effect signals, and a
bounded blast-radius graph, while labeling dynamic-dispatch coverage incomplete.

**Reason:** Static analysis is useful review evidence, but it is not a complete
dynamic call graph or proof of semantic equivalence.

## 6. Make Bob central through artifacts, not an unavailable runtime claim

**Decision:** Define five Bob roles in checked-in workflow artifacts: mapper,
characterization-test designer, implementer, critic/security reviewer, and release
reviewer.

**Reason:** The workflow connects full-repository context to the behavior map,
tests, patch, and release evidence. When run in the actual IBM Bob IDE, exported
sessions belong in `bob_sessions/`. The zero-key public demo performs deterministic
local analysis and does not impersonate live Bob inference.

## 7. Prioritize reviewer evidence over visual complexity

**Decision:** Export Markdown and JSON evidence packs and show the failed bad patch;
do not make a complex graph visualization the centerpiece.

**Reason:** Reviewers need source hashes, changed files, intended delta, preserved
behavior, risks, reviewer checklist, rollback notes, and raw test summaries to
understand a verdict.

## 8. Be explicit about non-goals

**Decision:** State that the system does not execute arbitrary hosted repositories,
prove semantic equivalence beyond named fixtures, autonomously merge or deploy, or
provide general autonomous modernization.

**Reason:** Clear limitations preserve trust in the narrow proof and prevent a
fixture-scoped verdict from being overread as a universal guarantee.

