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

    def test_source_does_not_use_shell_true(self) -> None:
        targets = (
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "cli.py",
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "doctor.py",
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "install.py",
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "godot.py",
        )
        for target in targets:
            self.assertNotIn("shell=True", target.read_text(encoding="utf-8"))

    def test_source_does_not_use_break_system_packages(self) -> None:
        targets = (
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "install.py",
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "cli.py",
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "doctor.py",
        )
        for target in targets:
            self.assertNotIn("--break-system-packages", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
