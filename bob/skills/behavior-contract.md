# Bob skill: behavior contract

## Purpose

Translate the requested maintenance change into deterministic observations that
separate preserved behavior from the new acceptance behavior.

## Procedure

- Name inputs, outputs, exceptions, persistence effects, and relevant side
  effects.
- Keep characterization scenarios unchanged as the preservation contract.
- Add a separate acceptance scenario for the requested delta.
- Include the plausible over-broad behavior when it proves a regression.
- State what the scenarios do not prove.

## Guardrails

Do not infer universal equivalence from named fixtures. Do not change an
assertion merely to accept a candidate. Record lower-confidence observations
as limitations.

