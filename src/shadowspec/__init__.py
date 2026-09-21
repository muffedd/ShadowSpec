"""ShadowSpec public Python API."""

from .analyzer import (
    AnalysisReport,
    CallEdge,
    FunctionInfo,
    FunctionRecord,
    SideEffectSignal,
    SyntaxErrorRecord,
    analyze_repository,
    blast_radius,
    reachable_functions,
)

__all__ = [
    "AnalysisReport",
    "CallEdge",
    "FunctionInfo",
    "FunctionRecord",
    "SideEffectSignal",
    "SyntaxErrorRecord",
    "analyze_repository",
    "blast_radius",
    "reachable_functions",
]
