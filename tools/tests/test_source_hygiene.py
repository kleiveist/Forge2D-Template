"""Tests for machine-independent paths in repository source."""

from pathlib import Path
import re
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATHS = (
    REPOSITORY_ROOT / "config",
    REPOSITORY_ROOT / "game",
    REPOSITORY_ROOT / "tools" / "src",
)
SOURCE_SUFFIXES = {".gd", ".godot", ".py", ".toml", ".tscn"}
USER_PATH_PATTERNS = (
    re.compile("/" + r"home/[A-Za-z0-9._-]+/"),
    re.compile("/" + r"Users/[A-Za-z0-9._-]+/"),
    re.compile(r"[A-Za-z]:\\Users\\[A-Za-z0-9._-]+\\"),
)


class SourceHygieneTests(unittest.TestCase):
    def test_source_and_configuration_have_no_hard_coded_user_paths(self) -> None:
        violations: list[str] = []
        files = [REPOSITORY_ROOT / "pyproject.toml"]
        for source_path in SOURCE_PATHS:
            if source_path.exists():
                files.extend(
                    path
                    for path in source_path.rglob("*")
                    if path.is_file() and path.suffix in SOURCE_SUFFIXES
                )

        for path in files:
            contents = path.read_text(encoding="utf-8")
            if any(pattern.search(contents) for pattern in USER_PATH_PATTERNS):
                violations.append(path.relative_to(REPOSITORY_ROOT).as_posix())

        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
