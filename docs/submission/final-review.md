# Final adversarial and minimality review

## Previous minimality pass (pre-2026-09-26)

- The hosted release has one golden path and three audited variants; public-repository execution does not exist.
- Core analysis and validation reuse Python's AST, subprocess, tempfile, hashlib, JSON, difflib, and SQLite modules.
- Streamlit is the only runtime UI dependency; pytest is development-only.
- The unused lockfile was removed. The approved candidate now differs from the baseline by only the requested normalization expression.
- Validation, path containment, structured failures, accessibility cues, and evidence provenance were retained even where they cost additional code.

---

## Adversarial release review — 2026-09-26

**Reviewer:** IBM Bob (adversarial mode)
**Branch:** `bob-2.0-build-2026-09-25`
**Diff base:** `main`
**Test result:** 76 passed, 3 skipped (platform-only), 91.46% coverage — **GREEN**

---

### 1. Engine correctness review

**Diff reviewed:** 9 commits, ~14 000 lines added (primarily new files: Next.js UI, CI workflow, session exports, design tokens).

**Core change:** [`src/shadowspec/validator.py`](../../src/shadowspec/validator.py) — full event-window rebuild.

| Area | Finding | Status |
|---|---|---|
| Subprocess isolation | Old Linux-only `selectors`/`pass_fds` pipe replaced with cross-platform temp-file result channel — correct, simpler, portable. | ✓ No issue |
| `_drain_stream` threads | Stdout/stderr drained in background threads with a byte cap; `kill_event` triggers termination on cap breach. | ✓ No issue |
| `_terminate_process` | POSIX: `os.killpg` + `signal.SIGKILL`; Windows: `process.kill()`. Both paths handle `OSError` gracefully. | ✓ No issue |
| Runner result channel | Runner writes JSON to `result_path` (temp file, not an inherited fd). Result is read by parent after subprocess exits. Cannot be forged by candidate stdout. | ✓ No issue |
| Separation rule | `bad` candidate: `strip().upper()` → `characterization_passed=False`, `acceptance_passed=True`, `verdict=rejected`. `narrow` candidate: `strip()` only → all checks pass, `verdict=accepted`. Validated end-to-end by `test_behavior_gate.py`. | ✓ No issue |
| SHA integrity check | `AUDITED_VARIANT_SHA256` checked for both the selected candidate and `baseline.py` before any subprocess is launched. | ✓ No issue |
| Windows compatibility | `pass_fds` and `selectors` removed; `start_new_session` only set on POSIX. Tests pass on Windows. | ✓ No issue |

**Verdict on engine:** Correct and complete. Separation rule is enforced by both tests and live engine.

---

### 2. CI gate behavior

**File:** [`.github/workflows/behavior-gate.yml`](../../.github/workflows/behavior-gate.yml)

| Check | Finding | Status |
|---|---|---|
| Negative control step | Runs `bad` candidate, asserts `verdict=rejected`, `characterization_passed=False`, `acceptance_passed=True`. Uses `|| true` to capture non-zero exit then asserts in Python. | ✓ Correct |
| Positive control step | Runs `narrow` candidate, asserts `verdict=accepted`, all checks pass. Hard exit on failure. | ✓ Correct |
| Gate step | Separate "Characterization gate (must be green to merge)" step runs `narrow` again and `sys.exit(1)` on any failure. This is the step that branch protection must require. | ✓ Correct |
| Gate bites on bad patch | The bad candidate **cannot** be accidentally substituted for narrow here; the gate step only runs `narrow` by name. | ✓ No issue |
| Coverage threshold | `pytest --cov-fail-under=85`. Current actual: 91.46%. | ✓ No issue |
| Permissons | `permissions: contents: read` — minimal. | ✓ No issue |

**Verdict on CI gate:** Both controls are live and the gate step correctly exits non-zero when `characterization_passed` is false.

---

### 3. Frontend verdict logic

**Files:** [`web/shadowspec-ui/components/VerdictPanel.tsx`](../../web/shadowspec-ui/components/VerdictPanel.tsx), [`web/shadowspec-ui/pages/index.tsx`](../../web/shadowspec-ui/pages/index.tsx), [`web/shadowspec-ui/types/verdict.ts`](../../web/shadowspec-ui/types/verdict.ts)

| Area | Finding | Status |
|---|---|---|
| `isAccepted` derivation | `verdict.verdict === "accepted"` — string equality against a typed `"accepted" \| "rejected" \| "error"` union. Correct. | ✓ No issue |
| Characterization/acceptance pills | Rendered directly from `verdict.characterization_passed` and `verdict.acceptance_passed` booleans. No derived logic. | ✓ No issue |
| Check list | Rendered from `verdict.checks[]`, type-checked against `CheckResult` interface. | ✓ No issue |
| Static verdicts | Pre-computed JSON in `public/verdicts/` — loaded at build time, no runtime API call. | ✓ No issue |
| `"error"` verdict | Renders with rejected (red) styling since `isAccepted` is `false` for `"error"`. Acceptable given demo-only scope. | ✓ Acceptable |

