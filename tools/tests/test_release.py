"""Tests for safe, repeatable GitHub release-asset preparation."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import os
import shutil
import unittest
import zipfile

from _source_path import add_source_root

add_source_root()

from g2dtool.release import (
    RELEASE_ASSETS,
    ReleaseAsset,
    run_release_prepare,
    validate_release_metadata,
)
from g2dtool.repository import discover_repository_layout


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class ReleaseRepositoryContractTests(unittest.TestCase):
    def test_repository_release_metadata_is_consistent(self) -> None:
        metadata = validate_release_metadata(
            discover_repository_layout(REPOSITORY_ROOT)
        )

        self.assertEqual(metadata.version, "0.1.0")
        self.assertEqual(metadata.tag, "v0.1.0")
        self.assertEqual(metadata.release_date, "2026-08-28")
        self.assertEqual(
            metadata.notes_path,
            REPOSITORY_ROOT
            / "docs"
            / "forge2d-template"
            / "releases"
            / "v0.1.0.md",
        )

    def test_publication_guide_preserves_tag_and_asset_audit_boundaries(self) -> None:
        guide = (
            REPOSITORY_ROOT
            / "docs"
            / "forge2d-template"
            / "tooling"
            / "releasing.md"
        ).read_text(encoding="utf-8")

        required = (
            "push CI run for that exact commit",
            "git cat-file -t refs/tags/v0.1.0",
            "git push origin refs/tags/v0.1.0",
            "--verify-tag",
            "SHA256SUMS.txt",
            "must never move or be overwritten",
            "v0.1.1",
        )
        for text in required:
            with self.subTest(text=text):
                self.assertIn(text, guide)

    def test_release_notes_name_every_asset_and_signing_limitation(self) -> None:
        notes = (
            REPOSITORY_ROOT
            / "docs"
            / "forge2d-template"
            / "releases"
            / "v0.1.0.md"
        ).read_text(encoding="utf-8")

        for asset in RELEASE_ASSETS:
            with self.subTest(target=asset.target.key):
                self.assertIn(asset.filename("0.1.0"), notes)
        self.assertIn("SHA256SUMS.txt", notes)
        self.assertIn("not production-signed", notes)


class ReleasePreparationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        (self.root / ".git").mkdir(parents=True)
        (self.root / "config").mkdir()
        (self.root / "game").mkdir()
        self.release_docs = (
            self.root / "docs" / "forge2d-template" / "releases"
        )
        self.release_docs.mkdir(parents=True)
        (self.root / "config" / "project.toml").write_text(
            """schema_version = 1

[project]
template_id = "forge2d-template"
display_name = "Forge2D Template"
version = "0.1.0"
repository_language = "en"
default_cli_name = "g2d"
godot_project_path = "game/project.godot"
license_status = "selected"
""",
            encoding="utf-8",
        )
        (self.root / "game" / "project.godot").write_text(
            '[application]\nconfig/version="0.1.0"\n',
            encoding="utf-8",
        )
        (self.root / "README.md").write_text(
            "# Forge2D Template\n\n- Version: `0.1.0`\n",
            encoding="utf-8",
        )
        (self.root / "CHANGELOG.md").write_text(
            """# Changelog

## Unreleased

No changes yet.

## Forge2D-Template v0.1.0 - 2026-08-28

### Added

- Initial reviewed release.
""",
            encoding="utf-8",
        )
        (self.release_docs / "v0.1.0.md").write_text(
            """# Forge2D Template v0.1.0

