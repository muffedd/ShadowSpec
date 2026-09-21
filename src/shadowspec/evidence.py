"""Reviewer evidence rendering."""

import json
from dataclasses import asdict, dataclass
from typing import Any

from shadowspec.validator import ValidationRun


@dataclass(frozen=True)
class EvidenceInput:
    request: str
    changed_files: tuple[str, ...]
    intended_delta: str
    preserved_behavior: tuple[str, ...]
    risks: tuple[str, ...]
    reviewer_checklist: tuple[str, ...]
    rollback_notes: str
    analysis: dict[str, Any]
    validation: ValidationRun


def render_markdown(evidence):
    validation = evidence.validation
    bullets = lambda values: "\n".join(f"- {value}" for value in values)
    analysis = json.dumps(evidence.analysis, indent=2, sort_keys=True)
    provenance = json.dumps(validation.provenance, indent=2, sort_keys=True)
    return f"""# ShadowSpec evidence pack

**Run ID:** `{validation.run_id}`  
**Candidate:** `{validation.candidate}`  
**Verdict:** **{validation.verdict.upper()}**  
**Source SHA-256:** `{validation.source_sha256}`<br>
**Baseline SHA-256:** `{validation.baseline_sha256}`<br>
**Validator SHA-256:** `{validation.validator_sha256}`<br>
**Runner SHA-256:** `{validation.runner_sha256}`

## Provenance

```json
{provenance}
```

## Maintenance request

{evidence.request}

## Intended behavior delta

{evidence.intended_delta}

## Preserved behavior

{bullets(evidence.preserved_behavior)}

## Changed files

{bullets(evidence.changed_files)}

## Static analysis

```json
{analysis}
```

## Risks

{bullets(evidence.risks)}

## Reviewer checklist

{bullets(evidence.reviewer_checklist)}

## Rollback notes

{evidence.rollback_notes}

## Raw validation summary

```json
{validation.output}
```
"""


def render_json(evidence):
    payload = {
        "schema_version": "1.0",
        "request": evidence.request,
        "changed_files": list(evidence.changed_files),
        "intended_delta": evidence.intended_delta,
        "preserved_behavior": list(evidence.preserved_behavior),
        "analysis": evidence.analysis,
        "risks": list(evidence.risks),
        "reviewer_checklist": list(evidence.reviewer_checklist),
        "rollback_notes": evidence.rollback_notes,
        "validation": asdict(evidence.validation),
        "provenance": evidence.validation.provenance,
    }
    return json.dumps(payload, indent=2, sort_keys=True)
