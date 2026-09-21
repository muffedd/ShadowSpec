"""ShadowSpec public Python API."""

from .analyzer import (
    AnalysisReport,
    CallEdge,
    FunctionRecord,
    SideEffectSignal,
    SyntaxErrorRecord,
    analyze_repository,
)

__all__ = [
    "AnalysisReport",
    "CallEdge",
    "FunctionRecord",
    "SideEffectSignal",
    "SyntaxErrorRecord",
    "analyze_repository",
]
