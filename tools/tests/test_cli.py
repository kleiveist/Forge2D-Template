"""Tests for stable CLI output and exit codes."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
import tomllib
import unittest
from unittest.mock import patch

from _source_path import add_source_root

add_source_root()

from g2dtool.cli import main, welcome
from g2dtool.doctor import DoctorCheck, DoctorReport


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class CliTests(unittest.TestCase):
    def test_help_exits_zero(self) -> None:
        output = StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as exit_context:
            main(["--help"])

        self.assertEqual(exit_context.exception.code, 0)
        self.assertIn("usage: g2d", output.getvalue())

    def test_version_has_stable_output_and_exit_code(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(["version"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(output.getvalue(), "g2d 0.1.0\n")

    def test_forge2d_welcome_lists_beginner_commands_with_emojis(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            exit_code = welcome()

        rendered = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertTrue(rendered.startswith("🧭 Forge2D developer entry point\n"))
        self.assertIn("🛠️  Prepare or activate the tooling environment", rendered)
        self.assertIn("g2d doctor", rendered)
        self.assertIn("python -m unittest discover -s tools/tests -v", rendered)
        self.assertIn("godot4 --headless --path game -- --test-mode", rendered)

    def test_packaging_exposes_forge2d_welcome_command(self) -> None:
        with (REPOSITORY_ROOT / "pyproject.toml").open("rb") as project_file:
            project = tomllib.load(project_file)

        scripts = project["project"]["scripts"]
        self.assertEqual(scripts["Forge2D"], "g2dtool.cli:welcome")
        self.assertEqual(scripts["g2d"], "g2dtool.cli:main")

    def test_invalid_command_exits_with_usage_code(self) -> None:
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as context:
            main(["unknown"])

        self.assertEqual(context.exception.code, 2)

    def test_doctor_returns_zero_when_all_checks_pass(self) -> None:
        report = DoctorReport((DoctorCheck("godot", "ok", "4.3.stable"),))
        with patch("g2dtool.cli.collect_doctor_report", return_value=report):
            with redirect_stdout(StringIO()):
                exit_code = main(["doctor"])

        self.assertEqual(exit_code, 0)

    def test_doctor_returns_one_for_a_missing_requirement(self) -> None:
        report = DoctorReport((DoctorCheck("godot", "missing", "not found"),))
        with patch("g2dtool.cli.collect_doctor_report", return_value=report):
            with redirect_stdout(StringIO()):
                exit_code = main(["doctor"])

        self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
