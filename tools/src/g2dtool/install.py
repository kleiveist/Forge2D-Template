"""Prepare and verify a local Forge2D development environment."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path
import os
import platform
import shutil
import subprocess
import sys

from g2dtool.config import load_toolchain_config, ToolchainConfigError
from g2dtool.doctor import (
    collect_doctor_report,
    format_doctor_report,
)
from g2dtool.godot import PASS, discover_godot
from g2dtool.repository import discover_repository_layout
from g2dtool.logger import (
    error,
    info,
    join_command,
    print_dry_run,
    print_help_line,
    print_status_line,
)

ToolFinder = Callable[[str], str | None]
CommandRunner = Callable[[Sequence[str]], "CommandResult"]


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


def run_install(
    *,
    start: Path | None = None,
    dry_run: bool = False,
    yes: bool = False,
    run_command: CommandRunner | None = None,
    find_tool: ToolFinder = shutil.which,
    confirm: Callable[[str], str] | None = None,
) -> int:
    """Create/prepare local tooling and run doctor afterwards."""

    layout = discover_repository_layout(start)
    runner = run_command or _run_command
    prompt = confirm or (lambda text: input(text))

    info(f"Preparing Forge2D environment in {layout.repository_root}")
    distribution = _linux_distribution() or "not detected"
    info(f"Detected platform: {platform.system()} ({distribution})")

    _handle_system_dependencies(
        layout,
        distribution=distribution,
        dry_run=dry_run,
        yes=yes,
        find_tool=find_tool,
        run_command=runner,
        confirm=prompt,
    )
    _ensure_venv(layout.venv_directory, dry_run=dry_run, run_command=runner)
    _install_local_tooling(layout.venv_directory, dry_run=dry_run, run_command=runner, start=layout.repository_root)

    report = collect_doctor_report(
        start=layout.repository_root,
        find_tool=find_tool,
        run_command=runner,
    )
    print(format_doctor_report(report))
    return report.exit_code


def _handle_system_dependencies(
    layout,
    *,
    distribution: str,
    dry_run: bool,
    yes: bool,
    find_tool: ToolFinder,
    run_command: CommandRunner,
    confirm: Callable[[str], str],
) -> None:
    probe = discover_godot(layout.repository_root, find_tool=find_tool, run_command=run_command)
    if probe.status == PASS:
        return
    info(f"Godot probe failed: {probe.detail}")
    if probe.status != PASS and "runtime library mismatch" in probe.detail.lower():
        print_help_line("Possible binary/runtime mismatch: install a matching Godot 4 package or use flatpak/appimage.")

    pacman_command = ["sudo", "pacman", "-S", "--needed", "godot"]
    if distribution == "arch":
        if find_tool("pacman") is None:
            _print_manual_godot_installation()
            return

        if dry_run:
            _print_dry_run(pacman_command)
            return
        if yes:
            _run_or_fail(pacman_command, "Install system godot", run_command)
            return

        answer = confirm(
            f"Install Godot 4 now with: {' '.join(pacman_command)}? [y/N]: "
        ).strip().lower()
        if answer in {"y", "yes"}:
            _run_or_fail(pacman_command, "Install system godot", run_command)

    _print_manual_godot_installation()


def _ensure_venv(
    venv_directory: Path,
    *,
    dry_run: bool,
    run_command: CommandRunner,
) -> None:
    venv_python = _venv_python_path(venv_directory)
    if venv_python.exists():
        return

    command = [sys.executable, "-m", "venv", str(venv_directory)]
    if dry_run:
        _print_dry_run(command)
        return
    _run_or_fail(command, "Create .venv", run_command)


def _install_local_tooling(
    venv_directory: Path,
    *,
    dry_run: bool,
    run_command: CommandRunner,
    start: Path,
) -> None:
    venv_python = _venv_python_path(venv_directory)
    try:
        toolchain = load_toolchain_config(start / "config" / "toolchain.toml")
    except ToolchainConfigError as error:
        raise RuntimeError(f"Failed to read toolchain configuration: {error}") from error

    dependencies = tuple(dict.fromkeys(toolchain.runtime_dependencies + toolchain.development_dependencies))

    if dry_run:
        _print_dry_run([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
        _print_dry_run([str(venv_python), "-m", "pip", "install", "-e", "."])
        if dependencies:
            _print_dry_run([str(venv_python), "-m", "pip", "install", *dependencies])
        return

    _run_or_fail(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
        "Upgrade pip",
        run_command,
    )
    _run_or_fail(
        [str(venv_python), "-m", "pip", "install", "-e", "."],
        "Install local tooling",
        run_command,
    )
    if dependencies:
        _run_or_fail(
            [str(venv_python), "-m", "pip", "install", *dependencies],
            "Install declared toolchain dependencies",
            run_command,
        )


def _run_or_fail(command: Sequence[str], description: str, run_command: CommandRunner) -> None:
    print_status_line("running", description, join_command(command))
    result = run_command(command)
    if result[0] != 0:
        raise RuntimeError(f"{description} failed: {result[2]}")


def _print_dry_run(command: Sequence[str]) -> None:
    print_dry_run(join_command(command))


def _print_manual_godot_installation() -> None:
    error("Godot 4 was not found.")
    print_help_line("Bitte installieren Sie Godot 4 manuell.")
    print_help_line("  - Linux: install the godot package from your distribution")
    print_help_line("  - Arch Linux (empfohlen): sudo pacman -S --needed godot")
    print_help_line("Danach erneut prüfen:")
    print_help_line("  python tools/control.py doctor")


def _venv_python_path(venv_directory: Path) -> Path:
    return (
        venv_directory / "Scripts" / "python.exe"
        if os.name == "nt"
        else venv_directory / "bin" / "python"
    )


def _run_command(arguments: Sequence[str]) -> CommandResult:
    completed = subprocess.run(
        list(arguments),
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def _linux_distribution() -> str | None:
    if platform.system() != "Linux":
        return None
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        return None
    for line in os_release.read_text(encoding="utf-8").splitlines():
        if line.startswith("ID="):
            return line.removeprefix("ID=").strip().strip('"')
    return None
