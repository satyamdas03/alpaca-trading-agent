import os
import subprocess
import sys
from pathlib import Path

import pytest


REPO = Path(__file__).parents[2]
SCRIPT = REPO / "scripts" / "ml_benchmark_demo.py"


def _run(args: list[str]) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO / "src")
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )


def test_honest_wall_controls_false_certs():
    """With the train-only wall, no classifier should be certified."""
    result = _run(["--trials", "100", "--reps", "5", "--wall"])
    assert "Mean certified configs: 0.00" in result.stdout


def test_online_by_wall_controls_false_certs():
    """Online BY prefix correction with the wall should also certify nothing."""
    result = _run(["--trials", "100", "--reps", "5", "--wall", "--online"])
    assert "Mean certified configs: 0.00" in result.stdout


def test_cheating_generator_non_negative():
    """Without the wall the generator may find spurious certs, but not many."""
    result = _run(["--trials", "200", "--reps", "5"])
    # Just sanity-check it runs and prints the expected fields.
    assert "Mean certified configs:" in result.stdout
    assert "Best observed val acc:" in result.stdout
