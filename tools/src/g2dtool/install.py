"""Prepare and verify a local Forge2D Template development environment."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
import os
import platform
import re
import shutil
import subprocess
import sys

from g2dtool.config import ToolchainConfig, ToolchainConfigError, load_toolchain_config
from g2dtool.doctor import collect_doctor_report, format_doctor_report
from g2dtool.godot import PASS, GodotProbeResult, discover_godot
from g2dtool.logger import (
    error,
    info,
    join_command,
    print_command_plan,
    print_dry_run,
    print_help_line,
    print_status_line,
    success,
    warning,
)
from g2dtool.repository import RepositoryLayout, discover_repository_layout


ToolFinder = Callable[[str], str | None]
CommandRunner = Callable[[Sequence[str]], "CommandResult"]
CONFIRMED_ANSWERS = frozenset({"y", "yes", "j", "ja"})
ARCH_DISTRIBUTIONS = frozenset({"arch", "archlinux", "endeavouros", "manjaro"})
SUPPORTED_SYSTEMS = frozenset({"Linux", "Windows", "Darwin"})
REQUIREMENT_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
APT_CANDIDATE = re.compile(
    r"^\s*Candidate:\s*(?:\d+:)?(?P<major>\d+)(?:\.\d+)",
    re.MULTILINE,
)


class CommandResult(tuple[int, str, str]):
    """Tuple-compatible subprocess result."""

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


class InstallError(RuntimeError):
    """Expected installer failure with concrete recovery steps."""

    def __init__(self, cause: str, solutions: Sequence[str] = ()) -> None:
        super().__init__(cause)
        self.cause = cause
        self.solutions = tuple(solutions)


@dataclass(frozen=True, slots=True)
class HostEnvironment:
    """Detected host properties relevant to safe package installation."""

    system: str
    distribution: str | None
    package_manager: str | None
    elevated: bool
    sudo_available: bool


@dataclass(frozen=True, slots=True)
class PythonBootstrapProbe:
    """Availability of standard-library virtual-environment bootstrapping."""

    venv_available: bool
    pip_seed_available: bool
    venv_detail: str
    pip_detail: str

    @property
    def ready(self) -> bool:
        return self.venv_available and self.pip_seed_available


@dataclass(frozen=True, slots=True)
class SystemAction:
    """One package-manager operation and its failure remediation."""

    description: str
    command: tuple[str, ...]
    recovery: str


@dataclass(frozen=True, slots=True)
class SystemPlan:
    """Package-manager work required by the current preflight."""

    actions: tuple[SystemAction, ...]
    notes: tuple[str, ...]
    python_planned: bool = False
    bootstrap_planned: bool = False
    godot_planned: bool = False


def run_install(
    *,
    start: Path | None = None,
    dry_run: bool = False,
    yes: bool = False,
    run_command: CommandRunner | None = None,
    find_tool: ToolFinder = shutil.which,
    confirm: Callable[[str], str] | None = None,
    system_name: str | None = None,
    distribution: str | None = None,
    python_version: tuple[int, int] | None = None,
    python_executable: str | None = None,
    is_elevated: bool | None = None,
) -> int:
    """Create a repository-local environment without using system pip."""

    runner = run_command or _run_command
    prompt = confirm or input
    try:
        return _run_install(
            start=start,
            dry_run=dry_run,
            yes=yes,
            run_command=runner,
            find_tool=find_tool,
            confirm=prompt,
            system_name=system_name,
            distribution=distribution,
            python_version=python_version,
            python_executable=python_executable,
            is_elevated=is_elevated,
        )
    except InstallError as exc:
        error(f"Installation failed: {exc.cause}")
        for solution in exc.solutions:
            print_help_line(solution)
        return 1


def _run_install(
    *,
    start: Path | None,
    dry_run: bool,
    yes: bool,
    run_command: CommandRunner,
    find_tool: ToolFinder,
    confirm: Callable[[str], str],
    system_name: str | None,
    distribution: str | None,
    python_version: tuple[int, int] | None,
    python_executable: str | None,
    is_elevated: bool | None,
) -> int:
    layout = discover_repository_layout(start)
    toolchain = _load_toolchain(layout)
    host = _detect_host(
        system_name=system_name,
        distribution=distribution,
        find_tool=find_tool,
        is_elevated=is_elevated,
    )
    installer_python = python_executable or sys.executable
    observed_python = python_version or (sys.version_info.major, sys.version_info.minor)
    minimum_python = (
        toolchain.minimum_python_major,
        toolchain.minimum_python_minor,
    )

    info(f"Preparing Forge2D Template environment in {layout.repository_root}")
    distribution_label = host.distribution or "not applicable"
    manager_label = host.package_manager or "none detected"
    info(
        f"Detected platform: {host.system} ({distribution_label}); "
        f"package manager: {manager_label}"
    )
    if host.system not in SUPPORTED_SYSTEMS:
        warning(
            f"Platform {host.system!r} has no automatic system-package path; "
            "local .venv setup will still be attempted."
        )

    python_supported = observed_python >= minimum_python
    _print_python_version_status(observed_python, minimum_python)
    bootstrap = _probe_python_bootstrap(installer_python, run_command)
    existing_venv_python = _venv_python_path(
        layout.venv_directory,
        system_name=host.system,
    )
    existing_venv_ready = _venv_has_pip(existing_venv_python, run_command)
    _print_bootstrap_status(
        bootstrap,
        existing_venv_ready=existing_venv_ready,
    )
    godot_probe = discover_godot(
        layout.repository_root,
        find_tool=find_tool,
        run_command=run_command,
    )
    _print_godot_status(godot_probe)

    plan = _build_system_plan(
        host,
        need_python=not python_supported,
        need_bootstrap=not bootstrap.ready and not existing_venv_ready,
        need_godot=godot_probe.status != PASS,
        minimum_python=minimum_python,
        required_godot_major=toolchain.required_godot_major,
        yes=yes,
        find_tool=find_tool,
        run_command=run_command,
    )
    actions_applied = _apply_system_plan(
        plan,
        dry_run=dry_run,
        yes=yes,
        confirm=confirm,
        run_command=run_command,
    )

    if not python_supported:
        if dry_run and plan.python_planned:
            print_help_line(_python_rerun_instruction(host, minimum_python))
            success("Dry-run complete; no changes were made.")
            return 0
        cause = (
            f"Python {minimum_python[0]}.{minimum_python[1]} or newer is required; "
            f"the current interpreter is {observed_python[0]}.{observed_python[1]}."
        )
        if actions_applied and plan.python_planned:
            cause += (
                " A supported Python was requested, but this process cannot switch "
                "interpreters."
            )
        raise InstallError(cause, (_python_rerun_instruction(host, minimum_python),))

    if (
        not bootstrap.ready
        and not existing_venv_ready
        and not dry_run
        and actions_applied
        and plan.bootstrap_planned
    ):
        bootstrap = _probe_python_bootstrap(installer_python, run_command)
        _print_bootstrap_status(bootstrap, existing_venv_ready=False)

    if not bootstrap.ready and not existing_venv_ready:
        if not (dry_run and plan.bootstrap_planned):
            raise InstallError(
                "The current Python cannot create a pip-enabled virtual environment.",
                (
                    _python_bootstrap_instruction(host),
                    "Re-run `python tools/control.py install` after repairing Python venv support.",
                ),
            )

    venv_python = _ensure_venv(
        layout.venv_directory,
        system_name=host.system,
        installer_python=installer_python,
        dry_run=dry_run,
        yes=yes,
        run_command=run_command,
        confirm=confirm,
    )
    _install_local_tooling(
        layout,
        toolchain=toolchain,
        venv_python=venv_python,
        dry_run=dry_run,
        run_command=run_command,
    )

    if dry_run:
        if godot_probe.status != PASS and not plan.godot_planned:
            _print_manual_godot_installation(host, toolchain.required_godot_major)
        success("Dry-run complete; no changes were made.")
        return 0

    final_godot_probe = discover_godot(
        layout.repository_root,
        find_tool=find_tool,
        run_command=run_command,
    )
    if final_godot_probe.status != PASS:
        _print_manual_godot_installation(host, toolchain.required_godot_major)

    report = collect_doctor_report(
        start=layout.repository_root,
        find_tool=find_tool,
        run_command=run_command,
    )
    print(format_doctor_report(report))
    if report.exit_code != 0:
        print_help_line(
            "Resolve the failed Doctor checks, then run `python tools/control.py doctor` again."
        )
    else:
        success("Forge2D Template environment is ready.")
    return report.exit_code


def _load_toolchain(layout: RepositoryLayout) -> ToolchainConfig:
    try:
        return load_toolchain_config(layout.toolchain_config)
    except ToolchainConfigError as exc:
        raise InstallError(
            f"Cannot read toolchain requirements: {exc}",
            (f"Review {layout.toolchain_config} and correct its TOML values.",),
        ) from exc


def _detect_host(
    *,
    system_name: str | None,
    distribution: str | None,
    find_tool: ToolFinder,
    is_elevated: bool | None,
) -> HostEnvironment:
    system = system_name or platform.system()
    detected_distribution = distribution
    if system == "Linux" and detected_distribution is None:
        detected_distribution = _linux_distribution()

    manager: str | None = None
    if system == "Linux":
        if detected_distribution in ARCH_DISTRIBUTIONS and find_tool("pacman") is not None:
            manager = "pacman"
        elif find_tool("apt-get") is not None:
            manager = "apt"
        elif find_tool("pacman") is not None:
            manager = "pacman"
    elif system == "Windows" and find_tool("winget") is not None:
        manager = "winget"
    elif system == "Darwin" and find_tool("brew") is not None:
        manager = "brew"

    elevated = is_elevated
    if elevated is None:
        get_effective_user_id = getattr(os, "geteuid", None)
        elevated = bool(get_effective_user_id is not None and get_effective_user_id() == 0)

    return HostEnvironment(
        system=system,
        distribution=detected_distribution,
        package_manager=manager,
        elevated=elevated,
        sudo_available=find_tool("sudo") is not None,
    )


def _probe_python_bootstrap(
    python_executable: str,
    run_command: CommandRunner,
) -> PythonBootstrapProbe:
    venv_result = run_command((python_executable, "-c", "import venv"))
    pip_result = run_command((python_executable, "-m", "ensurepip", "--version"))
    return PythonBootstrapProbe(
        venv_available=venv_result.returncode == 0,
        pip_seed_available=pip_result.returncode == 0,
        venv_detail=_result_detail(venv_result, "standard-library venv module is available"),
        pip_detail=_result_detail(pip_result, "ensurepip can seed pip inside .venv"),
    )


def _print_python_version_status(
    observed: tuple[int, int],
    minimum: tuple[int, int],
) -> None:
    if observed >= minimum:
        print_status_line(
            "pass",
            "Python",
            f"{observed[0]}.{observed[1]} satisfies >= {minimum[0]}.{minimum[1]}",
        )
    else:
        print_status_line(
            "fail",
            "Python",
            f"{observed[0]}.{observed[1]} is below required {minimum[0]}.{minimum[1]}",
        )


def _print_bootstrap_status(
    probe: PythonBootstrapProbe,
    *,
    existing_venv_ready: bool,
) -> None:
    fallback = "; existing .venv pip remains usable" if existing_venv_ready else ""
    print_status_line(
        "pass" if probe.venv_available else ("warn" if existing_venv_ready else "fail"),
        "Python venv",
        probe.venv_detail + (fallback if not probe.venv_available else ""),
    )
    print_status_line(
        "pass"
        if probe.pip_seed_available
        else ("warn" if existing_venv_ready else "fail"),
        "pip bootstrap",
        probe.pip_detail + (fallback if not probe.pip_seed_available else ""),
    )


def _print_godot_status(probe: GodotProbeResult) -> None:
    print_status_line(
        "pass" if probe.status == PASS else "fail",
        "Godot",
        probe.detail,
    )


def _build_system_plan(
    host: HostEnvironment,
    *,
    need_python: bool,
    need_bootstrap: bool,
    need_godot: bool,
    minimum_python: tuple[int, int],
    required_godot_major: int,
    yes: bool,
    find_tool: ToolFinder,
    run_command: CommandRunner,
) -> SystemPlan:
    manager = host.package_manager
    notes: list[str] = []
    actions: list[SystemAction] = []
    python_planned = False
    bootstrap_planned = False
    godot_planned = False

    if not any((need_python, need_bootstrap, need_godot)):
        return SystemPlan((), ())
    if manager is None:
        notes.append("No supported package manager was detected for missing system requirements.")
        return SystemPlan((), tuple(notes))

    prefix = _elevation_prefix(host)
    if prefix is None:
        notes.append(
            f"{manager} needs elevated privileges, but neither root access nor sudo is available."
        )
        return SystemPlan((), tuple(notes))

    if manager == "apt":
        packages: list[str] = []
        if need_python:
            packages.extend(("python3", "python3-venv"))
            python_planned = True
            bootstrap_planned = True
        elif need_bootstrap:
            packages.append("python3-venv")
            bootstrap_planned = True

        if need_godot:
            candidate_major = _apt_godot_candidate_major(find_tool, run_command)
            if candidate_major == required_godot_major:
                packages.append("godot")
                godot_planned = True
            elif candidate_major is None:
                notes.append(
                    "APT does not expose a verifiable `godot` package; refusing an "
                    "ambiguous install."
                )
            else:
                notes.append(
                    f"APT offers Godot {candidate_major}.x, but this repository requires "
                    f"Godot {required_godot_major}.x; refusing the incompatible package."
                )

        packages = list(dict.fromkeys(packages))
        if packages:
            actions.append(
                SystemAction(
                    "Refresh APT package metadata",
                    (*prefix, "apt-get", "update"),
                    "Check network access and configured APT repositories, then run "
                    "`apt-get update`.",
                )
            )
            install_flags = ("--yes",) if yes else ()
            actions.append(
                SystemAction(
                    "Install required APT packages",
                    (
                        *prefix,
                        "apt-get",
                        "install",
                        *install_flags,
                        "--no-install-recommends",
                        *packages,
                    ),
                    "Install the listed packages manually with APT, then re-run the installer.",
                )
            )

    elif manager == "pacman":
        packages = []
        if need_python or need_bootstrap:
            packages.append("python")
            python_planned = need_python
            bootstrap_planned = True
        if need_godot:
            packages.append("godot")
            godot_planned = True
        pacman_flags = ("--noconfirm",) if yes else ()
        actions.append(
            SystemAction(
                "Install required Pacman packages",
                (
                    *prefix,
                    "pacman",
                    "-S",
                    "--needed",
                    *pacman_flags,
                    *packages,
                ),
                "Synchronize Arch repositories and install the listed packages with Pacman.",
            )
        )

    elif manager == "winget":
        agreement_flags = (
            ("--accept-package-agreements", "--accept-source-agreements") if yes else ()
        )
        if need_python or need_bootstrap:
            python_id = f"Python.Python.{minimum_python[0]}.{minimum_python[1]}"
            actions.append(
                SystemAction(
                    "Install supported Python with Winget",
                    (
                        "winget",
                        "install",
                        "--id",
                        python_id,
                        "--exact",
                        "--source",
                        "winget",
                        *agreement_flags,
                    ),
                    f"Run `winget install --id {python_id} --exact --source winget` "
                    "in a new terminal.",
                )
            )
            python_planned = need_python
            bootstrap_planned = True
        if need_godot:
            actions.append(
                SystemAction(
                    "Install Godot 4 with Winget",
                    (
                        "winget",
                        "install",
                        "--id",
                        "GodotEngine.GodotEngine",
                        "--exact",
                        "--source",
                        "winget",
                        *agreement_flags,
                    ),
                    "Install package `GodotEngine.GodotEngine` with Winget and open "
                    "a new terminal.",
                )
            )
            godot_planned = True

    elif manager == "brew":
        if need_python or need_bootstrap:
            formula = f"python@{minimum_python[0]}.{minimum_python[1]}"
            actions.append(
                SystemAction(
                    "Install supported Python with Homebrew",
                    ("brew", "install", formula),
                    f"Run `brew install {formula}`, then use its python executable for setup.",
                )
            )
            python_planned = need_python
            bootstrap_planned = True
        if need_godot:
            actions.append(
                SystemAction(
                    "Install Godot 4 with Homebrew",
                    ("brew", "install", "--cask", "godot"),
                    "Run `brew install --cask godot`, then ensure the Godot command is on PATH.",
                )
            )
            godot_planned = True

    return SystemPlan(
        actions=tuple(actions),
        notes=tuple(notes),
        python_planned=python_planned,
        bootstrap_planned=bootstrap_planned,
        godot_planned=godot_planned,
    )


def _elevation_prefix(host: HostEnvironment) -> tuple[str, ...] | None:
    if host.package_manager not in {"apt", "pacman"} or host.elevated:
        return ()
    if host.sudo_available:
        return ("sudo",)
    return None


def _apt_godot_candidate_major(
    find_tool: ToolFinder,
    run_command: CommandRunner,
) -> int | None:
    if find_tool("apt-cache") is None:
        return None
    result = run_command(("apt-cache", "policy", "godot"))
    if result.returncode != 0:
        return None
    match = APT_CANDIDATE.search(result.stdout)
    return int(match.group("major")) if match is not None else None


def _apply_system_plan(
    plan: SystemPlan,
    *,
    dry_run: bool,
    yes: bool,
    confirm: Callable[[str], str],
    run_command: CommandRunner,
) -> bool:
    for note in plan.notes:
        warning(note)
    if not plan.actions:
        return False

    for action in plan.actions:
        if dry_run:
            print_dry_run(f"{action.description}: {join_command(action.command)}")
        else:
            print_command_plan(f"{action.description}: {join_command(action.command)}")
    if dry_run:
        return False

    if not yes and not _confirmed(
        "Run the package-manager commands shown above? [y/N]: ", confirm
    ):
        warning("System package installation was declined; continuing with available tools.")
        return False

    for action in plan.actions:
        _run_or_fail(
            action.command,
            action.description,
            run_command,
            solutions=(action.recovery,),
        )
    return True


def _confirmed(question: str, confirm: Callable[[str], str]) -> bool:
    try:
        return confirm(question).strip().lower() in CONFIRMED_ANSWERS
    except EOFError as exc:
        raise InstallError(
            "Confirmation input is unavailable.",
            ("Re-run with `--yes` for unattended installation or use an interactive terminal.",),
        ) from exc


def _ensure_venv(
    venv_directory: Path,
    *,
    system_name: str,
    installer_python: str,
    dry_run: bool,
    yes: bool,
    run_command: CommandRunner,
    confirm: Callable[[str], str],
) -> Path:
    venv_python = _venv_python_path(venv_directory, system_name=system_name)
    if _venv_has_pip(venv_python, run_command):
        print_status_line("pass", ".venv pip", f"available at {venv_python}")
        return venv_python

    replacing = venv_directory.exists()
    command = [installer_python, "-m", "venv"]
    if replacing:
        command.append("--clear")
    command.append(str(venv_directory))
    description = "Recreate invalid .venv" if replacing else "Create repository .venv"
    if dry_run:
        print_dry_run(f"{description}: {join_command(command)}")
        return venv_python

    if replacing and not yes and not _confirmed(
        f"The existing {venv_directory} has no working pip. Recreate it? [y/N]: ",
        confirm,
    ):
        raise InstallError(
            f"Existing virtual environment is incomplete: {venv_directory}",
            ("Re-run with `--yes` to recreate only the repository-local .venv.",),
        )

    _run_or_fail(
        command,
        description,
        run_command,
        solutions=(
            _venv_failure_instruction(system_name),
            f"Remove or repair only {venv_directory}, then re-run the installer.",
        ),
    )
    if not _venv_has_pip(venv_python, run_command):
        raise InstallError(
            f"Virtual environment creation completed without a working pip at {venv_python}.",
            (
                _venv_failure_instruction(system_name),
                "Do not install project packages into system Python; repair venv support instead.",
            ),
        )
    print_status_line("pass", ".venv pip", f"available at {venv_python}")
    return venv_python


def _venv_has_pip(venv_python: Path, run_command: CommandRunner) -> bool:
    if not venv_python.exists():
        return False
    result = run_command((str(venv_python), "-m", "pip", "--version"))
    return result.returncode == 0


def _install_local_tooling(
    layout: RepositoryLayout,
    *,
    toolchain: ToolchainConfig,
    venv_python: Path,
    dry_run: bool,
    run_command: CommandRunner,
) -> None:
    dependencies = tuple(
        dict.fromkeys(toolchain.runtime_dependencies + toolchain.development_dependencies)
    )
    pip_prefix = [str(venv_python), "-m", "pip", "--disable-pip-version-check"]
    local_command = [*pip_prefix, "install", "-e", str(layout.repository_root)]
    dependency_command = [*pip_prefix, "install", *dependencies]
    check_command = [*pip_prefix, "check"]

    if dry_run:
        print_dry_run(f"Install local tooling in .venv: {join_command(local_command)}")
        if dependencies:
            print_dry_run(
                "Install declared Python packages in .venv: "
                + join_command(dependency_command)
            )
        print_dry_run(f"Verify .venv dependency consistency: {join_command(check_command)}")
        for requirement in dependencies:
            package_name = _requirement_name(requirement)
            print_dry_run(
                "Verify required package in .venv: "
                + join_command([*pip_prefix, "show", package_name])
            )
        return

    _run_or_fail(
        local_command,
        "Install local tooling into .venv",
        run_command,
        solutions=(
            "Check network access and pyproject.toml build requirements.",
            "Run the displayed command with the .venv Python; never use system pip.",
        ),
    )
    if dependencies:
        _run_or_fail(
            dependency_command,
            "Install declared Python packages into .venv",
            run_command,
            solutions=(
                "Check requirement strings in config/toolchain.toml and package index access.",
            ),
        )
    _run_or_fail(
        check_command,
        "Verify .venv dependency consistency",
        run_command,
        solutions=("Resolve the packages reported by `.venv` pip check, then re-run install.",),
    )
    for requirement in dependencies:
        package_name = _requirement_name(requirement)
        _run_or_fail(
            [*pip_prefix, "show", package_name],
            f"Verify required Python package {requirement}",
            run_command,
            solutions=(
                f"Install `{requirement}` with `{venv_python} -m pip install {requirement}`.",
            ),
        )


def _requirement_name(requirement: str) -> str:
    match = REQUIREMENT_NAME.match(requirement)
    if match is None:
        raise InstallError(
            f"Cannot determine package name from requirement {requirement!r}.",
            ("Correct the requirement in config/toolchain.toml.",),
        )
    return match.group(0)


def _run_or_fail(
    command: Sequence[str],
    description: str,
    run_command: CommandRunner,
    *,
    solutions: Sequence[str] = (),
) -> None:
    print_status_line("running", description, join_command(command))
    result = run_command(command)
    if result.returncode == 0:
        return
    detail = (result.stderr or result.stdout).strip()
    if not detail:
        detail = "the command produced no diagnostic output"
    if len(detail) > 1200:
        detail = detail[-1200:]
    raise InstallError(
        f"{description} exited with code {result.returncode}: {detail}",
        (f"Command: {join_command(command)}", *solutions),
    )


def _print_manual_godot_installation(
    host: HostEnvironment,
    required_major: int,
) -> None:
    warning(f"Godot {required_major}.x still requires manual installation.")
    if host.system == "Linux":
        print_help_line(
            "Use a trusted distribution package that explicitly provides Godot 4, "
            "or download it from https://godotengine.org/download/linux/."
        )
    elif host.system == "Windows":
        print_help_line(
            "Install `GodotEngine.GodotEngine` with Winget or use "
            "https://godotengine.org/download/windows/."
        )
    elif host.system == "Darwin":
        print_help_line(
            "Install with `brew install --cask godot` or use "
            "https://godotengine.org/download/macos/."
        )
    else:
        print_help_line("Use the official download at https://godotengine.org/download/.")
    print_help_line("After installation, ensure `godot4` or `godot` is on PATH and run Doctor.")


def _python_rerun_instruction(
    host: HostEnvironment,
    minimum: tuple[int, int],
) -> str:
    version = f"{minimum[0]}.{minimum[1]}"
    if host.system == "Windows":
        return f"Open a new terminal and run `py -{version} tools/control.py install`."
    return f"Run `python{version} tools/control.py install` with the newly installed interpreter."


def _python_bootstrap_instruction(host: HostEnvironment) -> str:
    if host.package_manager == "apt":
        return "Install venv support with `sudo apt-get install python3-venv`."
    if host.package_manager == "pacman":
        return "Repair the Python package with `sudo pacman -S --needed python`."
    if host.package_manager == "winget":
        return "Repair or reinstall supported Python with Winget, then open a new terminal."
    if host.package_manager == "brew":
        return "Repair or reinstall the selected Homebrew Python formula."
    return "Install Python with its standard venv and ensurepip components."


def _venv_failure_instruction(system_name: str) -> str:
    if system_name == "Linux":
        return "Install your distribution's Python venv package (for APT: `python3-venv`)."
    if system_name == "Windows":
        return "Repair the Python installation and include pip and the standard library."
    if system_name == "Darwin":
        return "Repair the selected Python installation or Homebrew Python formula."
    return "Install Python with venv and ensurepip support."


def _venv_python_path(venv_directory: Path, *, system_name: str) -> Path:
    return (
        venv_directory / "Scripts" / "python.exe"
        if system_name == "Windows"
        else venv_directory / "bin" / "python"
    )


def _result_detail(result: CommandResult, success_detail: str) -> str:
    if result.returncode == 0:
        output = (result.stdout or result.stderr).strip()
        return output or success_detail
    detail = (result.stderr or result.stdout).strip()
    return detail or f"probe exited with code {result.returncode}"


def _run_command(arguments: Sequence[str]) -> CommandResult:
    try:
        completed = subprocess.run(
            list(arguments),
            check=False,
            capture_output=True,
            text=True,
            timeout=900,
        )
    except FileNotFoundError as exc:
        return CommandResult(127, "", f"command not found: {exc.filename}")
    except subprocess.TimeoutExpired:
        return CommandResult(124, "", "command timed out after 900 seconds")
    except OSError as exc:
        return CommandResult(1, "", f"operating-system error: {exc}")
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def _linux_distribution() -> str | None:
    if platform.system() != "Linux":
        return None
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        return None
    try:
        lines = os_release.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        if line.startswith("ID="):
            return line.removeprefix("ID=").strip().strip('"').lower()
    return None
