"""Tests for CLI behavior and command dispatch."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import unittest
from unittest.mock import patch

from _source_path import add_source_root

add_source_root()

from g2dtool.cli import main
from g2dtool import __version__
from g2dtool.repository import RepositoryLayout


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class CliTests(unittest.TestCase):
    def test_help_contains_control_examples(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as context:
                main(["--help"], prog="python tools/control.py")

        self.assertEqual(context.exception.code, 0)
        text = output.getvalue()
        self.assertIn("python tools/control.py doctor", text)
        self.assertIn("python tools/control.py godot4 test", text)
        self.assertIn("python tools/control.py Forge2D-Template run", text)

    def test_version_has_stable_output(self) -> None:
        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(["version"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(output.getvalue().strip(), f"g2d {__version__}")

    def test_invalid_command_uses_cli_error_code(self) -> None:
        with self.assertRaises(SystemExit) as context:
            main(["unknown"])
        self.assertEqual(context.exception.code, 2)

    def test_doctor_output_is_printed_and_exit_code_is_reported(self) -> None:
        with (
            patch(
                "g2dtool.cli.collect_doctor_report",
                return_value=type(
                    "report",
                    (),
                    {"exit_code": 1, "checks": ()},
                )(),
            ),
            patch("g2dtool.cli.format_doctor_report", return_value="DONE"),
            redirect_stdout(StringIO()) as output,
        ):
            exit_code = main(["doctor"])
            self.assertEqual(output.getvalue(), "DONE\n")

        self.assertEqual(exit_code, 1)

    def test_check_dispatches_release_gate(self) -> None:
        with patch("g2dtool.cli.run_check", return_value=0) as run_gate:
            exit_code = main(["check"])

        self.assertEqual(exit_code, 0)
        run_gate.assert_called_once_with()

    def test_template_aliases_run_the_same_mode(self) -> None:
        layout = RepositoryLayout(
            repository_root=REPOSITORY_ROOT,
            pyproject_toml=REPOSITORY_ROOT / "pyproject.toml",
            project_config=REPOSITORY_ROOT / "config" / "project.toml",
            toolchain_config=REPOSITORY_ROOT / "config" / "toolchain.toml",
            tools_directory=REPOSITORY_ROOT / "tools",
            tools_source_directory=REPOSITORY_ROOT / "tools" / "src",
            game_directory=REPOSITORY_ROOT / "game",
            venv_directory=REPOSITORY_ROOT / ".venv",
        )
        with (
            patch("g2dtool.cli.discover_repository_layout", return_value=layout),
            patch(
                "g2dtool.cli.discover_godot",
                return_value=type(
                    "Result",
                    (),
                    {
                        "status": "pass",
                        "executable": Path("/fake/godot"),
                        "version": "4.3",
                    },
                )(),
            ),
            patch(
                "g2dtool.cli.build_godot_run_command",
                return_value=["/fake/godot", "--path", str(layout.game_directory)],
            ) as build_command,
            patch("g2dtool.cli._run_external_command", return_value=42) as runner,
        ):
            exit_lower = main(["forge2d-template", "run"])
            exit_upper = main(["Forge2D-Template", "run"])

        self.assertEqual(build_command.call_count, 2)
        self.assertEqual(exit_lower, 42)
        self.assertEqual(exit_upper, 42)
        self.assertEqual(runner.call_count, 2)

    def test_missing_godot_prints_install_guidance(self) -> None:
        layout = RepositoryLayout(
            repository_root=REPOSITORY_ROOT,
            pyproject_toml=REPOSITORY_ROOT / "pyproject.toml",
            project_config=REPOSITORY_ROOT / "config" / "project.toml",
            toolchain_config=REPOSITORY_ROOT / "config" / "toolchain.toml",
            tools_directory=REPOSITORY_ROOT / "tools",
            tools_source_directory=REPOSITORY_ROOT / "tools" / "src",
            game_directory=REPOSITORY_ROOT / "game",
            venv_directory=REPOSITORY_ROOT / ".venv",
        )
        with (
            patch("g2dtool.cli.discover_repository_layout", return_value=layout),
            patch(
                "g2dtool.cli.discover_godot",
                return_value=type(
                    "Result",
                    (),
                    {
                        "status": "fail",
                        "executable": None,
                        "version": None,
                    },
                )(),
            ),
        ):
            from io import StringIO
            from contextlib import redirect_stdout
            output = StringIO()

            with redirect_stdout(output):
                exit_code = main(["godot4", "run"])

        self.assertEqual(exit_code, 1)
        self.assertIn("Godot 4 wurde nicht gefunden.", output.getvalue())
        self.assertIn("python tools/control.py install", output.getvalue())
