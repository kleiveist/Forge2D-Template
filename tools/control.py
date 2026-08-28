"""Repository-local bootstrap for Forge2D Template tooling."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence
import sys


MINIMUM_PYTHON = (3, 11)


def _repository_root() -> Path:
    """Return the repository root without relying on the current working directory."""

    return Path(__file__).resolve().parent.parent


def _bootstrap_python_path() -> None:
    """Add ``tools/src`` to ``sys.path`` so this works without installation."""

    source_root = (_repository_root() / "tools" / "src").resolve()
    source_text = str(source_root)
    if source_text not in sys.path:
        sys.path.insert(0, source_text)


def main(arguments: Sequence[str] | None = None) -> int:
    """Execute the local CLI through a stable repository-local bootstrap."""

    observed = (sys.version_info.major, sys.version_info.minor)
    if observed < MINIMUM_PYTHON:
        print(
            "Error: Forge2D Template requires Python "
            f">= {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]}; "
            f"this interpreter is {observed[0]}.{observed[1]}.",
            file=sys.stderr,
        )
        print(
            f"Install Python {MINIMUM_PYTHON[0]}.{MINIMUM_PYTHON[1]} or newer "
            "with your operating-system package manager, then re-run "
            "tools/control.py with that interpreter.",
            file=sys.stderr,
        )
        return 1

    _bootstrap_python_path()
    from g2dtool.cli import main as cli_main

    return int(cli_main(arguments, prog="python tools/control.py"))


if __name__ == "__main__":
    raise SystemExit(main())
