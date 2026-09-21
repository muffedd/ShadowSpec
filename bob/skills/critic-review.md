# Bob skill: actor-critic review

## Purpose

Make the critic an independent adversary rather than a restatement of the
implementer’s success report.

## Procedure

- Re-read the original context and contract before reading the conclusion.
- Inspect the complete diff and test evidence.
- Try preserved-behavior regressions, over-broad interpretations, and
  boundary failures involving paths, URLs, timeouts, and output limits.
- Check that zero-key demo behavior is clearly separated from live Bob
  inference.
- Report severity, evidence, impact, and a minimal correction; then issue a
  bounded `accept`, `revise`, or `reject` verdict.

## Guardrails

Review findings must be tied to the named fixture and evidence. Never claim
that passing the demo proves general security or semantic equivalence.

