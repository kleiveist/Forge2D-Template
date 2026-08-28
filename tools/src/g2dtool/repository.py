"""Locate the Forge2D Template repository and its canonical local paths."""

from __future__ import annotations

from pathlib import Path
from dataclasses import dataclass


class RepositoryNotFoundError(RuntimeError):
    """Raised when no Git repository exists at or above a start path."""


@dataclass(frozen=True, slots=True)
class RepositoryLayout:
    """Resolved repository paths used by tooling."""

    repository_root: Path
    pyproject_toml: Path
    project_config: Path
    toolchain_config: Path
    tools_directory: Path
    tools_source_directory: Path
    game_directory: Path
    venv_directory: Path

    @property
    def game_project_path(self) -> Path:
        return self.repository_root / "game" / "project.godot"

    @property
    def export_presets_path(self) -> Path:
        """Return the version-controlled Godot export preset file."""

        return self.game_directory / "export_presets.cfg"

    @property
    def export_directory(self) -> Path:
        """Return the ignored root for locally generated release exports."""

        return self.repository_root / "artifacts" / "exports"


def find_repository_root(start: Path | None = None) -> Path:
    """Return the nearest parent containing a Git worktree marker."""

    candidate = (start if start is not None else Path.cwd()).resolve()
    if candidate.is_file():
        candidate = candidate.parent

    for directory in (candidate, *candidate.parents):
        if (directory / ".git").exists():
            return directory

    raise RepositoryNotFoundError(
        f"No Git repository found from {candidate}. Run g2d inside a checkout."
    )


def discover_repository_layout(start: Path | None = None) -> RepositoryLayout:
    """Resolve all local paths used by the tooling entry points."""

    repository_root = find_repository_root(start)
    return RepositoryLayout(
        repository_root=repository_root,
        pyproject_toml=repository_root / "pyproject.toml",
        project_config=repository_root / "config" / "project.toml",
        toolchain_config=repository_root / "config" / "toolchain.toml",
        tools_directory=repository_root / "tools",
        tools_source_directory=repository_root / "tools" / "src",
        game_directory=repository_root / "game",
        venv_directory=repository_root / ".venv",
    )
