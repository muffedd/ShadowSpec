from __future__ import annotations

from pathlib import Path

import pytest

from shadowspec.analyzer import AnalysisReport, analyze_repository


def test_analyze_repository_inventories_python_files_calls_and_side_effects(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "app.py").write_text(
        """
import sqlite3
import subprocess
import socket

def helper(value):
    return value

def entry(db_path):
    connection = sqlite3.connect(db_path)
    connection.execute("create table audit (value text)")
    open("audit.log", "a")
    socket.socket()
    subprocess.run(["echo", "ok"])
    return helper("ok")
""",
        encoding="utf-8",
    )
    (tmp_path / "pkg" / "worker.py").write_text(
        "from app import helper\n\ndef worker():\n    return helper('worker')\n",
        encoding="utf-8",
    )

    report = analyze_repository(tmp_path, allowed_root=tmp_path)

    assert isinstance(report, AnalysisReport)
    assert report.files == ["app.py", "pkg/worker.py"]
    assert {function.name for function in report.functions} >= {
        "entry",
        "helper",
        "worker",
    }
    assert any(edge.caller == "entry" and edge.callee == "helper" for edge in report.call_edges)
    assert {signal.kind for signal in report.side_effect_signals} >= {
        "sqlite",
        "connect",
        "execute",
        "open",
        "network",
        "subprocess",
        "import",
    }
    assert all(not Path(path).is_absolute() for path in report.files)


def test_syntax_errors_are_reported_without_aborting_and_paths_are_relative(tmp_path):
    (tmp_path / "nested").mkdir()
    (tmp_path / "nested" / "broken.py").write_text("def broken(:\n", encoding="utf-8")
    (tmp_path / "ok.py").write_text("def okay():\n    return 1\n", encoding="utf-8")

    report = analyze_repository(tmp_path, allowed_root=tmp_path)

    assert report.files == ["nested/broken.py", "ok.py"]
    assert report.syntax_errors[0].path == "nested/broken.py"
    assert "invalid syntax" in report.syntax_errors[0].message
    assert [function.name for function in report.functions] == ["okay"]


def test_root_must_be_beneath_allowed_root_before_repository_access(tmp_path):
    allowed_root = tmp_path / "allowed"
    outside_root = tmp_path / "outside"
    allowed_root.mkdir()
    outside_root.mkdir()
    (outside_root / "secret.py").write_text("raise RuntimeError('must not read')\n", encoding="utf-8")

    with pytest.raises(ValueError, match="allowed_root"):
        analyze_repository(outside_root, allowed_root=allowed_root)


def test_symlinked_python_file_outside_allowed_root_is_not_read(tmp_path):
    allowed_root = tmp_path / "allowed"
    repository = allowed_root / "repository"
    outside_file = tmp_path / "outside.py"
    repository.mkdir(parents=True)
    outside_file.write_text(
        "def secret_function():\n    return 'outside boundary'\n",
        encoding="utf-8",
    )
    (repository / "linked.py").symlink_to(outside_file)

    report = analyze_repository(repository, allowed_root=allowed_root)

    assert "linked.py" not in report.files
    assert not any(function.name == "secret_function" for function in report.functions)


def test_reachability_reports_transitive_local_dependencies_and_dynamic_limitations(tmp_path):
    (tmp_path / "service.py").write_text(
        """
def leaf():
    return 1

def middle():
    return leaf()

def entry():
    return middle()

def dynamic_entry():
    operation = middle
    return operation()
""",
        encoding="utf-8",
    )

    report = analyze_repository(tmp_path, allowed_root=tmp_path)

    assert report.reachable_from("entry") == {"middle", "leaf"}
    assert report.blast_radius("middle") == {"leaf"}
    assert report.dynamic_dispatch_limitations
    assert any("dynamic dispatch" in limitation.lower() for limitation in report.dynamic_dispatch_limitations)


def test_undecodable_file_is_bounded_finding_not_crash(tmp_path):
    (tmp_path / "bad.py").write_bytes(b"def f():\n    return b'\xff\xfe'\n")
    (tmp_path / "ok.py").write_text("def okay():\n    return 1\n", encoding="utf-8")

    report = analyze_repository(tmp_path, allowed_root=tmp_path)

    assert report.files == ["bad.py", "ok.py"]
    assert [function.name for function in report.functions] == ["okay"]
    assert report.syntax_errors[0].path == "bad.py"


def test_bom_prefixed_file_parses_like_the_interpreter(tmp_path):
    (tmp_path / "bom.py").write_text("\ufeffdef flagged():\n    return 1\n", encoding="utf-8")

    report = analyze_repository(tmp_path, allowed_root=tmp_path)

    assert report.syntax_errors == []
    assert [function.name for function in report.functions] == ["flagged"]


def test_selected_files_reject_traversal_and_absolute_paths(tmp_path):
    (tmp_path / "ok.py").write_text("def okay():\n    return 1\n", encoding="utf-8")

    for bad in ("../outside.py", str(tmp_path / "ok.py")):
        with pytest.raises(ValueError, match="relative to root"):
            analyze_repository(tmp_path, allowed_root=tmp_path, selected_files=(bad,))


def test_async_functions_and_unknown_reachability_start(tmp_path):
    (tmp_path / "mod.py").write_text(
        "async def fetch():\n    return 1\n",
        encoding="utf-8",
    )

    report = analyze_repository(tmp_path, allowed_root=tmp_path)

    assert [function.name for function in report.functions] == ["fetch"]
    assert report.reachable_from("does_not_exist") == set()
