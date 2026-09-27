# ShadowSpec

> **Event-window build — branch `bob-2.0-build-2026-09-25`.** Authored by IBM Bob starting after kickoff on 2026-09-25. The pre-kickoff state on `main` is reference-only. See [event-window provenance](docs/release/event-window-provenance.md).

**Reject the broad patch. Accept the narrow one. Export the proof.**

ShadowSpec is a zero-key evidence workbench for one risky maintenance job: changing undocumented legacy behavior without quietly changing something else.

The bundled demo asks for one precise change to a Python order service: accept surrounding whitespace in `SAVE10` while preserving case sensitivity, pricing, errors, and the SQLite audit write.

## Live demo

- **Live demo:** https://shadowspec-demo.pages.dev
- **Source:** https://github.com/muffedd/ShadowSpec

### Try it in 60 seconds

1. Open the live demo and run **Plausible bad candidate**. Verdict: REJECTED - the new whitespace case passes, but lowercase `save10` behavior changed.
2. Run **Narrow candidate**. Verdict: ACCEPTED - preserved behavior and the requested delta both pass.
3. Open the evidence drawer to see the diff, provenance hashes, and export a condensed preview.

| Build proof | |
| --- | --- |
| Tests | 76 passed, 3 platform-gated skips |
| Coverage | 91.46% (CI enforces >= 85%) |
| IBM Bob sessions | 6 exported task transcripts + 6 consumption screenshots in [`bob_sessions/`](bob_sessions/) |


## Problem

Legacy maintenance fails when a patch satisfies the new request but silently changes an old contract. Reviewers need executable evidence of both the intended delta and the behavior that must remain unchanged.

## Three-minute golden path

1. Run **Plausible bad candidate**. It trims and uppercases the code, so the new example passes but lowercase behavior changes. ShadowSpec rejects it.
2. Run **Narrow candidate**. It trims surrounding whitespace only. Characterization and acceptance checks pass.
3. Download the Markdown or JSON evidence pack containing the real diff, provenance hashes, named checks, risks, reviewer checklist, and rollback notes.

## Expected proof

| Candidate | Characterization | New acceptance check | Verdict |
| --- | --- | --- | --- |
| Baseline | Pass | Fail | Rejected: request not implemented |
| Bad: `strip().upper()` | Fail | Pass | Rejected: lowercase behavior changed |
| Narrow: `strip()` | Pass | Pass | Accepted for the named fixtures |

ShadowSpec never treats “the new example works” as sufficient evidence. Existing observations and the requested delta are tested separately.

## Setup

Requires Python 3.12 or later.

The pinned install below requires Python 3.12 or later. The engine itself is
standard-library only: to run just the core test suite without the full pinned
install, `pip install pytest pytest-cov` is enough (`tests/test_app.py` needs
Streamlit and `tests/test_deployment.py` needs Python 3.11+; both are
platform-gated).

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -q
streamlit run app.py
```

`requirements.in` and `requirements-dev.in` are the small direct-dependency
inputs. The corresponding `.txt` files pin the complete Python 3.12 dependency
graphs consumed by deployment and CI.

The `app.py` entry point adds the repository's `src/` directory before importing
the application package, so this launch works after a dependencies-only install
without setting `PYTHONPATH`. Keep the bundled `fixtures/legacy_orders` directory
alongside `app.py` in deployments.

The CLI is intentionally a source-checkout command because it consumes the
repository-level audited fixture. The distribution does not install a
`shadowspec` console script.

```bash
PYTHONPATH=src python -m shadowspec.cli run bad --format markdown
PYTHONPATH=src python -m shadowspec.cli run narrow --format json
```

## Architecture

```mermaid
flowchart TD
    A[Audited legacy fixture] --> B[AST behavior mapper]
    B --> C[Characterization contract]
    C --> D[Prepared candidate]
    D --> E[Differential validator]
    E --> F{Preserved and requested behavior pass?}
    F -->|No| G[Rejected with failed checks]
    F -->|Yes| H[Accepted within named fixtures]
    G --> I[Markdown and JSON evidence]
    H --> I
