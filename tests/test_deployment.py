from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]


def test_app_imports_src_package_and_bundled_fixture_without_pythonpath():
    check = """
from pathlib import Path
import sys

project_root = Path.cwd().resolve()
src_root = project_root / "src"
sys.path[:] = [entry for entry in sys.path if Path(entry or ".").resolve() != src_root]

import app
import shadowspec
from shadowspec.service import FIXTURE_ROOT

assert Path(shadowspec.__file__).resolve().is_relative_to(src_root)
assert FIXTURE_ROOT == project_root / "fixtures" / "legacy_orders"
assert (FIXTURE_ROOT / "variants" / "narrow.py").is_file()
"""
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        [sys.executable, "-c", check],
        cwd=PROJECT_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
