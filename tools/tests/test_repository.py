"""Tests for repository-root discovery."""

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from _source_path import add_source_root

add_source_root()

from g2dtool.repository import RepositoryNotFoundError, discover_repository_layout, find_repository_root


class RepositoryRootTests(unittest.TestCase):
    def test_finds_repository_root_from_nested_directory(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "repository"
            nested = root / "tooling" / "src"
            (root / ".git").mkdir(parents=True)
            nested.mkdir(parents=True)

            self.assertEqual(find_repository_root(nested), root.resolve())

    def test_accepts_worktree_git_file(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "worktree"
            root.mkdir()
            (root / ".git").write_text("gitdir: ../metadata\n", encoding="utf-8")

            self.assertEqual(find_repository_root(root), root.resolve())

    def test_repository_layout_contains_expected_paths(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory) / "layout"
            (root / ".git").mkdir(parents=True)
            layout = discover_repository_layout(root)
            self.assertEqual(layout.repository_root, root.resolve())
            self.assertEqual(layout.project_config, root / "config" / "project.toml")
            self.assertEqual(layout.toolchain_config, root / "config" / "toolchain.toml")
            self.assertEqual(layout.venv_directory, root / ".venv")

    def test_reports_missing_repository(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            with self.assertRaises(RepositoryNotFoundError):
                find_repository_root(Path(temporary_directory))