```

The analyzer never imports repository code. It inventories Python files, functions, static calls, syntax failures, and side-effect signals. The validator only executes three server-owned audited variants in per-run temporary directories with a timeout, bounded output, and an empty explicit environment.

These controls are not an OS-level sandbox. The hosted demo does not execute arbitrary uploaded or fetched repositories.

## Workflow guidance for IBM Bob

ShadowSpec includes repository guidance for five Bob roles:

1. Mapper
2. Characterization-test designer
3. Implementer
4. Critic/security reviewer
5. Release reviewer

The checked-in Markdown files propose a full-repository, actor-critic handoff for
use in an IBM Bob IDE. They are workflow guidance, not evidence that Bob performed
this build. See [AGENTS.md](AGENTS.md), [Bob workflow](docs/architecture/bob-workflow.md),
and the role contracts under [`bob/`](bob/).

Bob session exports from the `bob-2.0-build-2026-09-25` build are in
[`bob_sessions/`](bob_sessions/). These are redacted task-history exports from
the IBM Bob IDE sessions that authored this branch. The public zero-key demo
performs deterministic local analysis and does not impersonate live Bob inference.

## Evidence pack

Each run exports:

- changed files and source SHA-256
- intended behavior delta
- named preserved behavior
- static analysis and limitations
- failed checks and raw normalized summary
- reviewer checklist
- risks and rollback notes

## Security boundary

- Bundled fixture execution only
- No arbitrary uploads, dependency installation, or fetched-code execution
- Candidate allowlist checked before file access
- Immutable server-owned SHA-256 manifest checked for the baseline and selected
  candidate before subprocess launch; these audited hashes are the
  verdict-integrity boundary
- Repository paths constrained beneath a fixed root, including symlink checks
- Per-run temporary directory, three-second timeout, bounded output
- No secrets passed explicitly to the validation subprocess
- These application controls are not an OS-level sandbox
- No autonomous merge or deployment

See [security.md](docs/submission/security.md) for the threat boundary and limitations.

## Tests

```bash
pytest -q --cov=shadowspec --cov-report=term --cov-fail-under=85
```

Verified reference baseline: **76 tests passed, 3 platform-gated skips, 91.46% coverage**. CI enforces at least 85% coverage.

## Demo and submission

- Live demo: https://shadowspec-demo.pages.dev
- GitHub repository: https://github.com/muffedd/ShadowSpec
- Demo video: `VIDEO_URL_PENDING`

## Submission materials

- [Hackathon slide deck](assets/submission/ShadowSpec-Hackathon-Deck.pptx)
- [One-page project brief](assets/submission/ShadowSpec-One-Page.pdf)
- [Under-three-minute demo script](docs/submission/demo-script.md)
- [Judge pitch](docs/submission/judge-pitch.md)
- [Submission copy](docs/submission/submission-copy.md)
- [Decision log](docs/submission/decision-log.md)
- [Deployment guide](docs/submission/deployment.md)
- [Winner-pattern research](docs/research/winner-pattern-report.md)

## Scope limits

An accepted result means that the named observations passed for the audited fixture, together with the requested acceptance check. It does not prove semantic equivalence, complete dynamic-call coverage, or production safety for an arbitrary codebase.

## Bob-native behavior gate

IBM Bob can load the project skill at [`.bob/skills/shadowspec-behavior-gate/SKILL.md`](.bob/skills/shadowspec-behavior-gate/SKILL.md) in **Advanced mode**. Ask Bob to review the SAVE10 bad and narrow candidates with that skill. The skill directs Bob to invoke the actual checked-in ShadowSpec CLI, not to infer a result from instructions. Bob may ask to approve the skill unless Skills auto-approval is enabled. The rejected CLI exits with code 2 while still emitting JSON evidence; narrow exits 0.

This is a repo-local Bob instruction integration, not a claim that the public demo performs Bob inference or that arbitrary patches can be validated. Until a real Bob session export showing both CLI calls lands in [`bob_sessions/`](bob_sessions/), the repository proves the skill definition and locally tested CLI, **not** that Bob ran this new workflow. Bob's [Skills documentation](https://bob.ibm.com/docs/ide/features/skills) describes the `.bob/skills/<name>/SKILL.md` convention and Advanced-mode requirement.

### Optional Bob MCP tool (local only)

For a direct Bob tool call rather than a skill-driven terminal call, install `pip install -r requirements-mcp.in` in the project's Python 3.12 environment. Configure Bob's **project** `.bob/mcp.json` on your machine as below, replacing both absolute paths with the path to your own checkout (and using `.venv\\Scripts\\python.exe` on Windows). Do not commit a machine-specific absolute path or put secrets in this configuration:

```json
{
  "mcpServers": {
    "shadowspec": {
      "command": "C:\\path\\to\\ShadowSpec\\.venv\\Scripts\\python.exe",
      "args": ["-m", "shadowspec.bob_mcp"],
      "cwd": "C:\\path\\to\\ShadowSpec",
      "env": {"PYTHONPATH": "src"}
    }
  }
}
```

Reload the MCP servers in Bob, enable **Use MCP Servers**, then ask Bob to call `validate_fixture` twice, with `candidate` values `bad` and `narrow`. This adapter invokes the actual CLI in a bounded local subprocess and returns named checks and provenance. It accepts only the three integrity-checked bundled fixtures, does not open network access, and does not auto-merge. If Bob does not discover the tool, report that setup failure rather than describing an unobserved Bob run. Bob's [MCP configuration documentation](https://bob.ibm.com/docs/ide/configuration/mcp/mcp-in-bob) describes project `.bob/mcp.json`, STDIO transport, and the MCP settings toggle.


## License

[MIT](LICENSE) © 2026 Sutharshan Kanthakumar. Dependency licenses are unchanged.
