# Event-window provenance

## Status

This repository is a **pre-kickoff reference and scaffolding baseline**. It is not the eligible submitted core.

The user-defined eligibility boundary is **Friday, 25 September 2026 at 8:30 PM IST**. Any corrected build completed before that timestamp remains reference material only.

## Preserved reference points

- Pre-kickoff UI and documentation commit: `4b72a298294dc80ad7e83d18a7f2eeb0ec7bb413`
- Pre-fix archive: `ShadowSpec-current-tree.zip`
- Reference project: ShadowSpec behavior-contract maintenance gate

## Event-window rebuild — bob-2.0-build-2026-09-25

### Branch

`bob-2.0-build-2026-09-25`

### Base commit

`4b72a298294dc80ad7e83d18a7f2eeb0ec7bb413` (pre-kickoff reference)

### Files authored or materially rebuilt during the window

| File | Change summary |
| --- | --- |
| `src/shadowspec/validator.py` | Full rebuild: correct audited fixture SHA-256 manifest; cross-platform subprocess execution model (file-based result channel instead of `pass_fds`); polling wait loop with kill-on-output-limit; explicit SQLite connection close in runner to avoid Windows file-lock on per-case DB files; `_terminate_process` helper; separation rule enforced (strip().upper() → rejected, strip() → accepted). |
| `tests/test_validator.py` | Updated `_run_modified_candidate` to pass workspace dir instead of `audit.db` path; updated stdout-forge test to use file-based result model; added Windows symlink skip marker. |
| `tests/test_analyzer.py` | Added Windows symlink skip marker. |
| `docs/release/event-window-provenance.md` | This record. |

### Test evidence

- **65 passed, 3 skipped** (2 × Windows symlink privilege skip, 1 × Linux process-group regression skip)
- **Coverage: 91.46%** (threshold: 85%)
- `PYTHONPATH=src python -m shadowspec.cli run bad --format markdown` → `REJECTED`, exit 2
- `PYTHONPATH=src python -m shadowspec.cli run narrow --format markdown` → `ACCEPTED`, exit 0

### Separation rule verification

| Candidate | Characterization | Acceptance | Verdict |
| --- | --- | --- | --- |
| Baseline | Pass | **Fail** | Rejected (request not implemented) |
| Bad: `strip().upper()` | **Fail** (lowercase check) | Pass | Rejected (preserved behavior changed) |
| Narrow: `strip()` | Pass | Pass | **Accepted** |

## Event-window rebuild rule

During the eligible event window, rebuild the submitted core from a fresh branch and record:

1. Event-window start timestamp and base commit.
2. Files authored or materially rebuilt during the window.
3. Test, coverage, CLI, and deployment evidence generated during the window.
4. IBM Bob session exports created during the window, with secrets and personal data redacted.
5. Final commit and public deployment URL used for submission.

Reference artifacts may guide the rebuild, but must not be misrepresented as event-window implementation. The release baseline published before kickoff must retain the `pre-kickoff-reference` label in its README, repository description, and deployment copy.
