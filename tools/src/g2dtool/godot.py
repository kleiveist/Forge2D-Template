"""Godot binary discovery and command helpers."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
import os
import re
import shutil
import subprocess

from g2dtool.config import ToolchainConfigError, load_toolchain_config


ToolFinder = Callable[[str], str | None]


class CommandResult(tuple[int, str, str]):
    """Compatibility tuple used by runners in tests and subprocess wrappers."""

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


@dataclass(frozen=True, slots=True)
class GodotProbeResult:
    """Result of one Godot search step."""

    executable: Path | None
    version: str | None
    status: str
    detail: str


PASS = "pass"
WARN = "warn"
FAIL = "fail"

DEFAULT_TEST_MODE_ARGUMENT = "--test-mode"

PROJECT_MAIN_SCENE_RE = re.compile(r'^run/main_scene="res://([^"]+)"', re.MULTILINE)
SCENE_SCRIPT_RE = re.compile(r'path="res://([^"]+\.gd)"')
TEST_MODE_RE = re.compile(r'const\s+TEST_MODE_ARGUMENT\s*:\s*"([^"]+)"')
TEST_MODE_ALT_RE = re.compile(r'const\s+TEST_MODE_ARGUMENT\s*:=\s*"([^"]+)"')
GODOT_LABELED_VERSION_RE = re.compile(
    r"(?i)\bgodot\b.*?\bv?(?P<major>\d+)\.(?P<minor>\d+)"
)
GODOT_VERSION_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9_])(v?\d+\.\d+)")
GODOT_RUNTIME_LOAD_ERROR_RE = re.compile(
    r"(?i)(GLIBC_|libc\.so|libm\.so|libstdc\+\+|cannot open shared object file|not found)"
)


def discover_godot(
    repository_root: Path,
    *,
    explicit_binary: str | None = None,
    toolchain_config_path: Path | None = None,
    environment: Mapping[str, str] | None = None,
    required_major: int = 4,
    find_tool: ToolFinder = shutil.which,
    run_command: Callable[[Sequence[str]], CommandResult] | None = None,
) -> GodotProbeResult:
    """Find a Godot executable and ensure it reports the required major version."""

    environment = environment or os.environ
    runner = run_command or _run_command

    try:
        toolchain = load_toolchain_config(
            toolchain_config_path or repository_root / "config" / "toolchain.toml"
        )
        required_major = toolchain.required_godot_major
        configured_executable = toolchain.godot_binary
        candidate_names = toolchain.godot_executable_candidates
    except ToolchainConfigError:
        configured_executable = None
        candidate_names = ("godot4", "godot")

    preferred = explicit_binary or configured_executable
    ordered_candidates: list[str] = []
    if preferred:
        ordered_candidates.append(str(preferred))
    for name in ("GODOT4_BIN", "GODOT_BIN"):
        value = environment.get(name)
        if value:
            ordered_candidates.append(value)
    ordered_candidates.extend(candidate_names)

    seen: set[str] = set()
    attempts: list[str] = []
    failures: list[str] = []
    for candidate in ordered_candidates:
        if candidate in seen:
            continue
        seen.add(candidate)

        executable = _resolve_binary(candidate, repository_root, find_tool=find_tool)
        if executable is None:
            continue
        attempts.append(str(executable))
        result = runner((str(executable), "--version"))
        version_text = _combined_version_output(result)
        version = _extract_version_line(version_text)
        major_version = _extract_major_version(version)
        if major_version is None:
            if result.returncode != 0:
                failures.append(
                    _probe_failure_detail(str(executable), result.returncode, version_text)
                )
                continue
            return GodotProbeResult(
                executable=executable,
                version=version,
                status=FAIL,
                detail=f"Could not parse Godot version from {executable}.",
            )

        if major_version != required_major:
            return GodotProbeResult(
                executable=executable,
                version=version,
                status=FAIL,
                detail=(
                    f"Found Godot at {executable}, but version {version} is not "
                    f"Godot {required_major}.x."
                ),
            )

        if result.returncode != 0:
            return GodotProbeResult(
                executable=executable,
                version=version,
                status=PASS,
                detail=(
                    f"Godot {version} at {executable} (exit code {result.returncode}, "
                    "assuming compatibility from version output)."
                ),
            )

        return GodotProbeResult(
            executable=executable,
            version=version,
            status=PASS,
            detail=f"Godot {version} at {executable}.",
        )

    return GodotProbeResult(
        executable=None,
        version=None,
        status=FAIL,
        detail=_build_not_found_detail(
            attempts,
            ordered_candidates,
            failures,
        ),
    )


def _combined_version_output(result: CommandResult) -> str:
    return (result.stdout or result.stderr).strip()


def build_godot_editor_command(
    executable: Path,
    game_directory: Path,
    user_arguments: Sequence[str] = (),
) -> list[str]:
    return _extend_with_user_arguments(
        [str(executable), "--editor", "--path", str(game_directory)],
        user_arguments,
    )


def build_godot_run_command(
    executable: Path,
    game_directory: Path,
    user_arguments: Sequence[str] = (),
) -> list[str]:
    return _extend_with_user_arguments(
        [str(executable), "--path", str(game_directory)],
        user_arguments,
    )


def build_godot_test_command(
    executable: Path,
    game_directory: Path,
    project_file: Path,
    user_arguments: Sequence[str] = (),
) -> list[str]:
    test_argument = detect_project_test_argument(project_file)
    return [
        str(executable),
        "--headless",
        "--path",
        str(game_directory),
        "--",
        test_argument,
        *_normalize_user_arguments(user_arguments),
    ]


def detect_project_test_argument(project_file: Path) -> str:
    """Detect the project-specific test argument, with a safe fallback."""

    if not project_file.exists():
        return DEFAULT_TEST_MODE_ARGUMENT

    project_text = project_file.read_text(encoding="utf-8")
    main_scene_match = PROJECT_MAIN_SCENE_RE.search(project_text)
    if main_scene_match is None:
        return DEFAULT_TEST_MODE_ARGUMENT

    scene_path = _res_path_to_file(project_file.parent, main_scene_match.group(1))
    if scene_path is None or not scene_path.exists():
        return DEFAULT_TEST_MODE_ARGUMENT

    scene_text = scene_path.read_text(encoding="utf-8")
    script_match = SCENE_SCRIPT_RE.search(scene_text)
    if script_match is None:
        return DEFAULT_TEST_MODE_ARGUMENT

    script_path = _res_path_to_file(project_file.parent, script_match.group(1))
    if script_path is None or not script_path.exists():
        return DEFAULT_TEST_MODE_ARGUMENT

    script_text = script_path.read_text(encoding="utf-8")
    match = TEST_MODE_RE.search(script_text) or TEST_MODE_ALT_RE.search(script_text)
    if match is None:
        return DEFAULT_TEST_MODE_ARGUMENT
    return match.group(1)


def run_godot_command(arguments: Sequence[str]) -> int:
    """Run a pre-built Godot command and return the child process return code."""

    completed = subprocess.run(list(arguments), check=False)
    return int(completed.returncode)


def _resolve_binary(
    candidate: str,
    repository_root: Path,
    *,
    find_tool: ToolFinder,
) -> Path | None:
    path = Path(candidate)
    if path.is_absolute():
        return path if path.is_file() else None

    if candidate.startswith(".") or "/" in candidate or "\\" in candidate:
        resolved = (repository_root / candidate).resolve()
        return resolved if resolved.is_file() else None

    found = find_tool(candidate)
    return Path(found) if found is not None else None


def _extend_with_user_arguments(
    base: list[str],
    user_arguments: Sequence[str],
) -> list[str]:
    normalized = _normalize_user_arguments(user_arguments)
    if not normalized:
        return base
    return [*base, "--", *normalized]


def _normalize_user_arguments(arguments: Sequence[str]) -> tuple[str, ...]:
    items = tuple(arguments)
    if items and items[0] == "--":
        return items[1:]
    return items


def _res_path_to_file(game_root: Path, value: str) -> Path | None:
    if not value.startswith("res://"):
        return None
    return (game_root / value.removeprefix("res://")).resolve()


def _run_command(arguments: Sequence[str]) -> CommandResult:
    process = subprocess.run(
        list(arguments),
        check=False,
        capture_output=True,
        text=True,
        timeout=5,
    )
    return CommandResult(process.returncode, process.stdout, process.stderr)


def _first_line(output: str) -> str:
    return output.splitlines()[0] if output else ""


def _extract_version_line(output: str) -> str:
    if not output:
        return ""
    for line in output.splitlines():
        if _extract_major_version(line):
            return line
    return _first_line(output)


def _extract_major_version(version: str) -> int | None:
    labeled = GODOT_LABELED_VERSION_RE.search(version)
    if labeled is not None:
        return int(labeled.group("major"))

    for match in GODOT_VERSION_TOKEN_RE.finditer(version):
        token = match.group(1).removeprefix("v")
        if _looks_like_godot_version_token(token):
            return int(token.split(".", 1)[0])
    return None


def _looks_like_godot_version_token(token: str) -> bool:
    if "_" in token or "/" in token:
        return False
    if not re.fullmatch(r"\d+\.\d+\w*", token):
        return False
    major = int(token.split(".", 1)[0])
    return major >= 3


def _build_not_found_detail(
    attempts: list[str],
    candidates: list[str],
    failures: list[str],
) -> str:
    candidate_report = ", ".join(attempts) if attempts else ", ".join(candidates)
    detail = f"Godot 4 was not found. Attempted candidates: {candidate_report}"
    if failures:
        detail += f". Runtime errors: {' ; '.join(failures[:3])}"

    if any(GODOT_RUNTIME_LOAD_ERROR_RE.search(failure) for failure in failures):
        detail += (
            ". A runtime library mismatch was detected (for example GLIBC). "
            "Use a binary matching your system libc or a containerized distribution."
        )
    return detail


def _probe_failure_detail(candidate: str, returncode: int, output: str) -> str:
    if not output:
        return f"{candidate}: exit code {returncode} without version output."
    message = _first_line(output)
    if not message:
        message = output
    return f"{candidate}: exit code {returncode}: {message}"
