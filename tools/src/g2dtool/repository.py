"""Locate the Forge2D repository using portable path handling."""

from __future__ import annotations

from pathlib import Path


class RepositoryNotFoundError(RuntimeError):
    """Raised when no Git repository exists at or above a start path."""


def find_repository_root(start: Path | None = None) -> Path:
    """Return the nearest parent containing a Git worktree marker.

    Both a `.git` directory and the `.git` file used by linked worktrees are
    accepted. The returned path is resolved so callers can compare it reliably.
    """

    candidate = (start if start is not None else Path.cwd()).resolve()
    if candidate.is_file():
        candidate = candidate.parent

    for directory in (candidate, *candidate.parents):
        if (directory / ".git").exists():
            return directory

    raise RepositoryNotFoundError(
        f"No Git repository found from {candidate}. Run g2d inside a checkout."
    )
