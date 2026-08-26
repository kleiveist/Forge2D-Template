"""Run environment checks for the Forge2D repository."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
import importlib.util
import os
import platform
import re
import shutil
import subprocess
import tomllib

from g2dtool.config import (
    ProjectConfigError,
    ToolchainConfigError,
    load_project_config,
    load_toolchain_config,
)
from g2dtool.godot import FAIL as GODOT_FAIL
from g2dtool.godot import discover_godot
from g2dtool.repository import RepositoryLayout, RepositoryNotFoundError, discover_repository_layout
from g2dtool.logger import log_status


EXIT_REQUIREMENT_MISSING = 1

PASS = "pass"
WARN = "warn"
FAIL = "fail"


class CommandResult(tuple[int, str, str]):
    """Tuple-compatible process result."""

    returncode: int
    stdout: str
    stderr: str

    def __new__(cls, returncode: int, stdout: str, stderr: str):
        return tuple.__new__(cls, (returncode, stdout, stderr))

    @property
    def returncode(self) -> int:
        return int(self[0])

    @property
    def stdout(self) -> str:
        return str(self[1])

    @property
    def stderr(self) -> str:
        return str(self[2])


ToolFinder = Callable[[str], str | None]
CommandRunner = Callable[[Sequence[str]], CommandResult]


@dataclass(frozen=True, slots=True)
class DoctorCheck:
    name: str
    status: str
    detail: str

    @property
    def printable(self) -> str:
        return log_status(self.status, self.name, self.detail)


@dataclass(frozen=True, slots=True)
class DoctorReport:
    checks: tuple[DoctorCheck, ...]

    @property
    def exit_code(self) -> int:
        if any(check.name == "internal" and check.status == FAIL for check in self.checks):
            return 2
        return 0 if all(check.status in {PASS, WARN} for check in self.checks) else 1


def collect_doctor_report(
    start: Path | None = None,
    *,
    find_tool: ToolFinder = shutil.which,
    run_command: CommandRunner | None = None,
    python_version: str | None = None,
    python_executable: str | None = None,
) -> DoctorReport:
    """Inspect repository and external tool requirements."""

    del python_executable
    runner = run_command or _run_command
    try:
        repository = discover_repository_layout(start)
    except RepositoryNotFoundError as error:
        return DoctorReport(
            (
                DoctorCheck("repository", FAIL, str(error)),
                DoctorCheck("internal", FAIL, "Cannot continue without repository root."),
            )
        )

    checks = [
        _check_repository_root(repository),
        _check_python(repository, observed_version=python_version),
        _check_pyproject(repository),
        _check_tooling_layout(repository),
        _check_project_configuration(repository),
        _check_godot_project(repository),
        _check_writable_paths(repository),
        _check_venv(repository),
        _check_local_import(repository),
        _check_godot(repository, find_tool=find_tool, run_command=runner),
        _check_project_dependencies(repository),
        _check_optional_dev_tools(find_tool),
    ]

    return DoctorReport(tuple(checks))


def format_doctor_report(report: DoctorReport) -> str:
    lines = ["🧾 Forge2D environment doctor"]
    lines.extend(check.printable for check in report.checks)
    passed = sum(1 for check in report.checks if check.status == PASS)
    warnings = sum(1 for check in report.checks if check.status == WARN)
    failures = sum(1 for check in report.checks if check.status == FAIL)
    lines.append(
        f"Doctor summary: {passed} passed, {warnings} warnings, {failures} failures"
    )
    if report.exit_code == 0:
        lines.append("✅ Result: requirements satisfied")
    else:
        lines.append("❌ Result: requirements missing or incompatible")
    return "\n".join(lines)


def _check_repository_root(repository: RepositoryLayout) -> DoctorCheck:
    if repository.repository_root.exists():
        return DoctorCheck("repository", PASS, f"found at {repository.repository_root}")
    return DoctorCheck("repository", FAIL, "Repository root not found.")


def _check_python(repository: RepositoryLayout, *, observed_version: str | None) -> DoctorCheck:
    observed = _parse_version(observed_version or platform.python_version())
    if observed is None:
        return DoctorCheck(
            "supported python",
            FAIL,
            "Python version could not be parsed.",
        )

    try:
        toolchain = load_toolchain_config(repository.toolchain_config)
        minimum = (toolchain.minimum_python_major, toolchain.minimum_python_minor)
    except ToolchainConfigError as error:
        return DoctorCheck(
            "supported python",
            FAIL,
            f"Cannot read toolchain configuration: {error}",
        )

    if observed < minimum:
        return DoctorCheck(
            "supported python",
            FAIL,
            f"Python >= {minimum[0]}.{minimum[1]} required; found {observed[0]}.{observed[1]}.",
        )
    return DoctorCheck(
        "supported python",
        PASS,
        f"Python {observed[0]}.{observed[1]} is supported.",
    )


def _check_pyproject(repository: RepositoryLayout) -> DoctorCheck:
    if not repository.pyproject_toml.exists():
        return DoctorCheck("pyproject", FAIL, "pyproject.toml is missing.")
    try:
        with repository.pyproject_toml.open("rb") as project_file:
            tomllib.load(project_file)
        return DoctorCheck("pyproject", PASS, f"found at {repository.pyproject_toml}")
    except OSError as error:
        return DoctorCheck("pyproject", FAIL, f"failed to read pyproject: {error}")
    except tomllib.TOMLDecodeError as error:
        return DoctorCheck("pyproject", FAIL, f"invalid pyproject.toml: {error}")


def _check_tooling_layout(repository: RepositoryLayout) -> DoctorCheck:
    if not repository.tools_source_directory.exists():
        return DoctorCheck("tools path", FAIL, "tools/src is missing.")
    return DoctorCheck("tools path", PASS, "tools/src is present.")


def _check_project_configuration(repository: RepositoryLayout) -> DoctorCheck:
    try:
        config = load_project_config(repository.project_config)
        return DoctorCheck(
            "project configuration",
            PASS,
            (
                f"schema={config.schema_version}, template={config.template_id}, "
                f"godot project={config.godot_project_path}"
            ),
        )
    except ProjectConfigError as error:
        return DoctorCheck("project configuration", FAIL, str(error))


def _check_godot_project(repository: RepositoryLayout) -> DoctorCheck:
    if repository.game_project_path.exists():
        return DoctorCheck(
            "godot project",
            PASS,
            f"project file exists at {repository.game_project_path}",
        )
    return DoctorCheck("godot project", FAIL, f"{repository.game_project_path} not found.")


def _check_writable_paths(repository: RepositoryLayout) -> DoctorCheck:
    required = (
        repository.repository_root,
        repository.tools_source_directory,
        repository.game_directory,
    )
    for directory in required:
        if not directory.exists():
            return DoctorCheck(
                "required directories",
                FAIL,
                f"{directory} is missing.",
            )
        if not os.access(directory, os.W_OK):
            return DoctorCheck(
                "required directories",
                FAIL,
                f"{directory} is not writable for the current user.",
            )
    return DoctorCheck("required directories", PASS, "required directories are writable.")


def _check_venv(repository: RepositoryLayout) -> DoctorCheck:
    venv_python = repository.venv_directory / ("Scripts" if os.name == "nt" else "bin") / (
        "python.exe" if os.name == "nt" else "python"
    )
    if not venv_python.exists():
        return DoctorCheck(
            ".venv",
            WARN,
            "No .venv has been created yet. Run `python tools/control.py install`.",
        )
    return DoctorCheck(".venv", PASS, f".venv python at {venv_python}")


def _check_local_import(repository: RepositoryLayout) -> DoctorCheck:
    spec = importlib.util.spec_from_file_location(
        "g2dtool", str(repository.tools_source_directory / "g2dtool" / "__init__.py")
    )
    if spec is None:
        return DoctorCheck(
            "local tooling import",
            FAIL,
            "Could not load package g2dtool from tools/src.",
        )
    return DoctorCheck("local tooling import", PASS, "g2dtool package is resolvable.")


def _check_godot(
    repository: RepositoryLayout,
    *,
    find_tool: ToolFinder,
    run_command: CommandRunner,
) -> DoctorCheck:
    result = discover_godot(
        repository.repository_root,
        find_tool=find_tool,
        run_command=run_command,
    )
    if result.status == PASS:
        return DoctorCheck("godot", PASS, result.detail)

    detail = result.detail
    if result.status == GODOT_FAIL and _is_arch():
        detail += (
            "\nInstallation:\n"
            "  sudo pacman -S --needed godot\n"
            "Danach erneut:\n"
            "  python tools/control.py doctor"
        )
    return DoctorCheck("godot", FAIL, detail)


def _check_project_dependencies(repository: RepositoryLayout) -> DoctorCheck:
    try:
        with repository.pyproject_toml.open("rb") as project_file:
            project = tomllib.load(project_file)
    except OSError as error:
        return DoctorCheck(
            "project dependencies",
            WARN,
            f"could not read pyproject.toml: {error}",
        )
    except tomllib.TOMLDecodeError as error:
        return DoctorCheck(
            "project dependencies",
            FAIL,
            f"invalid pyproject.toml: {error}",
        )

    dependencies = project.get("project", {}).get("dependencies", [])
    if not isinstance(dependencies, list):
        return DoctorCheck(
            "project dependencies",
            FAIL,
            "project.dependencies is invalid.",
        )
    return DoctorCheck(
        "project dependencies",
        PASS,
        f"{len(dependencies)} dependency declared.",
    )


def _check_optional_dev_tools(find_tool: ToolFinder) -> DoctorCheck:
    missing = [name for name in ("pytest",) if find_tool(name) is None]
    if missing:
        return DoctorCheck(
            "optional development tools",
            WARN,
            "Optional tool(s) missing: " + ", ".join(missing),
        )
    return DoctorCheck("optional development tools", PASS, "optional dev tools available.")


def _run_command(arguments: Sequence[str]) -> CommandResult:
    completed = subprocess.run(
        list(arguments),
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def _is_arch() -> bool:
    if platform.system() != "Linux":
        return False
    release = Path("/etc/os-release")
    if not release.exists():
        return False
    for line in release.read_text(encoding="utf-8").splitlines():
        if line.startswith("ID="):
            return line.removeprefix("ID=").strip().strip('"') == "arch"
    return False


def _parse_version(value: str) -> tuple[int, int] | None:
    parts = value.split(".")
    if len(parts) < 2:
        return None
    if not (parts[0].isdigit() and parts[1].isdigit()):
        return None
    return int(parts[0]), int(parts[1])
