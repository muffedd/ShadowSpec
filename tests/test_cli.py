from __future__ import annotations

import json

from shadowspec.cli import main


def test_cli_outputs_machine_readable_verdict(capsys):
    assert main(["run", "narrow", "--format", "json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["validation"]["verdict"] == "accepted"


def test_cli_rejected_candidate_uses_nonzero_exit(capsys):
    assert main(["run", "bad", "--format", "json"]) == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["validation"]["verdict"] == "rejected"

