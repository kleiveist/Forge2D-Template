"""Expose the src-layout package to direct standard-library test discovery."""

from pathlib import Path
import sys


def add_source_root() -> None:
    """Prepend `tools/src` without relying on an installed package."""

    source_root = Path(__file__).resolve().parents[1] / "src"
    source_root_text = str(source_root)
    if source_root_text not in sys.path:
        sys.path.insert(0, source_root_text)
