From d6d0df3101112e5b4bc158fad5a0ce0e3012d90b Mon Sep 17 00:00:00 2001
From: "Instinct (for Sutharshan)" <noreply@instinct.local>
Date: Sun, 27 Sep 2026 12:59:29 +0530
Subject: [PATCH] README: sync with event-branch submission state

- 76 tests / 91.46% coverage (was 64 / 89.29%)
- 6 IBM Bob session transcripts as build proof
- live demo URL, CI behavior-gate section, scope limits
- problem/business-value paragraph at top
---
 README.md | 44 +++++++++++++++++++++++++++++++-------------
 1 file changed, 31 insertions(+), 13 deletions(-)

diff --git a/README.md b/README.md
index adb7f45..946872e 100644
--- a/README.md
+++ b/README.md
@@ -1,16 +1,37 @@
 # ShadowSpec
 
-> **Pre-kickoff reference baseline.** This repository is scaffolding and review evidence, not the eligible submitted core. See [event-window provenance](docs/release/event-window-provenance.md).
+> **Hackathon build (IBM Bob 2.0, lablab.ai):** authored by IBM Bob on branch [`bob-2.0-build-2026-09-25`](https://github.com/muffedd/ShadowSpec/tree/bob-2.0-build-2026-09-25) starting after kickoff on 2026-09-25. See [event-window provenance](docs/release/event-window-provenance.md).
 
 **Reject the broad patch. Accept the narrow one. Export the proof.**
 
 ShadowSpec is a zero-key evidence workbench for one risky maintenance job: changing undocumented legacy behavior without quietly changing something else.
 
+## Problem and business value
+
+Legacy maintenance fails when a patch satisfies the new request but silently changes an old contract. That failure mode is expensive: it ships as a regression discovered by customers, not reviewers, and the audit trail is a shrug. ShadowSpec turns review into executable evidence — the intended delta and the behavior that must remain unchanged are tested separately, and the verdict ships with a proof pack a reviewer can check in minutes instead of hours.
+
 The bundled demo asks for one precise change to a Python order service: accept surrounding whitespace in `SAVE10` while preserving case sensitivity, pricing, errors, and the SQLite audit write.
 
-## Problem
+## Live demo
+
+- **Live demo:** https://shadowspec-demo.pages.dev
+- **Source:** https://github.com/muffedd/ShadowSpec
+
+### Try it in 60 seconds
+
+1. Open the live demo and run **Plausible bad candidate**. Verdict: REJECTED - the new whitespace case passes, but lowercase `save10` behavior changed.
+2. Run **Narrow candidate**. Verdict: ACCEPTED - preserved behavior and the requested delta both pass.
+3. Open the evidence drawer to see the diff, provenance hashes, and export a condensed preview.
+
+| Build proof | |
+| --- | --- |
+| Tests | 76 passed, 3 platform-gated skips |
+| Coverage | 91.46% (CI enforces >= 85%) |
+| IBM Bob sessions | 6 exported task transcripts + consumption screenshots in [`bob_sessions/`](https://github.com/muffedd/ShadowSpec/tree/bob-2.0-build-2026-09-25/bob_sessions) |
+
+## CI behavior gate
 
-Legacy maintenance fails when a patch satisfies the new request but silently changes an old contract. Reviewers need executable evidence of both the intended delta and the behavior that must remain unchanged.
+The event branch ships a GitHub Actions [behavior-gate workflow](https://github.com/muffedd/ShadowSpec/blob/bob-2.0-build-2026-09-25/.github/workflows/behavior-gate.yml) plus [`scripts/check-behavior-gate.sh`](https://github.com/muffedd/ShadowSpec/blob/bob-2.0-build-2026-09-25/scripts/check-behavior-gate.sh): a deliberately bad candidate PR goes red (rejected), while the accepted narrow candidate stays green. The workflow reports the PR's actual changed files and runs the differential check against them; merge blocking itself comes from branch protection requiring the green check. What is and is not proven is scoped explicitly in [docs/branch-protection.md](https://github.com/muffedd/ShadowSpec/blob/bob-2.0-build-2026-09-25/docs/branch-protection.md).
 
 ## Three-minute golden path
 
@@ -26,11 +47,11 @@ Legacy maintenance fails when a patch satisfies the new request but silently cha
 | Bad: `strip().upper()` | Fail | Pass | Rejected: lowercase behavior changed |
 | Narrow: `strip()` | Pass | Pass | Accepted for the named fixtures |
 
-ShadowSpec never treats “the new example works” as sufficient evidence. Existing observations and the requested delta are tested separately.
+ShadowSpec never treats "the new example works" as sufficient evidence. Existing observations and the requested delta are tested separately.
 
 ## Setup
 
-Requires Python 3.12 or later.
+Requires Python 3.12 or later for the pinned install. The engine itself is standard-library only: to run just the core test suite, `pip install pytest pytest-cov` is enough (`tests/test_app.py` needs Streamlit and `tests/test_deployment.py` needs Python 3.11+; both are platform-gated).
 
 ```bash
 python -m venv .venv
@@ -92,10 +113,7 @@ use in an IBM Bob IDE. They are workflow guidance, not evidence that Bob perform
 this build. See [AGENTS.md](AGENTS.md), [Bob workflow](docs/architecture/bob-workflow.md),
 and the role contracts under [`bob/`](bob/).
 
-No Bob runtime session or session export is included in the current repository.
-If the workflow is later run in IBM Bob, its redacted export belongs in
-[`bob_sessions/`](bob_sessions/). The public zero-key demo performs deterministic
-local analysis and does not impersonate live Bob inference.
+The six Bob session exports from the `bob-2.0-build-2026-09-25` build — task transcripts plus consumption screenshots — are in [`bob_sessions/`](https://github.com/muffedd/ShadowSpec/tree/bob-2.0-build-2026-09-25/bob_sessions) on the event branch. These are redacted task-history exports from the IBM Bob IDE sessions that authored that branch. The public zero-key demo performs deterministic local analysis and does not impersonate live Bob inference.
 
 ## Evidence pack
 
@@ -131,12 +149,12 @@ See [security.md](docs/submission/security.md) for the threat boundary and limit
 pytest -q --cov=shadowspec --cov-report=term --cov-fail-under=85
 ```
 
-Verified reference baseline: **64 tests passed, 89.29% coverage**. CI enforces at least 85% coverage.
+Verified reference baseline: **76 tests passed, 3 platform-gated skips, 91.46% coverage**. CI enforces at least 85% coverage.
 
 ## Demo and submission
 
-- Live demo: `PUBLIC_URL_PENDING`
-- GitHub repository: `GITHUB_URL_PENDING`
+- Live demo: https://shadowspec-demo.pages.dev
+- GitHub repository: https://github.com/muffedd/ShadowSpec
 - Demo video: `VIDEO_URL_PENDING`
 
 ## Submission materials
@@ -152,7 +170,7 @@ Verified reference baseline: **64 tests passed, 89.29% coverage**. CI enforces a
 
 ## Scope limits
 
-An accepted result means that the named observations passed for the audited fixture, together with the requested acceptance check. It does not prove semantic equivalence, complete dynamic-call coverage, or production safety for an arbitrary codebase.
+An accepted result means that the named observations passed for the audited fixture, together with the requested acceptance check. It does not prove semantic equivalence, complete dynamic-call coverage, or production safety for an arbitrary codebase. Verdicts apply to the bundled named fixtures only.
 
 ## License
 
-- 
2.34.1

