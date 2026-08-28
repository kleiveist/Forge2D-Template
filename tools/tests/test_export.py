"""Tests for safe, deterministic Godot release exports."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import shutil
import subprocess
import unittest
from unittest.mock import patch
import zipfile

from _source_path import add_source_root

add_source_root()

from g2dtool.export import EXPORT_TARGETS, export_template_candidates, run_export
from g2dtool.godot import CommandResult, FAIL, PASS, GodotProbeResult


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class FakeExportRunner:
    """Record one export command and create a controlled output when requested."""

    def __init__(self, mode: str = "success") -> None:
        self.mode = mode
        self.executed: list[tuple[tuple[str, ...], int]] = []

    def __call__(self, command, timeout_seconds: int) -> CommandResult:
        arguments = tuple(map(str, command))
        self.executed.append((arguments, timeout_seconds))
        if self.mode == "timeout":
            raise subprocess.TimeoutExpired(arguments, timeout_seconds)
        if self.mode == "failure":
            return CommandResult(
                42,
                "Godot Engine",
                "\x1b[31mExport template failed\x1b[0m",
            )

        output = Path(arguments[-1])
        if self.mode == "missing":
            return CommandResult(0, "", "")
        if self.mode == "empty":
            output.write_bytes(b"")
            return CommandResult(0, "", "")
        if self.mode == "invalid":
            output.write_bytes(b"not an executable")
            return CommandResult(0, "", "")
        if output.suffix == ".zip":
            with zipfile.ZipFile(output, "w") as archive:
                archive.writestr("Forge2D Template.app/Contents/MacOS/Forge2D Template", b"bin")
        elif output.suffix == ".exe":
            output.write_bytes(b"MZ\x00\x00Forge2D")
        else:
            output.write_bytes(b"\x7fELFForge2D")
        return CommandResult(0, "export complete", "")


class ExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        self.home = Path(self.temp.name) / "home"
        self.godot = Path(self.temp.name) / "godot4"
        (self.root / ".git").mkdir(parents=True)
        (self.root / "game").mkdir()
        (self.root / "game" / "project.godot").write_text(
            '[application]\nconfig/name="Forge2D Template"\n',
            encoding="utf-8",
        )
        shutil.copy2(
            REPOSITORY_ROOT / "game" / "export_presets.cfg",
            self.root / "game" / "export_presets.cfg",
        )
        self.probe = GodotProbeResult(
            executable=self.godot,
            version="4.7.2.stable.official.56d3583",
            status=PASS,
            detail="Godot 4.7.2 is available.",
        )

    def test_exports_all_reviewed_targets_to_exact_repository_paths(self) -> None:
        for target_name, target in EXPORT_TARGETS.items():
            with self.subTest(target=target_name):
                self._install_template(target_name)
                runner = FakeExportRunner()
                code, output = self._run(target_name, runner=runner)

                artifact = self.root / target.output_relative
                self.assertEqual(code, 0, output)
                self.assertTrue(artifact.is_file())
                self.assertGreater(artifact.stat().st_size, 0)
                self.assertIn(target.output_relative.as_posix(), output)
                arguments, timeout_seconds = runner.executed[0]
                self.assertEqual(arguments[1:3], ("--headless", "--path"))
                self.assertEqual(arguments[4:6], ("--export-release", target.preset_name))
                self.assertTrue(os.path.samefile(arguments[-1], artifact))
                self.assertGreater(timeout_seconds, 0)

    def test_dry_run_validates_inputs_without_writing_or_running_godot(self) -> None:
        self._install_template("linux")
        before = sorted(path.relative_to(self.root) for path in self.root.rglob("*"))
        runner = FakeExportRunner()

        code, output = self._run("linux", dry_run=True, runner=runner)

        after = sorted(path.relative_to(self.root) for path in self.root.rglob("*"))
        self.assertEqual(code, 0, output)
        self.assertEqual(before, after)
        self.assertEqual(runner.executed, [])
        self.assertIn("[DRY-RUN]", output)
        self.assertIn("no changes were made", output)
        self.assertFalse((self.root / "artifacts").exists())

    def test_missing_godot_reports_install_and_diagnostic_steps(self) -> None:
        probe = GodotProbeResult(
            executable=None,
            version=None,
            status=FAIL,
            detail="Godot 4 was not found.",
        )

        code, output = self._run("linux", dry_run=True, probe=probe)

        self.assertEqual(code, 1)
        self.assertIn("Godot 4 is unavailable", output)
        self.assertIn("tools/control.py install", output)
        self.assertIn("tools/control.py doctor", output)

    def test_missing_preset_file_reports_repository_recovery(self) -> None:
        (self.root / "game" / "export_presets.cfg").unlink()

        code, output = self._run("linux", dry_run=True)

        self.assertEqual(code, 1)
        self.assertIn("export presets are missing", output)
        self.assertIn("Restore game/export_presets.cfg", output)

    def test_invalid_preset_output_is_rejected_before_export(self) -> None:
        path = self.root / "game" / "export_presets.cfg"
        text = path.read_text(encoding="utf-8").replace(
            "../artifacts/exports/windows/Forge2D-Template.exe",
            "../../unsafe/Forge2D-Template.exe",
        )
        path.write_text(text, encoding="utf-8")

        code, output = self._run("windows", dry_run=True)

        self.assertEqual(code, 1)
        self.assertIn("invalid settings: export_path", output)
        self.assertIn("Restore the reviewed preset", output)

    def test_missing_template_names_version_path_and_install_steps(self) -> None:
        code, output = self._run("windows", dry_run=True)

        self.assertEqual(code, 1)
        self.assertIn("windows_release_x86_64.exe", output)
        self.assertIn("4.7.2.stable", output)
        self.assertIn("Manage Export Templates", output)
        self.assertFalse((self.root / "artifacts").exists())

    def test_failed_process_removes_stale_file_and_reports_godot_output(self) -> None:
        self._install_template("linux")
        artifact = self.root / EXPORT_TARGETS["linux"].output_relative
        artifact.parent.mkdir(parents=True)
        artifact.write_bytes(b"\x7fELFstale")

        code, output = self._run("linux", runner=FakeExportRunner("failure"))

        self.assertEqual(code, 1)
        self.assertFalse(artifact.exists())
        self.assertIn("Godot exited with code 42", output)
        self.assertIn("Export template failed", output)
        self.assertNotIn("\x1b", output)
        self.assertIn("Project > Export", output)

    def test_timeout_has_process_and_resource_recovery_steps(self) -> None:
        self._install_template("linux")

        code, output = self._run("linux", runner=FakeExportRunner("timeout"))

        self.assertEqual(code, 1)
        self.assertIn("did not finish", output)
        self.assertIn("available disk space", output)
        self.assertIn("printed command", output)

    def test_success_without_artifact_is_rejected(self) -> None:
        self._install_template("linux")

        code, output = self._run("linux", runner=FakeExportRunner("missing"))

        self.assertEqual(code, 1)
        self.assertIn("reported success but did not create", output)

    def test_empty_and_invalid_artifacts_are_rejected(self) -> None:
        self._install_template("windows")
        for mode, expected in (
            ("empty", "empty export"),
            ("invalid", "invalid PE signature"),
        ):
            with self.subTest(mode=mode):
                code, output = self._run(
                    "windows",
                    runner=FakeExportRunner(mode),
                )
                self.assertEqual(code, 1)
                self.assertIn(expected, output)

    def test_directory_destination_is_never_replaced_recursively(self) -> None:
        self._install_template("linux")
        artifact = self.root / EXPORT_TARGETS["linux"].output_relative
        artifact.mkdir(parents=True)
        marker = artifact / "keep.txt"
        marker.write_text("user data", encoding="utf-8")

        code, output = self._run("linux")

        self.assertEqual(code, 1)
        self.assertTrue(marker.is_file())
        self.assertIn("Refusing to replace non-regular", output)
        self.assertIn("Move that path aside manually", output)

    @unittest.skipIf(os.name == "nt", "Creating symlinks is not reliable on Windows CI")
    def test_symlinked_artifact_root_cannot_escape_repository(self) -> None:
        self._install_template("linux")
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (self.root / "artifacts").symlink_to(outside, target_is_directory=True)

        code, output = self._run("linux", dry_run=True)

        self.assertEqual(code, 1)
        self.assertIn("resolves outside the repository", output)
        self.assertEqual(list(outside.iterdir()), [])

    def test_template_candidates_cover_all_supported_host_locations(self) -> None:
        cases = (
            (
                "Linux",
                {},
                self.home / ".local/share/godot/export_templates/4.7.2.stable/macos.zip",
            ),
            (
                "Darwin",
                {},
                self.home
                / "Library/Application Support/Godot/export_templates/4.7.2.stable/macos.zip",
            ),
            (
                "Windows",
                {"APPDATA": str(self.home / "AppData/Roaming")},
                self.home
                / "AppData/Roaming/Godot/export_templates/4.7.2.stable/macos.zip",
            ),
        )
        for system_name, environment, expected in cases:
            with self.subTest(system=system_name):
                candidates = export_template_candidates(
                    self.godot,
                    "4.7.2.stable.official",
                    "macos.zip",
                    system_name=system_name,
                    environment=environment,
                    home_directory=self.home,
                )
                self.assertEqual(candidates, (expected,))

    def test_self_contained_editor_template_is_checked_first(self) -> None:
        portable_root = self.godot.parent
        (portable_root / "_sc_").write_text("", encoding="utf-8")

        candidates = export_template_candidates(
            self.godot,
            "4.7.2.stable.official",
            "linux_release.x86_64",
            system_name="Linux",
            environment={},
            home_directory=self.home,
        )

        expected = (
            portable_root
            / "editor_data/export_templates/4.7.2.stable/linux_release.x86_64"
        )
        self.assertEqual(candidates[0], expected)

    def test_unsupported_target_is_an_expected_usage_failure(self) -> None:
        code, output = self._run("android", dry_run=True)

        self.assertEqual(code, 1)
        self.assertIn("Unsupported target 'android'", output)
        self.assertIn("linux, windows, macos", output)

    def _install_template(self, target_name: str) -> Path:
        target = EXPORT_TARGETS[target_name]
        template = (
            self.home
            / ".local/share/godot/export_templates/4.7.2.stable"
            / target.template_file
        )
        template.parent.mkdir(parents=True, exist_ok=True)
        template.write_bytes(b"official template fixture")
        return template

    def _run(
        self,
        target_name: str,
        *,
        dry_run: bool = False,
        runner: FakeExportRunner | None = None,
        probe: GodotProbeResult | None = None,
    ) -> tuple[int, str]:
        command_runner = runner or FakeExportRunner()
        output = StringIO()
        with (
            patch("g2dtool.export.discover_godot", return_value=probe or self.probe),
            redirect_stdout(output),
        ):
            code = run_export(
                target_name,
                start=self.root,
                dry_run=dry_run,
                run_command=command_runner,
                system_name="Linux",
                environment={},
                home_directory=self.home,
            )
        return code, output.getvalue()


if __name__ == "__main__":
    unittest.main()
