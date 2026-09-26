#!/usr/bin/env bash
# scripts/check-behavior-gate.sh
#
# Local demo of the behavior gate.
# Shows the gate FAILING (red) on the known-bad patch and PASSING (green)
# on the narrow patch — same logic the CI workflow runs.
#
# Usage (from repo root):
#   bash scripts/check-behavior-gate.sh
#
# Expected output:
#   [1/2] Negative control — bad patch (strip().upper()) ...
#   verdict              : rejected
#   characterization_passed : False
#   acceptance_passed    : True
#   failed_checks        : ['lowercase code remains invalid ...']
#   ✓ GATE BITES: bad patch correctly REJECTED
#
#   [2/2] Positive control — narrow patch (strip() only) ...
#   verdict              : accepted
#   characterization_passed : True
#   acceptance_passed    : True
#   failed_checks        : []
#   ✓ GATE PASSES: narrow patch correctly ACCEPTED
#
# Exit codes:
#   0 — both controls behaved as expected (gate is working)
#   1 — a control produced an unexpected result (gate may be broken)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PYTHON="${PYTHON:-python}"
export PYTHONPATH="src"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RESET='\033[0m'

fail() { echo -e "${RED}FAIL: $*${RESET}" >&2; exit 1; }
pass() { echo -e "${GREEN}$*${RESET}"; }
info() { echo -e "${YELLOW}$*${RESET}"; }

# ---------------------------------------------------------------------------
# 1. Negative control — bad patch MUST be rejected
# ---------------------------------------------------------------------------
info "[1/2] Negative control — bad patch (strip().upper()) ..."
echo ""

# CLI exits 2 for rejected, so capture output without aborting on non-zero.
BAD_JSON=$($PYTHON -m shadowspec.cli run bad --format json 2>/dev/null || true)

echo "$BAD_JSON" | $PYTHON -c '
import json, sys
data  = json.load(sys.stdin)
v     = data["validation"]
print(f"  verdict              : {v[\"verdict\"]}")
print(f"  characterization_passed : {v[\"characterization_passed\"]}")
print(f"  acceptance_passed    : {v[\"acceptance_passed\"]}")
print(f"  failed_checks        : {v[\"failed_checks\"]}")
'

echo "$BAD_JSON" | $PYTHON -c '
import json, sys
data = json.load(sys.stdin)
v    = data["validation"]
assert v["verdict"]                == "rejected", f"verdict={v[\"verdict\"]!r}"
assert v["characterization_passed"] is False,     "characterization_passed should be False"
assert v["acceptance_passed"]       is True,      "acceptance_passed should be True"
lowcase_check = "lowercase code remains invalid with complete pricing result and audit row"
assert lowcase_check in v["failed_checks"], f"Expected \"{lowcase_check}\" in failed_checks"
' || fail "Negative control: expected bad patch to be rejected"

echo ""
pass "✓ GATE BITES: bad patch correctly REJECTED (characterization failure surfaced)"
echo ""

# ---------------------------------------------------------------------------
# 2. Positive control — narrow patch MUST be accepted
# ---------------------------------------------------------------------------
info "[2/2] Positive control — narrow patch (strip() only) ..."
echo ""

NARROW_JSON=$($PYTHON -m shadowspec.cli run narrow --format json)

echo "$NARROW_JSON" | $PYTHON -c '
import json, sys
data  = json.load(sys.stdin)
v     = data["validation"]
print(f"  verdict              : {v[\"verdict\"]}")
print(f"  characterization_passed : {v[\"characterization_passed\"]}")
print(f"  acceptance_passed    : {v[\"acceptance_passed\"]}")
print(f"  failed_checks        : {v[\"failed_checks\"]}")
'

echo "$NARROW_JSON" | $PYTHON -c '
import json, sys
data = json.load(sys.stdin)
v    = data["validation"]
assert v["verdict"]                == "accepted", f"verdict={v[\"verdict\"]!r}"
assert v["characterization_passed"] is True,      "characterization_passed should be True"
assert v["acceptance_passed"]       is True,      "acceptance_passed should be True"
assert v["failed_checks"]           == [],         f"expected no failed checks, got {v[\"failed_checks\"]}"
' || fail "Positive control: expected narrow patch to be accepted"

echo ""
pass "✓ GATE PASSES: narrow patch correctly ACCEPTED"
echo ""

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo "────────────────────────────────────────────────"
echo " Candidate          Characterization  Verdict"
echo "────────────────────────────────────────────────"
echo -e " bad  (strip().upper())   ${RED}FAIL${RESET}           ${RED}REJECTED${RESET}"
echo -e " narrow (strip() only)    ${GREEN}PASS${RESET}           ${GREEN}ACCEPTED${RESET}"
echo "────────────────────────────────────────────────"
echo ""
pass "Behavior gate is working correctly."
