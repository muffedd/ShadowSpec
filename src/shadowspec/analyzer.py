"""Small, bounded AST inventory for Python repositories.

The analyzer deliberately reports a conservative, static view.  It never
imports or executes the files it reads, and its call graph does not attempt to
resolve reflection, callbacks, or other runtime dispatch.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class FunctionRecord:
    """A function definition discovered in a Python source file."""

    name: str
    path: str
    lineno: int
    qualified_name: str | None = None

    def __post_init__(self) -> None:
        if self.qualified_name is None:
            object.__setattr__(self, "qualified_name", f"{self.path}::{self.name}")


@dataclass(frozen=True)
class CallEdge:
    """A syntactic call from one function (or module scope) to an expression."""

    caller: str
    callee: str
    path: str
    lineno: int
    caller_qualified: str | None = None
    callee_qualified: str | None = None


@dataclass(frozen=True)
class SideEffectSignal:
    """A static signal for an operation that can affect external state."""

    kind: str
    path: str
    lineno: int
    function: str | None = None
    detail: str | None = None


@dataclass(frozen=True)
class SyntaxErrorRecord:
    """A parse failure that did not prevent analysis of other files."""

    path: str
    message: str
    lineno: int | None = None
    offset: int | None = None


@dataclass
class AnalysisReport:
    """The bounded inventory produced by :func:`analyze_repository`."""

    files: list[str] = field(default_factory=list)
    functions: list[FunctionRecord] = field(default_factory=list)
    call_edges: list[CallEdge] = field(default_factory=list)
    side_effect_signals: list[SideEffectSignal] = field(default_factory=list)
    syntax_errors: list[SyntaxErrorRecord] = field(default_factory=list)
    dynamic_dispatch_limitations: list[str] = field(default_factory=list)

    def reachable_from(self, function: str) -> set[str]:
        """Return local function names reachable through static call edges.

        ``function`` may be a short function name or its ``path::name``
        qualified name.  The result intentionally contains only names, which
        keeps this small graph convenient for a UI while the records retain
        source locations for review.
        """

        starts = {
            record.qualified_name
            for record in self.functions
            if function in {record.name, record.qualified_name}
        }
        if not starts:
            return set()

        adjacency: dict[str, set[str]] = {}
        for edge in self.call_edges:
            if edge.caller_qualified and edge.callee_qualified:
                adjacency.setdefault(edge.caller_qualified, set()).add(edge.callee_qualified)

        seen: set[str] = set()
        pending = list(starts)
        while pending:
            caller = pending.pop()
            for target in adjacency.get(caller, ()):
                if target not in seen and target not in starts:
                    seen.add(target)
                    pending.append(target)

        names = {record.qualified_name: record.name for record in self.functions}
        return {names[qualified] for qualified in seen if qualified in names}

    def blast_radius(self, function: str) -> set[str]:
        """Return the statically reachable local functions for ``function``."""

        return self.reachable_from(function)


_NETWORK_MODULES = {"requests", "urllib", "http", "httpx", "aiohttp", "socket"}
_SUBPROCESS_CALLS = {"run", "Popen", "call", "check_call", "check_output", "communicate"}


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return None


def _root_module(name: str) -> str:
    return name.split(".", 1)[0]


class _InventoryVisitor(ast.NodeVisitor):
    def __init__(self, path: str) -> None:
        self.path = path
        self.functions: list[FunctionRecord] = []
        self.call_edges: list[CallEdge] = []
        self.side_effect_signals: list[SideEffectSignal] = []
        self._function_stack: list[FunctionRecord] = []

    @property
    def _current_function(self) -> FunctionRecord | None:
        return self._function_stack[-1] if self._function_stack else None

    def _signal(self, kind: str, node: ast.AST, detail: str | None = None) -> None:
        function = self._current_function
        self.side_effect_signals.append(
            SideEffectSignal(
                kind=kind,
                path=self.path,
                lineno=getattr(node, "lineno", 0),
                function=function.qualified_name if function else None,
                detail=detail,
            )
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        parent = self._current_function
        qualified = f"{self.path}::{node.name}"
        if parent:
            qualified = f"{parent.qualified_name}.{node.name}"
        record = FunctionRecord(
            name=node.name,
            path=self.path,
            lineno=node.lineno,
            qualified_name=qualified,
        )
        self.functions.append(record)
        self._function_stack.append(record)
        for statement in node.body:
            self.visit(statement)
        self._function_stack.pop()

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            module = alias.name
            self._signal("import", node, module)
            root = _root_module(module)
            if root == "sqlite3":
                self._signal("sqlite", node, module)
            elif root in _NETWORK_MODULES:
                self._signal("network", node, module)
            elif root == "subprocess":
                self._signal("subprocess", node, module)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        self._signal("import", node, module)
        root = _root_module(module)
        if root == "sqlite3":
            self._signal("sqlite", node, module)
        elif root in _NETWORK_MODULES:
            self._signal("network", node, module)
        elif root == "subprocess":
            self._signal("subprocess", node, module)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        callee = _dotted_name(node.func) or "<dynamic>"
        function = self._current_function
        caller = function.name if function else "<module>"
        caller_qualified = function.qualified_name if function else None
        self.call_edges.append(
            CallEdge(
                caller=caller,
                callee=callee,
                path=self.path,
                lineno=node.lineno,
                caller_qualified=caller_qualified,
            )
        )

        root = _root_module(callee)
        if callee == "open":
            self._signal("open", node, callee)
        if root == "sqlite3":
            self._signal("sqlite", node, callee)
        if callee.rsplit(".", 1)[-1] == "connect":
            self._signal("connect", node, callee)
        if callee.rsplit(".", 1)[-1] == "execute":
            self._signal("execute", node, callee)
        if root in _NETWORK_MODULES or callee.rsplit(".", 1)[-1] in {"urlopen", "request"}:
            self._signal("network", node, callee)
        if root == "subprocess" or callee.rsplit(".", 1)[-1] in _SUBPROCESS_CALLS:
            self._signal("subprocess", node, callee)
        self.generic_visit(node)


def _resolve_call_targets(
    functions: Iterable[FunctionRecord], edges: Iterable[CallEdge]
) -> list[CallEdge]:
    records = list(functions)
    by_path_and_name = {(record.path, record.name): record for record in records}
    by_name: dict[str, list[FunctionRecord]] = {}
    for record in records:
        by_name.setdefault(record.name, []).append(record)

    resolved: list[CallEdge] = []
    for edge in edges:
        target: FunctionRecord | None = None
        callee_name = edge.callee.rsplit(".", 1)[-1]
        if edge.caller_qualified and "::" in edge.caller_qualified:
            caller_path = edge.caller_qualified.split("::", 1)[0]
            target = by_path_and_name.get((caller_path, callee_name))
        if target is None and len(by_name.get(callee_name, ())) == 1:
            target = by_name[callee_name][0]
        resolved.append(
            CallEdge(
                caller=edge.caller,
                callee=edge.callee,
                path=edge.path,
                lineno=edge.lineno,
                caller_qualified=edge.caller_qualified,
                callee_qualified=target.qualified_name if target else None,
            )
        )
    return resolved


def analyze_repository(
    root: Path,
    allowed_root: Path | None = None,
    selected_files: Iterable[str] | None = None,
) -> AnalysisReport:
    """Analyze ``.py`` files beneath ``root`` without importing them.

    When ``selected_files`` is provided, only those relative Python paths are
    inventoried.  This keeps candidate-specific evidence separate from a
    directory containing multiple prepared variants.

    ``allowed_root`` is a mandatory security boundary in hosted callers; when
    omitted it defaults to ``root`` so direct local use remains convenient.
    The boundary check happens before directory traversal.
    """

    root_path = Path(root).resolve()
    allowed_path = Path(allowed_root if allowed_root is not None else root).resolve()
    try:
        root_path.relative_to(allowed_path)
    except ValueError as exc:
        raise ValueError(f"root must be beneath allowed_root: {root_path}") from exc
    if not root_path.is_dir():
        raise ValueError(f"root is not a directory: {root_path}")

    report = AnalysisReport(
        dynamic_dispatch_limitations=[
            "Static AST call edges do not resolve dynamic dispatch, reflection, callbacks, or runtime imports."
        ]
    )

    if selected_files is None:
        source_paths = sorted(root_path.rglob("*.py"))
    else:
        source_paths = []
        for relative_path in selected_files:
            relative = Path(relative_path)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError("selected files must be relative to root")
            source_path = root_path / relative
            try:
                source_path.resolve(strict=False).relative_to(root_path)
            except ValueError as exc:
                raise ValueError("selected files must be beneath root") from exc
            if source_path.suffix == ".py" and source_path.is_file():
                source_paths.append(source_path)

        source_paths.sort()

    for source_path in source_paths:
        # ``rglob`` can yield a symlink to a file outside the repository.  Do
        # not even list or read symlinked candidates; also re-check the
        # canonical target for defense in depth if traversal behavior changes.
        if source_path.is_symlink():
            continue
        resolved_source = source_path.resolve(strict=False)
        try:
            resolved_source.relative_to(root_path)
            resolved_source.relative_to(allowed_path)
        except ValueError:
            continue
        relative_path = source_path.relative_to(root_path).as_posix()
        report.files.append(relative_path)
        try:
            # utf-8-sig accepts the legal BOM form without shifting offsets.
            source = source_path.read_text(encoding="utf-8-sig")
            tree = ast.parse(source, filename=relative_path)
        except SyntaxError as exc:
            report.syntax_errors.append(
                SyntaxErrorRecord(
                    path=relative_path,
                    message=exc.msg,
                    lineno=exc.lineno,
                    offset=exc.offset,
                )
            )
            continue
        except UnicodeDecodeError as exc:
            # An undecodable file is a bounded per-file finding, not a reason
            # to abort the whole inventory.
            report.syntax_errors.append(
                SyntaxErrorRecord(path=relative_path, message=str(exc))
            )
            continue
        visitor = _InventoryVisitor(relative_path)
        visitor.visit(tree)
        report.functions.extend(visitor.functions)
        report.call_edges.extend(visitor.call_edges)
        report.side_effect_signals.extend(visitor.side_effect_signals)

    report.call_edges = _resolve_call_targets(report.functions, report.call_edges)
    return report


__all__ = [
    "AnalysisReport",
    "CallEdge",
    "FunctionRecord",
    "SideEffectSignal",
    "SyntaxErrorRecord",
    "analyze_repository",
]
