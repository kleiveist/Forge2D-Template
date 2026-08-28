"""Read and validate the Forge2D Template baseline project configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import re
import tomllib
from typing import Any


SUPPORTED_SCHEMA_VERSION = 1
LICENSE_STATUSES = frozenset({"undecided", "selected"})
IDENTIFIER_PATTERN = re.compile(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*\Z")
LANGUAGE_PATTERN = re.compile(r"[a-z]{2}(?:-[A-Za-z0-9]+)*\Z")
VERSION_PATTERN = re.compile(r"(?P<major>\d+)\.(?P<minor>\d+)(?:\.\d+)?")


class ProjectConfigError(ValueError):
    """Raised when project configuration is missing or invalid."""


class ToolchainConfigError(ValueError):
    """Raised when project toolchain configuration is invalid."""


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    """Validated values from `config/project.toml`."""

    schema_version: int
    template_id: str
    display_name: str
    version: str
    repository_language: str
    default_cli_name: str
    godot_project_path: PurePosixPath
    license_status: str


@dataclass(frozen=True, slots=True)
class ToolchainConfig:
    """Validated toolchain requirements."""

    minimum_python_major: int
    minimum_python_minor: int
    runtime_dependencies: tuple[str, ...]
    development_dependencies: tuple[str, ...]
    required_godot_major: int
    godot_binary: str | None
    godot_executable_candidates: tuple[str, ...]


def load_project_config(path: Path) -> ProjectConfig:
    """Load a project configuration file and enforce the M01 schema."""

    try:
        with path.open("rb") as config_file:
            document = tomllib.load(config_file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ProjectConfigError(f"Cannot read project configuration: {error}") from error

    schema_version = document.get("schema_version")
    if type(schema_version) is not int or schema_version != SUPPORTED_SCHEMA_VERSION:
        raise ProjectConfigError(
            f"schema_version must be {SUPPORTED_SCHEMA_VERSION}, got {schema_version!r}"
        )

    project = document.get("project")
    if not isinstance(project, dict):
        raise ProjectConfigError("project must be a TOML table")

    template_id = _required_string(project, "template_id")
    if IDENTIFIER_PATTERN.fullmatch(template_id) is None:
        raise ProjectConfigError(
            "project.template_id must be a stable lowercase identifier"
        )

    display_name = _required_string(project, "display_name")
    version = _required_string(project, "version")
    if VERSION_PATTERN.fullmatch(version) is None:
        raise ProjectConfigError("project.version must be a semantic version")
    repository_language = _required_string(project, "repository_language")
    if LANGUAGE_PATTERN.fullmatch(repository_language) is None:
        raise ProjectConfigError(
            "project.repository_language must be a short language tag"
        )

    default_cli_name = _required_string(project, "default_cli_name")
    if IDENTIFIER_PATTERN.fullmatch(default_cli_name) is None:
        raise ProjectConfigError(
            "project.default_cli_name must be a lowercase command identifier"
        )

    godot_path_value = _required_string(project, "godot_project_path")
    godot_project_path = _validate_relative_posix_path(godot_path_value)
    if godot_project_path.suffix != ".godot":
        raise ProjectConfigError(
            "project.godot_project_path must identify a .godot project file"
        )

    license_status = _required_string(project, "license_status")
    if license_status not in LICENSE_STATUSES:
        allowed = ", ".join(sorted(LICENSE_STATUSES))
        raise ProjectConfigError(
            f"project.license_status must be one of: {allowed}"
        )

    return ProjectConfig(
        schema_version=schema_version,
        template_id=template_id,
        display_name=display_name,
        version=version,
        repository_language=repository_language,
        default_cli_name=default_cli_name,
        godot_project_path=godot_project_path,
        license_status=license_status,
    )


def load_toolchain_config(path: Path) -> ToolchainConfig:
    """Load toolchain requirements from `config/toolchain.toml`."""

    try:
        with path.open("rb") as config_file:
            document = tomllib.load(config_file)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ToolchainConfigError(f"Cannot read toolchain configuration: {error}") from error

    python = document.get("python")
    if not isinstance(python, dict):
        raise ToolchainConfigError("`python` table is missing or invalid.")

    minimum_version = _required_string(python, "minimum_version")
    minimum_python = _parse_version_tuple(minimum_version)

    runtime_dependencies = _normalize_string_list(
        python.get("runtime_dependencies"), default=()
    )

    dev_dependencies = _normalize_string_list(
        python.get("development_dependencies"), default=()
    )

    godot = document.get("godot")
    if not isinstance(godot, dict):
        raise ToolchainConfigError("`godot` table is missing or invalid.")

    required_major = _required_int(godot, "required_major")
    godot_binary = godot.get("executable")
    godot_binary = godot_binary.strip() if isinstance(godot_binary, str) else None
    if godot_binary == "":
        godot_binary = None

    candidates = _normalize_string_list(
        godot.get("executable_candidates"),
        default=("godot4", "godot"),
    )

    return ToolchainConfig(
        minimum_python_major=minimum_python[0],
        minimum_python_minor=minimum_python[1],
        runtime_dependencies=runtime_dependencies,
        development_dependencies=dev_dependencies,
        required_godot_major=required_major,
        godot_binary=godot_binary,
        godot_executable_candidates=tuple(candidates),
    )


def _required_string(table: dict[str, Any], key: str) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProjectConfigError(f"project.{key} must be a non-empty string")
    if value != value.strip():
        raise ProjectConfigError(f"project.{key} must not have surrounding whitespace")
    return value


def _required_string_or_error(message_key: str, value: Any, *, key: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ToolchainConfigError(f"{message_key}.{key} must be a non-empty string")
    if value != value.strip():
        raise ToolchainConfigError(
            f"{message_key}.{key} must not have surrounding whitespace"
        )
    return value


def _normalize_string_list(value: Any, *, default: tuple[str, ...] = ()) -> tuple[str, ...]:
    if value is None:
        return tuple(default)
    if isinstance(value, str):
        return (value,)
    if not isinstance(value, list):
        raise ToolchainConfigError("Expected a list of dependency names.")
    normalized: list[str] = []
    for entry in value:
        normalized.append(
            _required_string_or_error("toolchain.python", entry, key="dependency")
        )
    return tuple(dict.fromkeys(normalized))


def _validate_relative_posix_path(value: str) -> PurePosixPath:
    if "\\" in value:
        raise ProjectConfigError(
            "project.godot_project_path must use portable forward slashes"
        )

    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path == PurePosixPath("."):
        raise ProjectConfigError(
            "project.godot_project_path must be a repository-relative path"
        )
    return path


def _parse_version_tuple(value: str) -> tuple[int, int]:
    match = VERSION_PATTERN.match(value.strip())
    if match is None:
        raise ToolchainConfigError(
            "python.minimum_version must be in the form <major>.<minor>"
        )
    return int(match.group("major")), int(match.group("minor"))


def _required_int(table: dict[str, Any], key: str) -> int:
    value = table.get(key)
    if not isinstance(value, int):
        raise ToolchainConfigError(f"{key} must be an integer")
    return value
