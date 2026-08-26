"""Read and validate the Forge2D baseline project configuration."""

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


class ProjectConfigError(ValueError):
    """Raised when project configuration is missing or invalid."""


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    """Validated values from `config/project.toml`."""

    schema_version: int
    template_id: str
    display_name: str
    repository_language: str
    default_cli_name: str
    godot_project_path: PurePosixPath
    license_status: str


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
        repository_language=repository_language,
        default_cli_name=default_cli_name,
        godot_project_path=godot_project_path,
        license_status=license_status,
    )


def _required_string(table: dict[str, Any], key: str) -> str:
    value = table.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProjectConfigError(f"project.{key} must be a non-empty string")
    if value != value.strip():
        raise ProjectConfigError(f"project.{key} must not have surrounding whitespace")
    return value


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
