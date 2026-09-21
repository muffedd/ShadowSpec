"""Application orchestration."""

from difflib import unified_diff
from dataclasses import dataclass
from pathlib import Path

from shadowspec.analyzer import analyze_repository
from shadowspec.evidence import EvidenceInput, render_json, render_markdown
from shadowspec.validator import ValidationRun, validate_candidate


FIXTURE_ROOT = Path(__file__).parents[2] / "fixtures" / "legacy_orders"


@dataclass(frozen=True)
class DemoResult:
    candidate: str
    changed_files: tuple[str, ...]
    analysis: dict[str, object]
    validation: ValidationRun
    evidence_markdown: str
    evidence_json: str


def run_demo(candidate: str) -> DemoResult:
    # Validate the selected fixture before reading it.  The analyzer receives
    # an explicit file selection so evidence cannot accidentally include calls
    # from the other prepared variants.
    validation = validate_candidate(candidate, FIXTURE_ROOT)
    candidate_relative = f"variants/{candidate}.py"
    baseline_relative = "variants/baseline.py"
    candidate_path = FIXTURE_ROOT / candidate_relative
    baseline_path = FIXTURE_ROOT / baseline_relative
    candidate_source = candidate_path.read_text(encoding="utf-8")
    baseline_source = baseline_path.read_text(encoding="utf-8")
    diff = "".join(
        unified_diff(
            baseline_source.splitlines(keepends=True),
            candidate_source.splitlines(keepends=True),
            fromfile="baseline.py",
            tofile=f"{candidate}.py",
        )
    )
    report = analyze_repository(
        FIXTURE_ROOT,
        allowed_root=FIXTURE_ROOT,
        selected_files=(candidate_relative,),
    )
    changed_files = (
        (f"fixtures/legacy_orders/{candidate_relative}",)
        if diff
        else ()
    )
    analysis: dict[str, object] = {
        "file_count": len(report.files),
        "files": report.files,
        "functions": sorted({item.name for item in report.functions}),
        "call_edges": [f"{edge.caller} -> {edge.callee}" for edge in report.call_edges],
        "side_effects": sorted({item.kind for item in report.side_effect_signals}),
        "syntax_errors": [item.path for item in report.syntax_errors],
        "limitations": report.dynamic_dispatch_limitations,
        "blast_radius": sorted(report.blast_radius("process_order")),
        "diff": diff,
        "baseline_file": baseline_relative,
        "candidate_file": candidate_relative,
        "provenance": validation.provenance,
    }
    evidence_input = EvidenceInput(
        request="Accept surrounding whitespace in discount codes.",
        changed_files=changed_files,
        intended_delta="Trim surrounding whitespace only; preserve case sensitivity.",
        preserved_behavior=(
            "Exact uppercase SAVE10 receives the 10% discount.",
            "Lowercase save10 remains invalid.",
            "Unknown codes remain full price.",
            "The SQLite audit row preserves the observed input code and total.",
        ),
        risks=(
            "The verdict is scoped to named fixtures and does not prove semantic equivalence.",
            "Static AST analysis does not resolve dynamic dispatch or runtime imports.",
            "Temporary workspaces and timeouts are not an OS-level security sandbox.",
            "A candidate can detect the test environment and behave only under test; the verdict covers observed runs.",
        ),
        reviewer_checklist=(
            "Confirm lowercase codes remain invalid.",
            "Confirm the audit row still stores the original code.",
            "Review the exact one-line normalization change.",
        ),
        rollback_notes="Restore the baseline variant and rerun the full validation matrix.",
        analysis=analysis,
        validation=validation,
    )
    return DemoResult(
        candidate=candidate,
        changed_files=changed_files,
        analysis=analysis,
        validation=validation,
        evidence_markdown=render_markdown(evidence_input),
        evidence_json=render_json(evidence_input),
    )
