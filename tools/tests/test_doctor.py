"""Tests for environment checks with controlled external-tool doubles."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from _source_path import add_source_root

add_source_root()

from g2dtool.doctor import (
    CommandResult,
    collect_doctor_report,
    format_doctor_report,
)
from g2dtool.repository import discover_repository_layout


BASELINE_CONFIG = Path(__file__).resolve().parents[2]


class DoctorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal_cleanup)
        self.repository = Path(self.temporary_directory.name) / "repository"
        (self.repository / ".git").mkdir(parents=True)
        (self.repository / "config").mkdir()
        (self.repository / "tools").mkdir()
        (self.repository / "tools" / "src").mkdir(parents=True)
        (self.repository / "tools" / "src" / "g2dtool").mkdir(parents=True)
        (self.repository / "game").mkdir()
        (self.repository / "game" / "project.godot").write_text(
            "[application]\nrun/main_scene=\"res://scenes/bootstrap.tscn\"\n",
            encoding="utf-8",
        )
        (self.repository / "scenes").mkdir()
        (self.repository / "config" / "project.toml").write_text(
            (BASELINE_CONFIG / "config" / "project.toml").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (self.repository / "config" / "toolchain.toml").write_text(
            (BASELINE_CONFIG / "config" / "toolchain.toml").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
        (self.repository / "pyproject.toml").write_text(
            "[project]\ndependencies = []\n",
            encoding="utf-8",
        )

    def temporal_cleanup(self) -> None:
        self.temporary_directory.cleanup()

    def test_passes_when_checks_align(self) -> None:
        tools = {"git": "fake-git", "godot4": "fake-godot4"}

        def run_command(arguments):
            if str(arguments[0]).endswith("godot4"):
                return CommandResult(0, "4.3.stable.test\n", "")
            return CommandResult(0, "git 2.42.0\n", "")

        report = collect_doctor_report(
            self.repository,
            find_tool=tools.get,
            run_command=run_command,
            python_version="3.11.0",
            python_executable="python-test-double",
        )

        self.assertEqual(report.exit_code, 0)
        self.assertTrue(all(check.status != "fail" for check in report.checks))

    def test_report_has_failure_when_godot_missing(self) -> None:
        tools = {"git": "fake-git"}
        report = collect_doctor_report(
            self.repository,
            find_tool=tools.get,
            run_command=lambda arguments: CommandResult(0, "git 2.42.0\n", ""),
            python_version="3.11.0",
        )
        check = next(item for item in report.checks if item.name == "godot")
        self.assertEqual(check.status, "fail")
        self.assertIn("Godot 4 was not found", check.detail)

    def test_report_includes_arch_install_hint_when_missing_godot(self) -> None:
        with patch("g2dtool.doctor._is_arch", return_value=True):
            report = collect_doctor_report(
                self.repository,
                find_tool=lambda name: None,
                run_command=lambda arguments: CommandResult(0, "", ""),
                python_version="3.11.0",
            )
        check = next(item for item in report.checks if item.name == "godot")
        self.assertEqual(check.status, "fail")
        self.assertIn("sudo pacman -S --needed godot", check.detail)

    def test_report_rejects_godot_3(self) -> None:
        tools = {"godot": "fake-godot"}

        def run_command(arguments):
            return CommandResult(0, "3.5.3.stable.test\n", "")

        report = collect_doctor_report(
            self.repository,
            find_tool=tools.get,
            run_command=run_command,
            python_version="3.11.0",
        )
        check = next(item for item in report.checks if item.name == "godot")
        self.assertEqual(check.status, "fail")
        self.assertIn("3.5.3", check.detail)

    def test_format_output_contains_summary(self) -> None:
        report_lines = format_doctor_report(collect_doctor_report(self.repository))
        self.assertIn("Doctor summary", report_lines)

    def test_repository_layout_is_included(self) -> None:
        layout = discover_repository_layout(self.repository)
        self.assertEqual(layout.repository_root, self.repository.resolve())


if __name__ == "__main__":
    unittest.main()
