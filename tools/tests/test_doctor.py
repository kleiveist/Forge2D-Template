"""Tests for environment checks with controlled external-tool doubles."""

from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import unittest

from _source_path import add_source_root

add_source_root()

from g2dtool.doctor import CommandResult, collect_doctor_report


BASELINE_CONFIG = Path(__file__).resolve().parents[2] / "config" / "project.toml"


class DoctorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.repository = Path(self.temporary_directory.name) / "repository"
        (self.repository / ".git").mkdir(parents=True)
        (self.repository / "config").mkdir()
        shutil.copy2(BASELINE_CONFIG, self.repository / "config" / "project.toml")

    def test_passes_with_git_and_godot_4_test_doubles(self) -> None:
        tools = {"git": "fake-git", "godot4": "fake-godot4"}

        def run_command(arguments):
            versions = {
                "fake-git": "git version 2.42.0\n",
                "fake-godot4": "4.3.stable.test\n",
            }
            return CommandResult(0, versions[arguments[0]], "")

        report = collect_doctor_report(
            self.repository,
            find_tool=tools.get,
            run_command=run_command,
            python_version="3.11.0",
            python_executable="python-test-double",
        )

        self.assertEqual(report.exit_code, 0)
        self.assertTrue(all(check.passed for check in report.checks))

    def test_missing_godot_is_a_requirement_failure(self) -> None:
        tools = {"git": "fake-git"}

        report = collect_doctor_report(
            self.repository,
            find_tool=tools.get,
            run_command=lambda _arguments: CommandResult(
                0, "git version 2.42.0\n", ""
            ),
            python_version="3.11.0",
            python_executable="python-test-double",
        )

        godot_check = next(check for check in report.checks if check.name == "godot")
        self.assertEqual(report.exit_code, 1)
        self.assertEqual(godot_check.status, "missing")
        self.assertIn("Install a verified Godot 4 editor", godot_check.detail)

    def test_rejects_incompatible_godot_major_version(self) -> None:
        tools = {"git": "fake-git", "godot": "fake-godot"}

        def run_command(arguments):
            if arguments[0] == "fake-godot":
                return CommandResult(0, "3.5.3.stable.test\n", "")
            return CommandResult(0, "git version 2.42.0\n", "")

        report = collect_doctor_report(
            self.repository,
            find_tool=tools.get,
            run_command=run_command,
            python_version="3.11.0",
            python_executable="python-test-double",
        )

        godot_check = next(check for check in report.checks if check.name == "godot")
        self.assertEqual(report.exit_code, 1)
        self.assertEqual(godot_check.status, "incompatible")


if __name__ == "__main__":
    unittest.main()