Release date: 2026-08-28
""",
            encoding="utf-8",
        )
        self.downloads = self.root / "artifacts" / "release" / "downloads"
        self.assets = self.root / "artifacts" / "release" / "assets"
        self._write_all_downloads()

    def test_prepares_all_platform_assets_and_sha256_checksums(self) -> None:
        code, output = self._run()

        self.assertEqual(code, 0, output)
        expected_names = {
            "Forge2D-Template-v0.1.0-linux-x86_64",
            "Forge2D-Template-v0.1.0-windows-x86_64.exe",
            "Forge2D-Template-v0.1.0-macos-universal.zip",
            "SHA256SUMS.txt",
        }
        self.assertEqual({path.name for path in self.assets.iterdir()}, expected_names)
        checksum_lines = (self.assets / "SHA256SUMS.txt").read_text(
            encoding="utf-8"
        ).splitlines()
        self.assertEqual(checksum_lines, sorted(checksum_lines))
        self.assertEqual(len(checksum_lines), 3)
        for line in checksum_lines:
            digest, filename = line.split("  ", maxsplit=1)
            self.assertEqual(digest, self._sha256(self.assets / filename))
        self.assertIn("3 verified assets", output)

    def test_second_run_accepts_identical_assets_without_rewriting(self) -> None:
        first_code, first_output = self._run()
        self.assertEqual(first_code, 0, first_output)
        before = {
            path.name: (path.stat().st_mtime_ns, self._sha256(path))
            for path in self.assets.iterdir()
        }

        second_code, second_output = self._run()

        after = {
            path.name: (path.stat().st_mtime_ns, self._sha256(path))
            for path in self.assets.iterdir()
        }
        self.assertEqual(second_code, 0, second_output)
        self.assertEqual(after, before)
        self.assertIn("already prepared and verified", second_output)

    def test_dry_run_accepts_identical_assets_without_rewriting(self) -> None:
        first_code, first_output = self._run()
        self.assertEqual(first_code, 0, first_output)
        before = self._tree_snapshot()

        code, output = self._run(dry_run=True)

        self.assertEqual(code, 0, output)
        self.assertEqual(self._tree_snapshot(), before)
        self.assertIn("[DRY-RUN]", output)
        self.assertIn("no changes were made", output)

    def test_dry_run_validates_without_creating_asset_directory(self) -> None:
        before = self._tree_snapshot()

        code, output = self._run(dry_run=True)

        self.assertEqual(code, 0, output)
        self.assertEqual(self._tree_snapshot(), before)
        self.assertFalse(self.assets.exists())
        self.assertIn("[DRY-RUN]", output)
        self.assertIn("no changes were made", output)

    def test_missing_download_names_exact_workflow_artifact(self) -> None:
        missing = self.downloads / RELEASE_ASSETS[1].downloaded_relative
        missing.unlink()

        code, output = self._run(dry_run=True)

        self.assertEqual(code, 1)
        self.assertIn("Windows artifact is missing", output)
        self.assertIn("forge2d-template-Windows", output)
        self.assertIn("approved successful main CI run", output)

    def test_invalid_signatures_are_rejected_for_every_platform(self) -> None:
        for asset in RELEASE_ASSETS:
            with self.subTest(target=asset.target.key):
                path = self.downloads / asset.downloaded_relative
                path.write_bytes(b"invalid release artifact")

                code, output = self._run(dry_run=True)

                self.assertEqual(code, 1)
                self.assertIn(
                    f"Downloaded {asset.target.preset_name} artifact is invalid",
                    output,
                )
                self.assertIn("approved successful main CI run", output)
                self._write_download(asset)

    def test_unreleased_changelog_entries_block_preparation(self) -> None:
        changelog = self.root / "CHANGELOG.md"
        text = changelog.read_text(encoding="utf-8").replace(
            "No changes yet.",
            "### Added\n\n- A change not assigned to the release.",
        )
        changelog.write_text(text, encoding="utf-8")

        code, output = self._run(dry_run=True)

        self.assertEqual(code, 1)
        self.assertIn("still contains Unreleased list entries", output)
        self.assertIn("Move every intended change into the v0.1.0", output)

    def test_inconsistent_project_version_has_recovery_guidance(self) -> None:
        project = self.root / "game" / "project.godot"
        project.write_text(
            project.read_text(encoding="utf-8").replace("0.1.0", "0.2.0"),
            encoding="utf-8",
        )

        code, output = self._run(dry_run=True)

        self.assertEqual(code, 1)
        self.assertIn("Version mismatch: game/project.godot", output)
        self.assertIn("Set application config/version", output)

    def test_readme_version_must_match_project_metadata(self) -> None:
        (self.root / "README.md").write_text(
            "# Forge2D Template\n\n- Version: `0.2.0`\n",
            encoding="utf-8",
        )

        code, output = self._run(dry_run=True)

        self.assertEqual(code, 1)
        self.assertIn("README.md does not declare release version 0.1.0", output)
        self.assertIn("Set the README version line", output)

    def test_release_notes_must_match_version_and_date(self) -> None:
        notes = self.release_docs / "v0.1.0.md"
        notes.write_text("# Forge2D Template v0.1.0\n", encoding="utf-8")

        code, output = self._run(dry_run=True)

        self.assertEqual(code, 1)
        self.assertIn("Release notes do not match", output)
        self.assertIn("Release date: 2026-08-28", output)

    def test_existing_mismatched_assets_are_never_overwritten(self) -> None:
        self.assets.mkdir(parents=True)
        marker = self.assets / "keep.txt"
        marker.write_text("user data", encoding="utf-8")

        code, output = self._run()

        self.assertEqual(code, 1)
        self.assertEqual(marker.read_text(encoding="utf-8"), "user data")
        self.assertIn("never overwrites it", output)

    @unittest.skipIf(os.name == "nt", "Creating symlinks is not reliable on Windows CI")
    def test_symlinked_download_root_cannot_escape_repository(self) -> None:
        shutil.rmtree(self.downloads)
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        self.downloads.symlink_to(outside, target_is_directory=True)

        code, output = self._run(dry_run=True)

        self.assertEqual(code, 1)
        self.assertIn("resolves outside", output)
        self.assertFalse(self.assets.exists())

    def _write_all_downloads(self) -> None:
        for asset in RELEASE_ASSETS:
            self._write_download(asset)

    def _write_download(self, asset: ReleaseAsset) -> None:
        path = self.downloads / asset.downloaded_relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if asset.target.key == "linux":
            path.write_bytes(b"\x7fELFForge2D release")
        elif asset.target.key == "windows":
            path.write_bytes(b"MZ\x00\x00Forge2D release")
        else:
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr(
                    "Forge2D Template.app/Contents/MacOS/Forge2D Template",
                    b"binary",
                )

    def _run(self, *, dry_run: bool = False) -> tuple[int, str]:
        output = StringIO()
        with redirect_stdout(output):
            code = run_release_prepare(start=self.root, dry_run=dry_run)
        return code, output.getvalue()

    def _tree_snapshot(self) -> dict[str, str]:
        return {
            path.relative_to(self.root).as_posix(): self._sha256(path)
            for path in self.root.rglob("*")
            if path.is_file()
        }

    @staticmethod
    def _sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()


if __name__ == "__main__":
    unittest.main()
