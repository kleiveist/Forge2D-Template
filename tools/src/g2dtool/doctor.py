"""Run environment checks for the Forge2D repository."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
import platform
import shutil
import subprocess
import sys

from g2dtool.config import ProjectConfigError, load_project_config
from g2dtool.repository import RepositoryNotFoundError, find_repository_root


EXIT_REQUIREMENT_MISSING = 1
GODOT_EXECUTABLE_CANDIDATES = ("godot4", "godot")


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Small subprocess result type that is straightforward to fake in tests."""

    returncode: int
    stdout: str
    stderr: str


@dataclass(frozen=True, slots=True)
class DoctorCheck:
    """One deterministic doctor check."""

    name: str
    status: str
    detail: str

    @property
    def passed(self) -> bool:
        return self.status == "ok"


@dataclass(frozen=True, slots=True)
class DoctorReport:
    """Complete doctor output and its process exit code."""

    checks: tuple[DoctorCheck, ...]

    @property
    def exit_code(self) -> int:
        return 0 if all(check.passed for check in self.checks) else EXIT_REQUIREMENT_MISSING


ToolFinder = Callable[[str], str | None]
CommandRunner = Callable[[Sequence[str]], CommandResult]


def collect_doctor_report(
    start: Path | None = None,
    *,
    find_tool: ToolFinder = shutil.which,
    run_command: CommandRunner | None = None,
    python_version: str | None = None,
    python_executable: str | None = None,
) -> DoctorReport:
    """Inspect repository, Python, Git, and Godot without changing the machine."""

    runner = run_command if run_command is not None else _run_command
    checks: list[DoctorCheck] = []

    repository_root: Path | None
    try:
        repository_root = find_repository_root(start)
        checks.append(DoctorCheck("repository", "ok", str(repository_root)))
    except RepositoryNotFoundError as error:
        repository_root = None
        checks.append(DoctorCheck("repository", "missing", str(error)))

    if repository_root is None:
        checks.append(
            DoctorCheck(
                "configuration",
                "missing",
                "Project configuration cannot be checked without a repository root.",
            )
        )
    else:
        try:
            config = load_project_config(repository_root / "config" / "project.toml")
            checks.append(
                DoctorCheck(
                    "configuration",
                    "ok",
                    f"schema {config.schema_version}, template {config.template_id}",
                )
            )
        except ProjectConfigError as error:
            checks.append(DoctorCheck("configuration", "error", str(error)))

    current_python_version = python_version or platform.python_version()
    current_python_executable = python_executable or sys.executable
    checks.append(
        DoctorCheck(
            "python",
            "ok",
            f"Python {current_python_version} at {current_python_executable}",
        )
    )

    checks.append(_check_git(find_tool, runner))
    checks.append(_check_godot(find_tool, runner))
    return DoctorReport(tuple(checks))


def format_doctor_report(report: DoctorReport) -> str:
    """Render stable, non-colored output suitable for humans and automation."""

    lines = ["Forge2D environment doctor"]
    lines.extend(
        f"[{check.status.upper()}] {check.name}: {check.detail}"
        for check in report.checks
    )
    if report.exit_code == 0:
        lines.append("Result: ready")
    else:
        lines.append("Result: requirements missing or incompatible")
    return "\n".join(lines)


def _check_git(find_tool: ToolFinder, run_command: CommandRunner) -> DoctorCheck:
    executable = find_tool("git")
    if executable is None:
        return DoctorCheck(
            "git",
            "missing",
            "Git was not found on PATH. Install Git and make its executable available.",
        )

    result = run_command((executable, "--version"))
    version = _first_output_line(result)
    if result.returncode != 0:
        return DoctorCheck(
            "git",
            "error",
            f"Git exists at {executable} but version detection failed: {version}",
        )
    return DoctorCheck("git", "ok", version or f"available at {executable}")


def _check_godot(find_tool: ToolFinder, run_command: CommandRunner) -> DoctorCheck:
    executable = next(
        (
            resolved
            for name in GODOT_EXECUTABLE_CANDIDATES
            if (resolved := find_tool(name)) is not None
        ),
        None,
    )
    if executable is None:
        attempted = ", ".join(GODOT_EXECUTABLE_CANDIDATES)
        return DoctorCheck(
            "godot",
            "missing",
            "Godot 4 was not found on PATH "
            f"(tried: {attempted}). Install a verified Godot 4 editor and expose its executable.",
        )

    result = run_command((executable, "--version"))
    version = _first_output_line(result)
    if result.returncode != 0:
        return DoctorCheck(
            "godot",
            "error",
            f"Godot exists at {executable} but version detection failed: {version}",
        )
    if not version.startswith("4."):
        return DoctorCheck(
            "godot",
            "incompatible",
            f"Expected Godot 4, found {version or 'an unknown version'} at {executable}.",
        )
    return DoctorCheck("godot", "ok", version)


def _run_command(arguments: Sequence[str]) -> CommandResult:
    try:
        completed = subprocess.run(
            list(arguments),
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return CommandResult(1, "", str(error))
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def _first_output_line(result: CommandResult) -> str:
    output = result.stdout.strip() or result.stderr.strip()
    return output.splitlines()[0] if output else "no version output"
