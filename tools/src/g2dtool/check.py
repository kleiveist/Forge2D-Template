"""Run the Forge2D Template release gate."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
import os
import subprocess
import sys

from g2dtool.doctor import collect_doctor_report, format_doctor_report
from g2dtool.godot import (
    PASS,
    GodotTestConfigurationError,
    build_godot_test_command,
    discover_godot,
)
from g2dtool.logger import error, join_command, print_status_line, success
from g2dtool.repository import RepositoryLayout, discover_repository_layout
from g2dtool.style import run_style


ProcessRunner = Callable[[Sequence[str], Path], int]
GODOT_TEST_SUCCESS_MARKER = "Forge2D bootstrap integration test: passed"


@dataclass(frozen=True, slots=True)
class GateStep:
    name: str
    exit_code: int


def run_check(
    *,
    start: Path | None = None,
    run_process: ProcessRunner | None = None,
) -> int:
    """Run Doctor, source style, Python tests, and the Godot integration test."""

    layout = discover_repository_layout(start)
    runner = run_process or _run_process
    steps: list[GateStep] = []

    print_status_line("running", "Doctor", "checking local requirements")
    doctor_report = collect_doctor_report(start=layout.repository_root)
    print(format_doctor_report(doctor_report))
    steps.append(GateStep("Doctor", doctor_report.exit_code))

    print_status_line("running", "Source style", "checking Python and GDScript")
    steps.append(GateStep("Source style", run_style(start=layout.repository_root)))

    python = _test_python(layout)
    pytest_command = [str(python), "-m", "pytest", "tools/tests"]
    print_status_line("running", "Python tests", join_command(pytest_command))
    steps.append(
        GateStep(
            "Python tests",
            runner(pytest_command, layout.repository_root),
        )
    )

    godot_result = discover_godot(layout.repository_root)
    if godot_result.status != PASS or godot_result.executable is None:
        error(f"Godot integration test skipped as failure: {godot_result.detail}")
        steps.append(GateStep("Godot headless integration test", 1))
    else:
        try:
            godot_command = build_godot_test_command(
                godot_result.executable,
                layout.game_directory,
            )
        except GodotTestConfigurationError as exc:
            error(f"Godot integration test configuration failed: {exc}")
            steps.append(GateStep("Godot headless integration test", 1))
        else:
            print_status_line(
                "running", "Godot headless integration test", join_command(godot_command)
            )
            godot_exit_code = (
                runner(godot_command, layout.repository_root)
                if run_process is not None
                else _run_godot_integration_test(godot_command, layout.repository_root)
            )
            steps.append(
                GateStep(
                    "Godot headless integration test",
                    godot_exit_code,
                )
            )

    failures = [step for step in steps if step.exit_code != 0]
    if failures:
        for step in failures:
            error(f"{step.name} failed with exit code {step.exit_code}.")
        return 1

    success("Release gate passed.")
    return 0


def _test_python(layout: RepositoryLayout) -> Path:
    candidate = layout.venv_directory / (
        "Scripts" if os.name == "nt" else "bin"
    ) / ("python.exe" if os.name == "nt" else "python")
    if candidate.exists():
        return candidate
    return Path(sys.executable)


def _run_process(command: Sequence[str], cwd: Path) -> int:
    try:
        completed = subprocess.run(
            list(command),
            cwd=str(cwd),
            check=False,
            timeout=180,
        )
    except FileNotFoundError as exc:
        error(f"Command not found: {exc.filename}")
        return 1
    except subprocess.TimeoutExpired:
        error(f"Command timed out: {join_command(command)}")
        return 1
    return int(completed.returncode)


def _run_godot_integration_test(command: Sequence[str], cwd: Path) -> int:
    """Run Godot and require the test runner's explicit success marker."""

    try:
        completed = subprocess.run(
            list(command),
            cwd=str(cwd),
            check=False,
            capture_output=True,
            text=True,
            timeout=180,
        )
    except FileNotFoundError as exc:
        error(f"Command not found: {exc.filename}")
        return 1
    except subprocess.TimeoutExpired:
        error(f"Command timed out: {join_command(command)}")
        return 1

    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    if completed.returncode != 0:
        return int(completed.returncode)
    if GODOT_TEST_SUCCESS_MARKER not in completed.stdout:
        error("Godot integration test exited without its success marker.")
        return 1
    return 0
