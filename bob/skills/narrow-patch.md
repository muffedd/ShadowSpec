# Bob skill: narrow patch

## Purpose

Keep the implementer’s change proportional to the approved behavior delta.

## Procedure

- Restate the requested delta and preserved behaviors.
- Identify the smallest file/symbol change that can satisfy the acceptance
  scenario.
- Avoid unrelated refactors, dependency additions, formatting churn, and API
  changes.
- Run the relevant tests and report the exact bounded result.
- Hand the diff, test summary, risks, and rollback note to the critic.

## Guardrails

No arbitrary source execution, model/API-key requirement, or claim of an
OS-level sandbox may be introduced to make the demo pass.

