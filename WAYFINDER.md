# ShadowSpec wayfinder

## Destination

A public, zero-key hackathon demo that proves one claim in under three minutes: ShadowSpec rejects a plausible behavior-breaking patch, accepts the narrow patch, and exports reviewer-ready evidence. The release target includes tested source, Bob workflow guidance, a public deployment, verified screenshots, slides, and a one-page handout.

## Notes

- Prior IBM Bob winners favored one sharp artifact and an instantly legible proof.
- Hosted execution remains restricted to the audited bundled Python fixture.
- The public demo performs deterministic local analysis. Bob session exports remain separate evidence.
- Remaining implementation follows the Ponytail ladder manually: remove, reuse, stdlib, native platform, installed dependency, smallest new code. Validation, security, data-loss handling, and accessibility are never cut.

## Decisions so far

1. Narrowed broad legacy modernization to a behavior-contract maintenance gate.
2. Chose `SAVE10` whitespace handling as the only maintenance request.
3. Kept characterization separate from acceptance.
4. Made bad-patch rejection the signature proof.
5. Limited hosted execution to three audited variants.
6. Used Python AST, subprocess, tempfile, hashlib, JSON, and SQLite from the standard library for the core.
7. Used Streamlit as the only runtime UI dependency.
8. Defined five Bob roles with an actor-critic handoff and honest session-export boundary.
9. Chose Streamlit Community Cloud as the primary deployment target and Render as fallback.

## Not yet specified

- Actual Bob IDE session exports. These require a real Bob run and cannot be fabricated.
- Final public GitHub and live-demo URLs until publication succeeds and both are verified.
- Whether future public GitHub import should analyze fetched source. It remains disabled in this release.

## Out of scope

- Arbitrary hosted repository execution
- General autonomous modernization
- Autonomous merge or deployment
- Complete dynamic call graphs
- Semantic-equivalence claims beyond named fixtures
- Private repository ingestion
- Installing dependencies from analyzed repositories

## Remaining decision tickets

| Ticket | Decision needed | Default and evidence gate | Status |
| --- | --- | --- | --- |
| D10 | Public repository name | Use `muffedd/shadowspec`; fallback only if occupied | Target confirmed unoccupied |
| D11 | Deployment path | Streamlit Community Cloud if GitHub publication succeeds; Render fallback | Open |
| D12 | Screenshot source | Capture the verified public deployment, never a mock | Open |
| D13 | Submission URLs | Add only after direct verification | Open |
| D14 | Bob evidence | Keep session export unresolved until a real IBM Bob run exists | Human-in-the-loop unresolved |
