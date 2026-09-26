# Enabling branch protection for the behavior gate

This document explains how to configure GitHub branch protection so that the
`ShadowSpec behavior gate` CI check **must pass before any pull request can be
merged to `main`**.

## What the workflow actually proves

The `behavior-gate` workflow runs two controls on every PR to `main`:

1. **Negative control** — always expected to be green. Confirms the engine
   correctly rejects the known-bad `strip().upper()` candidate.
2. **Positive control + characterization gate** — runs the audited `narrow`
   fixture and fails if `characterization_passed` is `False`.

It also reports the list of files changed in the PR so reviewers can see what
is in scope.

**What is and is not proven:**

- ✅ The gate mechanism is live and will reject a regression to the audited narrow fixture.
- ✅ Any PR that breaks `characterization_passed` on the narrow fixture will fail CI.
- ❌ The workflow does not automatically block an arbitrary bad PR from an external
  contributor unless branch protection is enabled and the status check is required.
  The `strip().upper()` negative control is always green because it proves the gate
  can detect that class of regression — it does not block the merge on its own.

Once branch protection is configured:

* Any PR that changes the gate-protected fixture in a way that breaks
  `characterization_passed` **cannot be merged** — the required status check
  blocks the Merge button.
* A PR that passes all characterization checks and the acceptance check clears
  the gate and can be merged normally.

---

## Prerequisites

* You are a repository owner or admin on `github.com/muffedd/ShadowSpec`.
* The `behavior-gate.yml` workflow has been pushed to the default branch (or to
  at least one branch where a pull request has triggered it, so GitHub has seen
  the check name).

---

## Step-by-step: GitHub web UI

### 1. Open the branch-protection settings

1. Go to **Settings → Branches** in the repository.
2. Under **Branch protection rules**, click **Add rule** (or **Edit** if a rule
   for `main` already exists).
3. In **Branch name pattern**, enter `main`.

### 2. Enable "Require status checks to pass before merging"

Check the box labelled:

> ☑ Require status checks to pass before merging

This reveals a search box.

### 3. Add the two required checks

Search for and add **both** of these status-check names:

| Status check name | Job in workflow |
|---|---|
| `pytest + coverage` | `test` |
| `ShadowSpec behavior gate` | `behavior-gate` |

> **Tip:** The check names appear exactly as the `name:` field of each job in
> `.github/workflows/behavior-gate.yml`. If they don't appear in the dropdown
> yet, open a draft PR from any branch — that triggers the workflow and
> registers the names.

### 4. (Recommended) Enable strict mode

Check:

> ☑ Require branches to be up to date before merging

This prevents a PR from being merged if `main` has moved ahead and invalidated
the gate run.

### 5. (Recommended) Require a passing run, not just a passing job

Also check:

> ☑ Require conversation resolution before merging

This is not strictly about the behavior gate, but it prevents a reviewer from
approving a PR while a gate discussion is still open.

### 6. Save the rule

Click **Create** (or **Save changes**).

---

## Verification

1. Open a pull request that contains the bad patch
   (`fixtures/legacy_orders/variants/bad.py` with `strip().upper()`).
2. The `ShadowSpec behavior gate` check should appear as **❌ failing**.
3. The **Merge pull request** button should be greyed out with the message
   *"Required status checks must pass before merging."*
4. Switch the PR to use the narrow patch (`strip()` only).
5. The check should turn **✅ passing** and the merge button becomes active.

---

## GitHub CLI equivalent

```bash
gh api repos/muffedd/ShadowSpec/branches/main/protection \
  --method PUT \
  --header "Accept: application/vnd.github+json" \
  --field required_status_checks='{"strict":true,"contexts":["pytest + coverage","ShadowSpec behavior gate"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews=null \
  --field restrictions=null
```

> **Note:** `enforce_admins=true` means repository admins cannot bypass the
> gate either. Set to `false` if you need an emergency override path.

---

## What the gate checks

The `behavior-gate` job runs three steps on every PR:

### Step 1 — Changed files report
Derives the list of files changed in the PR from the git diff between the PR
head and the base branch merge-base. This is reported in the CI log so reviewers
can verify what is in scope.

### Step 2 — Negative control (always expected green)
Runs `shadowspec.cli run bad` and asserts:
- `characterization_passed == False`
- `acceptance_passed == True`
- `verdict == "rejected"`

This step **always passes** in CI. Its purpose is to confirm the gate mechanism
is alive and can detect the known regression. It is not a gate on the PR itself.

### Step 3 — Positive control — narrow patch
Runs `shadowspec.cli run narrow` and asserts:
- `characterization_passed == True`
- `acceptance_passed == True`
- `verdict == "accepted"`

### Step 4 — Characterization gate (the blocking step)
Runs `shadowspec.cli run narrow` and exits `1` if `characterization_passed` is
`False`. **This is the step that branch protection should require to be green.**

> **Scope note:** This gate proves the audited `narrow` fixture passes. It does
> not automatically evaluate arbitrary contributor patches. To block bad merges,
> branch protection must be enabled as described above.

---

## Local verification

Run the demo script from the repository root:

```bash
bash scripts/check-behavior-gate.sh
```

Expected output:

```
[1/2] Negative control — bad patch (strip().upper()) ...
  verdict              : rejected
  characterization_passed : False
  acceptance_passed    : True
  failed_checks        : ['lowercase code remains invalid ...']
✓ GATE BITES: bad patch correctly REJECTED

[2/2] Positive control — narrow patch (strip() only) ...
  verdict              : accepted
  characterization_passed : True
  acceptance_passed    : True
  failed_checks        : []
✓ GATE PASSES: narrow patch correctly ACCEPTED
```

Or run only the gate tests:

```bash
pytest tests/test_behavior_gate.py -v
```

---

## How the gate interacts with the validator's separation rule

The validator enforces a strict separation between preserved behavior
(characterization) and the requested change (acceptance):

| Patch | Characterization | Acceptance | Gate |
|---|---|---|---|
| Baseline (no change) | ✅ pass | ❌ fail | ❌ BLOCKED — request not implemented |
| `strip().upper()` | ❌ **fail** | ✅ pass | ❌ BLOCKED — silently changed lowercase behavior |
| `strip()` only | ✅ pass | ✅ pass | ✅ ALLOWED |

A patch that satisfies the acceptance check but silently regresses any
characterization check is **always rejected**, regardless of whether the
regression was intentional.
