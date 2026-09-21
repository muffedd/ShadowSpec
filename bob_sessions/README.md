# Bob session exports

This directory is the designated home for redacted IBM Bob session exports
when a real Bob IDE session is used during development or review. The
repository’s zero-key demo does not require a Bob session, does not call a
model, and must remain a separate deterministic local path.

## What to export

After the release reviewer completes its checklist, save the IDE-supported
transcript/export plus a small Markdown manifest containing:

- date and repository revision/source hash, when available;
- the five roles used and their handoff order;
- requested delta and explicit scope/non-goals;
- changed files and named fixture/scenario results;
- critic findings and bounded verdict (`accept`, `revise`, or `reject`);
- release evidence path and known limitations; and
- a statement that the zero-key demo was separate from live Bob inference.

The exact filename is intentionally simple and portable:

`YYYY-MM-DD-<short-topic>-<revision-or-run-id>.md`

If the IDE provides a native export, keep its original file alongside the
manifest when policy permits. The Markdown role files in `bob/` are guidance;
they are not declared to be an officially executable IBM Bob session format.

## Redaction checklist

Before saving or sharing an export, remove API keys, access tokens, cookies,
environment variables, private source, absolute host paths, personal data,
and unrelated transcript content. Do not paste secrets merely to explain that
they were used. Prefer a source hash and relative repository paths.

Do not include arbitrary fetched or uploaded source in an export. The hosted
demo is fixture-only and analysis-only for public URLs. Never describe the
temporary workspace and subprocess limits as an OS-level sandbox.

## Reviewability

An export should let a reviewer reconstruct the bounded decision without
trusting an undocumented prompt. Keep the mapper context, characterization
contract, implementer diff/report, critic findings, release checklist, and
raw-but-bounded test summaries linked or adjacent. If an export is incomplete,
label it as incomplete instead of implying a successful Bob run.

