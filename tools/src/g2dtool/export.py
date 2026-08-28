"""Create validated Godot release exports below the repository artifact root."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
import os
import platform
import re
import shutil
import subprocess
import zipfile

from g2dtool.godot import CommandResult, PASS, discover_godot
from g2dtool.logger import (
    error,
    join_command,
    print_dry_run,
    print_help_line,
    running,
    success,
)
from g2dtool.repository import RepositoryLayout, discover_repository_layout


CommandRunner = Callable[[Sequence[str], int], CommandResult]
EXPORT_TIMEOUT_SECONDS = 600
TEMPLATE_VERSION = re.compile(
    r"(?P<version>\d+\.\d+(?:\.\d+)?)"
    r"(?:\.(?P<status>stable|beta\d*|rc\d*|dev\d*))?"
)
ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


class ExportError(RuntimeError):
    """Expected export failure with concrete recovery steps."""

    def __init__(self, cause: str, solutions: Sequence[str] = ()) -> None:
        super().__init__(cause)
        self.cause = cause
        self.solutions = tuple(solutions)


@dataclass(frozen=True, slots=True)
class ExportTarget:
    """Reviewed target metadata shared by presets, tooling, tests, and CI."""

    key: str
    preset_name: str
    godot_platform: str
    output_relative: Path
    preset_output: str
    template_file: str
    artifact_kind: str


EXPORT_TARGETS: Mapping[str, ExportTarget] = {
    "linux": ExportTarget(
        key="linux",
        preset_name="Linux",
        godot_platform="Linux",
        output_relative=Path(
            "artifacts/exports/linux/Forge2D-Template.x86_64"
        ),
        preset_output="../artifacts/exports/linux/Forge2D-Template.x86_64",
        template_file="linux_release.x86_64",
        artifact_kind="elf",
    ),
    "windows": ExportTarget(
        key="windows",
        preset_name="Windows",
        godot_platform="Windows Desktop",
        output_relative=Path("artifacts/exports/windows/Forge2D-Template.exe"),
        preset_output="../artifacts/exports/windows/Forge2D-Template.exe",
        template_file="windows_release_x86_64.exe",
        artifact_kind="pe",
    ),
    "macos": ExportTarget(
        key="macos",
        preset_name="macOS",
        godot_platform="macOS",
        output_relative=Path("artifacts/exports/macos/Forge2D-Template.zip"),
        preset_output="../artifacts/exports/macos/Forge2D-Template.zip",
        template_file="macos.zip",
        artifact_kind="zip",
    ),
}


def build_export_command(
    executable: Path,
    game_directory: Path,
    target: ExportTarget,
    output_path: Path,
) -> tuple[str, ...]:
    """Return the deterministic headless release-export command."""

    return (
        str(executable),
        "--headless",
        "--path",
        str(game_directory),
        "--export-release",
        target.preset_name,
        str(output_path),
    )


def run_export(
    target_name: str,
    *,
    start: Path | None = None,
    dry_run: bool = False,
    run_command: CommandRunner | None = None,
    find_tool: Callable[[str], str | None] = shutil.which,
    system_name: str | None = None,
    environment: Mapping[str, str] | None = None,
    home_directory: Path | None = None,
) -> int:
    """Export one reviewed target and report expected failures without tracebacks."""

    try:
        return _run_export(
            target_name,
            start=start,
            dry_run=dry_run,
            run_command=run_command or _run_command,
            find_tool=find_tool,
            system_name=system_name,
            environment=environment,
            home_directory=home_directory,
        )
    except ExportError as exc:
        error(f"Export failed: {exc.cause}")
        for solution in exc.solutions:
            print_help_line(solution)
        return 1


def export_template_candidates(
    executable: Path,
    godot_version: str,
    template_file: str,
    *,
    system_name: str | None = None,
    environment: Mapping[str, str] | None = None,
    home_directory: Path | None = None,
) -> tuple[Path, ...]:
    """Return the standard paths Godot checks for an official export template."""

    system = system_name or platform.system()
    env = os.environ if environment is None else environment
    home = Path.home() if home_directory is None else home_directory
    version_directory = _template_version_directory(godot_version)
    candidates: list[Path] = []

    portable_root = _portable_editor_root(executable)
    if any((portable_root / marker).is_file() for marker in ("._sc_", "_sc_")):
        candidates.append(
            portable_root
            / "editor_data"
            / "export_templates"
            / version_directory
            / template_file
        )

    if system == "Linux":
        configured_data = Path(env.get("XDG_DATA_HOME", ""))
        if not configured_data.is_absolute():
            configured_data = home / ".local" / "share"
        data_root = configured_data / "godot"
    elif system == "Darwin":
        data_root = home / "Library" / "Application Support" / "Godot"
    elif system == "Windows":
        app_data = env.get("APPDATA")
        data_root = Path(app_data) / "Godot" if app_data else Path.cwd() / "Godot"
    else:
        data_root = None

    if data_root is not None:
        candidates.append(
            data_root / "export_templates" / version_directory / template_file
        )
    return tuple(candidates)


def _run_export(
    target_name: str,
    *,
    start: Path | None,
    dry_run: bool,
    run_command: CommandRunner,
    find_tool: Callable[[str], str | None],
    system_name: str | None,
    environment: Mapping[str, str] | None,
    home_directory: Path | None,
) -> int:
    target = EXPORT_TARGETS.get(target_name)
    if target is None:
        choices = ", ".join(EXPORT_TARGETS)
        raise ExportError(
            f"Unsupported target {target_name!r}.",
            (f"Choose one of: {choices}.",),
        )

    layout = discover_repository_layout(start)
    output_path = _validated_output_path(layout, target)
    _validate_export_preset(layout.export_presets_path, target)

    probe = discover_godot(layout.repository_root, find_tool=find_tool)
    if probe.status != PASS or probe.executable is None or probe.version is None:
        detail = probe.detail.rstrip(".")
        raise ExportError(
            f"Godot 4 is unavailable. {detail}.",
            (
                "Run `python tools/control.py install` to install or locate Godot 4.",
                "Run `python tools/control.py doctor` for the complete toolchain report.",
            ),
        )

    candidates = export_template_candidates(
        probe.executable,
        probe.version,
        target.template_file,
        system_name=system_name,
        environment=environment,
        home_directory=home_directory,
    )
    _require_export_template(target, probe.version, candidates)
    command = build_export_command(
        probe.executable,
        layout.game_directory,
        target,
        output_path,
    )

    if dry_run:
        print_dry_run(
            f"Would create the {target.preset_name} release export at "
            f"{target.output_relative.as_posix()}"
        )
        print_dry_run(join_command(command))
        success("Export dry-run complete; no changes were made.")
        return 0

    _prepare_output(output_path, layout.repository_root)
    running(join_command(command))
    try:
        result = run_command(command, EXPORT_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired as exc:
        raise ExportError(
            f"Godot did not finish within {EXPORT_TIMEOUT_SECONDS} seconds.",
            (
                "Close other Godot processes, verify available disk space, and retry.",
                "Run the printed command manually to inspect long-running import work.",
            ),
        ) from exc
    except (FileNotFoundError, OSError) as exc:
        raise ExportError(
            f"Godot could not be started: {exc}.",
            ("Run `python tools/control.py doctor` and repair the Godot executable.",),
        ) from exc

    if result.returncode != 0:
        output = _summarize_process_output(result.stdout, result.stderr)
        cause = f"Godot exited with code {result.returncode}"
        if output:
            cause += f": {output}"
        raise ExportError(
            cause,
            (
                "Confirm the matching export templates are installed for this Godot version.",
                "Open the project in Godot and review Project > Export for preset errors.",
            ),
        )

    size = _validate_artifact(output_path, target)
    success(
        f"{target.preset_name} release export created: "
        f"{target.output_relative.as_posix()} ({size} bytes)."
    )
    return 0


def _validated_output_path(
    layout: RepositoryLayout,
    target: ExportTarget,
) -> Path:
    repository_root = layout.repository_root.resolve()
    artifact_root = layout.export_directory.resolve(strict=False)
    output_path = repository_root / target.output_relative
    output_parent = output_path.parent.resolve(strict=False)

    if not artifact_root.is_relative_to(repository_root):
        raise ExportError(
            f"Artifact directory resolves outside the repository: {artifact_root}.",
            ("Replace the artifacts path with a normal directory inside the checkout.",),
        )
    if not output_parent.is_relative_to(artifact_root):
        raise ExportError(
            f"Export destination resolves outside {layout.export_directory}.",
            ("Remove symlinks that redirect the selected export directory.",),
        )
    return output_path


def _validate_export_preset(path: Path, target: ExportTarget) -> None:
    if not path.is_file():
        raise ExportError(
            f"Godot export presets are missing: {path}.",
            ("Restore game/export_presets.cfg from the repository.",),
        )
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ExportError(
            f"Godot export presets cannot be read as UTF-8: {exc}.",
            ("Restore a readable UTF-8 game/export_presets.cfg file.",),
        ) from exc

    expected = {
        "name": f'"{target.preset_name}"',
        "platform": f'"{target.godot_platform}"',
        "export_path": f'"{target.preset_output}"',
    }
    preset_sections = re.finditer(
        r"(?ms)^\[preset\.\d+\]\s*$\n(?P<body>.*?)(?=^\[|\Z)",
        text,
    )
    for preset_section in preset_sections:
        section = preset_section.group("body")
        settings = dict(
            re.findall(r"(?m)^([a-z_]+)=(.+)$", section)
        )
        if settings.get("name") != expected["name"]:
            continue
        mismatches = [
            key for key, value in expected.items() if settings.get(key) != value
        ]
        if not mismatches:
            return
        raise ExportError(
            f"Preset {target.preset_name!r} has invalid settings: "
            f"{', '.join(mismatches)}.",
            ("Restore the reviewed preset from game/export_presets.cfg.",),
        )

    raise ExportError(
        f"Preset {target.preset_name!r} is missing from {path}.",
        ("Restore the reviewed preset from game/export_presets.cfg.",),
    )


def _require_export_template(
    target: ExportTarget,
    godot_version: str,
    candidates: Sequence[Path],
) -> Path:
    for candidate in candidates:
        try:
            if candidate.is_file() and candidate.stat().st_size > 0:
                return candidate
        except OSError:
            continue

    expected = ", ".join(map(str, candidates)) or "Godot's editor data directory"
    version_directory = _template_version_directory(godot_version)
    raise ExportError(
        f"Required template {target.template_file!r} was not found for "
        f"Godot {version_directory}. Expected: {expected}.",
        (
            "In Godot, use Editor > Manage Export Templates to install the matching version.",
            "Use only the official checksum-verified template archive, then retry the dry-run.",
        ),
    )


def _prepare_output(output_path: Path, repository_root: Path) -> None:
    if output_path.is_symlink() or (
        output_path.exists() and not output_path.is_file()
    ):
        raise ExportError(
            f"Refusing to replace non-regular export destination: {output_path}.",
            ("Move that path aside manually, then retry the export.",),
        )
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_parent = output_path.parent.resolve(strict=True)
        if not resolved_parent.is_relative_to(repository_root.resolve()):
            raise ExportError(
                f"Export directory escaped the repository: {resolved_parent}.",
                ("Remove symlinks beneath artifacts/exports and retry.",),
            )
        if output_path.exists():
            output_path.unlink()
    except ExportError:
        raise
    except OSError as exc:
        raise ExportError(
            f"Export destination cannot be prepared: {exc}.",
            ("Check repository permissions and available disk space, then retry.",),
        ) from exc


def _validate_artifact(output_path: Path, target: ExportTarget) -> int:
    try:
        if output_path.is_symlink() or not output_path.is_file():
            raise ExportError(
                f"Godot reported success but did not create {output_path}.",
                ("Review Godot's Project > Export messages and retry.",),
            )
        size = output_path.stat().st_size
        if size == 0:
            raise ExportError(
                f"Godot created an empty export: {output_path}.",
                ("Reinstall the matching export templates and retry.",),
            )
        with output_path.open("rb") as artifact_file:
            header = artifact_file.read(4)
    except ExportError:
        raise
    except OSError as exc:
        raise ExportError(
            f"Export artifact cannot be inspected: {exc}.",
            ("Check artifact permissions and available disk space.",),
        ) from exc

    valid = True
    if target.artifact_kind == "elf":
        valid = header == b"\x7fELF"
    elif target.artifact_kind == "pe":
        valid = header.startswith(b"MZ")
    elif target.artifact_kind == "zip":
        valid = zipfile.is_zipfile(output_path)
    if not valid:
        raise ExportError(
            f"Export has an invalid {target.artifact_kind.upper()} signature: {output_path}.",
            ("Reinstall official export templates and run the export again.",),
        )
    return size


def _template_version_directory(godot_version: str) -> str:
    match = TEMPLATE_VERSION.search(godot_version)
    if match is None:
        raise ExportError(
            f"Cannot determine the export-template version from {godot_version!r}.",
            ("Run `godot4 --version` and install a standard Godot 4 release.",),
        )
    status = match.group("status") or "stable"
    return f"{match.group('version')}.{status}"


def _portable_editor_root(executable: Path) -> Path:
    parent = executable.parent
    if parent.name == "MacOS" and parent.parent.name == "Contents":
        return parent.parents[2]
    return parent


def _summarize_process_output(stdout: str, stderr: str) -> str:
    lines = [
        line.strip()
        for line in f"{stdout}\n{stderr}".splitlines()
        if line.strip()
    ]
    return ANSI_ESCAPE.sub("", " | ".join(lines[-6:]))[:1200]


def _run_command(arguments: Sequence[str], timeout_seconds: int) -> CommandResult:
    process = subprocess.run(
        list(arguments),
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    return CommandResult(process.returncode, process.stdout, process.stderr)
