# ShadowSpec demo script

**Target runtime: under three minutes.** This is a judge-facing proof, not a tour of
every implementation detail. Keep the golden path visible and narrate the verdicts.

## 0:00–0:20 — Frame the request

“This is ShadowSpec, a behavior-contract maintenance gate for one audited legacy
Python service. The request is deliberately narrow: accept surrounding whitespace
in a discount code while preserving case sensitivity, pricing, error behavior, and
the SQLite audit write.”

Point out that the hosted demo is zero-key and runs against the bundled
`legacy_orders` fixture. It does not execute an arbitrary repository.

## 0:20–0:55 — Establish the baseline

Run the baseline characterization. Show the named observations:

- the exact code `SAVE10` receives the discount;
- the lowercase code `save10` remains invalid;
- surrounding whitespace is not accepted yet;
- ordinary orders return the observed totals and write an audit row; and
- a negative subtotal raises the observed error without an audit write.

“These observations are the preserved contract. The acceptance check for the new
request is separate from characterization, so a patch must do both jobs.”

## 0:55–1:35 — Reject the plausible bad patch

Select the prepared **bad** candidate. Describe it accurately: it trims whitespace
and normalizes case.

Show the verdict: **rejected**. It satisfies the new whitespace case, but the
preserved lowercase behavior is broken—`save10` now receives a discount. The
characterization checks therefore fail even though the acceptance check passes.

“This is the key safety proof: a patch can look helpful and still be rejected when
it broadens behavior outside the request.”

## 1:35–2:10 — Accept the narrow patch

Select the prepared **narrow** candidate. Describe it accurately: it trims only and
keeps the comparison case-sensitive.

Show the verdict: **accepted**. The preserved observations pass, and the new
surrounding-whitespace case passes. The return value, error behavior, and audit
effect remain in the named fixture checks.

## 2:10–2:40 — Export evidence and explain Bob’s role

Export the evidence pack. Point to the source hash, changed-file/intended-delta
summary, preserved behavior, risks, reviewer checklist, rollback notes, and raw
test summaries.

“Bob is represented by repository workflow guidance for mapper, characterization-
test designer, implementer, critic/security reviewer, and release reviewer. In an
actual IBM Bob IDE run, exported Bob sessions belong in `bob_sessions/`. This
zero-key public demo performs deterministic local analysis; it does not impersonate
live Bob inference or claim that these Markdown files are executable Bob syntax.”

## 2:40–3:00 — Close with the boundary

“The verdict is scoped to named fixtures and observed behavior. ShadowSpec does
not claim semantic equivalence, a complete dynamic call graph, arbitrary hosted
execution, autonomous merge or deployment, or OS-level sandboxing. That explicit
boundary is what makes the bad-patch rejection and narrow-patch acceptance
reviewable.”
