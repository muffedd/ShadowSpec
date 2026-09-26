# Bob session exports - manifest

This folder is the audit trail for the claim that the
`bob-2.0-build-2026-09-25` branch was authored by IBM Bob inside the hackathon
event window. Each task below was run in the IBM Bob IDE from an
Instinct-written prompt; the transcript export and a consumption screenshot
were captured after each task.

## Stats

| Proof | Value |
| --- | --- |
| Bob IDE task exports | 6 (5 task transcripts + 1 combined export) |
| Consumption screenshots | 6 |
| Final test state | 76 passed, 3 platform-gated skips |
| Final coverage | 91.46% (CI enforces >= 85%) |
| Branch | `bob-2.0-build-2026-09-25` |

## Index of exports

| File | What it contains | What it proves |
| --- | --- | --- |
| `bob-tasks-ShadowSpec-2026-09-26.md` | Tasks 1-2, combined export: event-window rebuild of the core engine (characterization runner, acceptance checker, differential validator) and the CI behavior gate. | The engine itself was authored by Bob in-window, preserving the reject-bad / accept-narrow separation rule. |
| `bob-task-fa9dd9e53831751d2e87ee7fb0c669d9-2026-09-26.md` | Task 3: the judge-facing Next.js workbench (candidate rail, verdict panel, evidence drawer, scan animation) built on the existing design tokens. | The UI was authored by Bob against a design-system contract, with precomputed verdicts from the real engine. |
| `bob-task-ee98feac15ea5912174a9133152f75a8-2026-09-26.md` | Task 4: static-export hardening for the UI and the event-window provenance record. | The deployment path and the in-window authorship claim are documented by the same tool that did the work. |
| `bob-task-b9e630a4f37c5de6cab777b6028f89b3-2026-09-26.md` | Task 5: adversarial release review - full-diff correctness pass, credential sweep (zero found), final review recorded in `docs/submission/final-review.md`. | An independent critic pass ran before submission, including a secrets check. |
| `bob-task-7441e2fffe971b8a03380d56c50a0cfc-2026-09-26.md` | CRLF portability fix: `.gitattributes` pins LF for fixtures, integrity manifest recomputed against LF bytes. | The hash-manifest integrity boundary works on both Windows and Linux checkouts, including CI. |
| `bob-task-0b38de284f48da0e1eacb961ba378b0b-2026-09-26.md` | Pre-submission fix pack: 7 targeted fixes (gate script stdin fix, workflow PR-diff scoping, claim scoping, UI honesty relabels, export-button nesting, preview labeling, real URLs). | Known review findings were fed back to Bob and fixed the same day. |

## About the "Status: error" header in the fix-pack export

`bob-task-0b38de28...md` carries a `Status: error` header because the Bob
session exhausted its credit allocation during its final verification step,
after the fixes themselves had been applied. The fixes were verified
independently of that session: they landed as commit `a214e94`, the full test
suite was re-run separately (76 passed, 91.46% coverage), and the live demo
was rebuilt and redeployed from that commit. Nothing in the export is
fabricated to hide the interruption.

## Consumption screenshots

`Screenshot 2026-09-26 *.png` (6 files) are the Bob IDE consumption summaries
captured after each task checkpoint, kept alongside the transcripts as the
credit-usage record.

## Reading guide for judges

Start with the manifest row for the claim you want to check, open that export,
and search for the acceptance criteria at the top of each task. The
zero-key public demo is a separate deterministic path and does not claim live
Bob inference; this folder is the evidence for the build process itself.
