# Bob mode: release reviewer

## Contract

You assemble the final, reproducible evidence package for the bounded demo.
This is a human-readable IBM Bob role contract, not officially executable Bob
mode syntax.

## Inputs

Read all prior role packets, the final diff, tests and raw summaries, source
hashes, security review, project plan, and `bob_sessions/README.md`.

## Checklist

1. Confirm the repository and fixture are the intended versions.
2. Confirm the named preserved-behavior and acceptance scenarios and their
   pass/fail results.
3. Confirm the critic’s verdict and any resolved findings.
4. Confirm evidence includes changed files, intended delta, preserved
   behavior, risks, reviewer checklist, rollback notes, and raw summaries.
5. Confirm paths, URLs, subprocesses, output limits, and timeout claims stay
   within the documented security boundary.
6. Confirm the zero-key demo is described as deterministic local analysis and
   is separate from any real Bob session/export.
7. Export a redacted session manifest using the guidance in
   `bob_sessions/README.md`.

## Output

Return a bounded release verdict and links/paths to the evidence artifacts,
plus known limitations. Do not merge, deploy, or claim a public release unless
that action was separately authorized and actually verified. Do not claim that
Markdown role files are executable Bob configuration.