**Verdict on frontend:** Logic is correct and consistent with engine verdicts.

---

### 4. Secrets and credentials scan

**Patterns scanned:** `api_key`, `secret`, `token`, `password`, `AWS_ACCESS_KEY_ID`, `OPENAI_API_KEY`, `sk-...`, `ghp_...`, `Bearer ...`

**Result:** **Zero secrets found** across all `.py`, `.ts`, `.tsx`, `.yml`, `.yaml`, `.json`, `.md`, `.txt`, `.env`, `.sh`, `.cfg`, `.ini`, `.toml` files (excluding `node_modules`, `.git`, `__pycache__`).

---

### 5. Bugs found and fixed

#### 5a. README stale claim about `bob_sessions/`

**File:** [`README.md`](../../README.md) line 95–98

**Before:**
> "No Bob runtime session or session export is included in the current repository. If the workflow is later run in IBM Bob, its redacted export belongs in `bob_sessions/`."

**After:**
> "Bob session exports from the `bob-2.0-build-2026-09-25` build are in `bob_sessions/`. These are redacted task-history exports from the IBM Bob IDE sessions that authored this branch."

**Impact:** Factual. Session exports were present but the README said they weren't. Fixed.

#### 5b. Placeholder `deadbeef` hashes in static verdict JSON files

**Files:** `web/shadowspec-ui/public/verdicts/{baseline,bad,narrow}.json`

**Before:**
```json
"validator_sha256": "deadbeef00000000000000000000000000000000000000000000000000000001",
"runner_sha256":    "deadbeef00000000000000000000000000000000000000000000000000000002"
```

**After (real hashes):**
```json
"validator_sha256": "3fb01d393fb45161a017854c182a455d2a929fdf5b86d1b0cd9dd74f01f00e63",
"runner_sha256":    "d0c2d57807be7856dbbd26204a0244e527c25737495d9d5fda84447a0b39e498"
```

**Impact:** The static verdict files displayed in the judge UI now show the real SHA-256 of the validator module and embedded runner, matching the values that a live engine run would produce. The evidence chain is now internally consistent.

---

### 6. Bob sessions present and referenced

`bob_sessions/` contains:

- `bob-task-fa9dd9e53831751d2e87ee7fb0c669d9-2026-09-26.md` — full task history export
- `bob-tasks-ShadowSpec-2026-09-26.md` — task summary export
- `README.md` — redaction checklist and export format guidance
- Three PNG screenshots from the IDE

The README now correctly references these exports (see fix 5a above).

---

### 7. Test suite — final result

```
76 passed, 3 skipped, 91.46% coverage
```

Skips are platform-only (Windows lacks symlink privilege and Linux process-group regression). No functional tests skipped. Coverage exceeds the 85% CI requirement.

---

### 8. Grill-me objections (retained and updated)

| Objection | Evidence-backed answer or limit |
|---|---|
| Is this another repository chatbot? | No. The demo produces deterministic AST evidence, executes named behavior checks, rejects a plausible bad patch, accepts the narrow patch, and exports a review pack. |
| Does acceptance prove semantic equivalence? | No. It proves only the named observations, and the UI and evidence say so. |
| Can the hosted app execute a pasted repository? | No. Execution is allowlisted to the bundled fixture; GitHub import is out of scope. |
| Is the call graph complete? | No. It is static and intentionally reports dynamic-dispatch limitations. |
| Is subprocess isolation an OS sandbox? | No. It adds a timeout, isolated interpreter mode, temporary workspace, bounded output, and an empty environment, but it is not a container boundary. |
| Is IBM Bob actually running in the public app? | No. Session exports from the IDE build are in `bob_sessions/`; the public demo is a deterministic zero-key local path. |
| What makes the evidence trustworthy? | Candidate, baseline, validator, and runner hashes (now real, not placeholder) plus the real unified diff bind the verdict to inspected inputs and evaluator code. |
| What can fail during judging? | Public hosting or networking. The deterministic CLI and bundled fixture remain the fallback. |

---

### 9. Remaining human-in-the-loop items

1. Confirm the public GitHub repository and deployment through the account-authorized publishing flow before claiming public URLs in `README.md`.
2. Capture screenshots only from the verified public deployment (current screenshots in `bob_sessions/` are from local IDE, not deployed app).
3. Decide whether the visually checked one-page PDF also requires formal tagged-PDF accessibility remediation.

These items are deliberately unresolved rather than self-authorized or fabricated.
