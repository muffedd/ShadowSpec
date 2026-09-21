# Sol/Codex handoff - Bill's overnight review (2026-09-21/22, reconciled)

State of the tree: Sol's signed-off baseline (published as `a3ec485` on top of
snapshot `f922066`) plus Bill's ported unique fixes. Suite: 68 passed
(64 signed-off + 4 added here). Bill independently re-verified Sol's fixes with
the original reproduction probes before porting anything.

## Verified on Sol's signed-off tree (do not redo)

Bill re-ran the overnight reproduction probes against `a3ec485`:

1. **Validator subprocess controls** - all three bypasses closed: `os.write`
   fd-flood dies in <0.1s with a bounded "exceeded output limit" error; stderr
   flood likewise; a grandchild process is dead after the timeout kill
   (process-group SIGKILL + Linux subreaper reaping). The dedicated result-fd
   design removes the stdout-parsing channel entirely.
2. **Server-owned audit manifest** - a tampered fixture (one mutated variant
   byte) fails integrity with "audited fixture integrity check failed" before
   any execution. This control did not exist in Bill's fix; keep it.
3. **Tri-state UI** - a forced timeout renders "ERROR - validation did not
   complete, so no contract verdict was issued", metrics show NOT RUN, and the
   failed-checks area is labeled "Run issue". No REJECTED leakage.

## Ported from Bill's tree (unique fixes, fresh commits here)

1. **Analyzer bounded findings** (`src/shadowspec/analyzer.py`): a non-UTF-8
   file crashed the whole inventory with `UnicodeDecodeError`; it is now a
   bounded per-file finding. BOM-prefixed files (legal Python) parse via
   `utf-8-sig` instead of being misreported as syntax errors. Two regression
   tests.
2. **Dead compatibility API removed** (same file + `__init__.py`): uncalled
   `FunctionInfo` alias, mirror properties, module-level wrappers, unused
   `end_lineno`, undocumented single-colon matching form. Verified the
   signed-off suite does not reference any of it before removal.
3. **CTA theme pin** (`app.py`): the primary button lost the accent after
   Streamlit reruns (default red re-won the cascade); pinned with
   higher-specificity selectors. Verified on the pre-reconciliation tree with
   computed style `rgb(199, 255, 74)`; re-verified on this tree in the browser.
4. **Evidence risk list** (`src/shadowspec/service.py`): names candidate
   test-environment fingerprinting explicitly.

## Deliberately NOT ported (signed-off versions win)

- Bill's validator subprocess rewrite (file capture + RLIMIT_FSIZE): superseded
  by Sol's result-fd + selectors + subreaper design, which also adds the audit
  manifest.
- Bill's UI tri-state patch: Sol's is strictly richer (NOT RUN metrics, per-check
  listing, generic exception logging without detail leakage).
- Bill's blank "Changed files" rendering: Sol's evidence.py already renders it,
  with a baseline-specific message.

## Residual gaps (documented, not fixed here)

1. **CLI exit codes**: `cli.py` still maps a validation *error* to exit code 2,
   same as rejection (the UI distinguishes; the CLI does not). Bill's tree used
   exit 3 for errors; not ported to keep the signed-off surface intact. One-line
   change plus one test if the team wants it.
2. **TOCTOU re-read** (`service.py`): validation hashes a canonicalized copy,
   then the diff/analysis re-reads the file. The new audit manifest pins fixture
   hashes, which shrinks this to a between-calls swap; a one-assertion hash
   comparison closes it fully.
3. **No address-space limit on candidates**: output, wall time, and file writes
   are bounded; memory is not. A tuned RLIMIT_AS is deployment hardening.
4. **POSIX-only controls**: process-group kill/subreaper are POSIX (Linux-best);
   Windows degrades to direct-child kill. Output bounds hold everywhere.
5. **Evidence JSON `validation.output` truncation** at 4000 chars can cut the
   raw summary mid-token; labeled raw, not parsed downstream. Cosmetic.
6. **Submission assets**: deck/one-pager/screenshots predate the UI changes on
   both trees; recapture from the verified deployment (D12/D13).
7. **Pinned requirements**: Sol replaced the two-line requirements with
   pip-compile output (full transitive pins via `requirements.in`). Direct
   dependencies unchanged (streamlit; pytest/pytest-cov dev). Keep `.in` files
   as the edit surface; regenerate with pip-compile, never hand-edit the pins.

## Deployment / publication

- Public deployment (Streamlit Community Cloud) still needs the owner's auth;
  follow `docs/submission/deployment.md` and verify URLs before quoting them.
- IBM Bob session exports remain human-in-the-loop (D14); do not fabricate.
