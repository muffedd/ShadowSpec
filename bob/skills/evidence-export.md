# Bob skill: evidence export

## Purpose

Produce reviewer-ready evidence and a redacted Bob session manifest without
coupling the zero-key demo to a live model session.

## Required fields

- repository revision/source hash, when available;
- role sequence and handoff summaries;
- intended delta and changed files;
- preserved behavior and acceptance results;
- risks, known limitations, reviewer findings, and rollback note; and
- raw test summaries with bounded output.

## Procedure

Export the final evidence only after the critic and release checks. Put actual
IBM Bob session exports under `bob_sessions/`, following its README. If the
IDE uses another export format, add a Markdown manifest with these fields;
do not invent a command syntax or imply that the repository can replay it.

## Redaction

Remove API keys, tokens, cookies, environment variables, private source,
absolute host paths, and unrelated transcript content. Keep the demo’s local
fixture results separate from any Bob transcript.

