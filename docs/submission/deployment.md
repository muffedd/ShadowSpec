# ShadowSpec deployment guide

## Deployment shape

ShadowSpec is a zero-key Python application with a Streamlit judge UI. The UI and
CLI consume the same orchestration API, so a deployed demo and a local invocation
share the deterministic service behavior. The deployment entry point is
`app.py`.

## Preconditions

- Install the project’s declared Python dependencies (the application entry
  point is runnable without installing the package itself):

  ```bash
  pip install -r requirements.txt
  ```

- `requirements.txt` pins the complete Python 3.12 runtime dependency graph.
  `requirements.in` remains the small, human-maintained input used to regenerate
  that file with the free `pip-tools` package:

  ```bash
  python -m pip install pip-tools==7.6.1
  python -m piptools compile --resolver=backtracking --strip-extras --output-file=requirements.txt requirements.in
  ```

- Run the entry point from the repository checkout so its `src/` package and
  bundled fixture are present.
- Start from the audited bundled fixture included with the project.
- No API key is required for the public demo.
- Keep the fixture and its prepared candidate variants available to the runtime.

## Launch checklist

1. Install the project dependencies in the deployment environment.
2. From the repository root, launch the Streamlit entry point with
   `streamlit run app.py`. `app.py` adds the local `src/` directory to the
   import path, so no `PYTHONPATH` setting or editable package install is
   required.
3. If command-line evidence is needed, run the source-checkout CLI explicitly:

   ```bash
   PYTHONPATH=src python -m shadowspec.cli run narrow --format json
   ```

   The package intentionally installs no `shadowspec` console script: the CLI
   depends on the repository-level audited fixture, which is not part of the
   wheel.
4. Exercise the golden path: baseline characterization, bad-candidate rejection,
   narrow-candidate acceptance, and evidence export.
5. Confirm that the UI exposes clear run IDs, source hashes, verdicts, and
   actionable errors.
6. Verify that the demo remains bounded to the bundled fixture and that no
   unverified public URL is advertised.

## Runtime boundary

Hosted execution is bundled-fixture-only. Public GitHub URLs, if exposed, must be
validated and analysis-only. Uploaded or fetched code must not be imported,
installed, or executed. Paths are canonicalized beneath a fixed root. An
immutable server-owned SHA-256 manifest pins the exact bundled `baseline.py`,
`bad.py`, and `narrow.py` bytes; validation compares the baseline and selected
candidate before launching a subprocess and returns an integrity error on any
mismatch. Those hashes are the verdict-integrity boundary, not an OS sandbox.
Validation subprocesses additionally use a timeout, bounded output, a temporary
working directory, and no secrets passed explicitly. Do not describe these
controls as OS-level sandboxing.

## Release evidence

Before publishing a deployment, use the evidence export to confirm source hashes,
changed files, intended delta, preserved behavior, risks, reviewer checklist,
rollback notes, and raw test summaries are present. The release-reviewer Bob
artifact should connect this evidence to the behavior map, tests, and patch.

## Honest publication notes

This guide intentionally contains no live demo URL or GitHub URL. Add public links
only after they have been verified. The zero-key public demo performs deterministic
local analysis; it does not claim unavailable live IBM Bob inference. If a workflow
is actually run in the IBM Bob IDE, place exported Bob sessions in `bob_sessions/`.
