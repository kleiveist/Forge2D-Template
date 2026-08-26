"""Tests for local install workflow behavior."""

from pathlib import Path
from tempfile import TemporaryDirectory
import os
import io
import sys
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout

from _source_path import add_source_root

add_source_root()

from g2dtool.install import run_install
from g2dtool.godot import CommandResult, PASS


class InstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        (self.root / ".git").mkdir(parents=True)
        (self.root / "config").mkdir()
        (self.root / "config" / "project.toml").write_text(
            "schema_version = 1\n\n[project]\ntemplate_id = \"forge2d\"\n"
            'display_name = "Forge2D"\nrepository_language = "en"\n'
            'default_cli_name = "g2d"\ngodot_project_path = "game/project.godot"\nlicense_status = "undecided"\n',
            encoding="utf-8",
        )
        (self.root / "config" / "toolchain.toml").write_text(
            "schema_version = 1\n\n[python]\nminimum_version = \"3.11\"\n"
            'runtime_dependencies = ["requests"]\ndevelopment_dependencies = ["pytest"]\n\n'
            "[godot]\nrequired_major = 4\nexecutable = \"\"\n"
            'executable_candidates = ["godot4", "godot"]\n',
            encoding="utf-8",
        )
        (self.root / "game").mkdir()
        (self.root / "game" / "project.godot").write_text(
            '[application]\nrun/main_scene="res://scenes/bootstrap.tscn"\n',
            encoding="utf-8",
        )
        (self.root / "tools").mkdir()
        (self.root / "tools" / "src").mkdir(parents=True)
        (self.root / "tools" / "src" / "g2dtool").mkdir(parents=True)
        (self.root / "pyproject.toml").write_text("[project]\ndependencies = []\n", encoding="utf-8")
        (self.root / "game" / "scenes").mkdir()

    def test_dry_run_shows_planned_commands_without_execution(self) -> None:
        executed: list[tuple[str, ...]] = []

        def fake_runner(command):
            executed.append(tuple(command))
            return CommandResult(0, "4.3.stable\n", "")

        with (
            patch("g2dtool.install._linux_distribution", return_value="arch"),
            patch("g2dtool.install.shutil.which", return_value="/usr/bin/pacman"),
        ):
            code = run_install(
                start=self.root,
                dry_run=True,
                yes=True,
                run_command=fake_runner,
                find_tool=lambda name: "/usr/bin/pacman" if name == "pacman" else None,
            )
        self.assertEqual(code, 1)
        self.assertFalse(
            any(cmd and cmd[:3] == ("sudo", "pacman", "-S") for cmd in executed)
        )
        self.assertFalse(any("pip" in cmd for cmd in executed))
        self.assertFalse(any(cmd[:2] == (sys.executable, "-m") and cmd[2:3] == ["venv"] for cmd in executed))

    def test_dry_run_prints_godot_pacman_plan_on_arch(self) -> None:
        executed: list[tuple[str, ...]] = []
        output = io.StringIO()

        def fake_runner(command):
            executed.append(tuple(command))
            return CommandResult(0, "4.3.stable\n", "")

        with (
            redirect_stdout(output),
            patch("g2dtool.install._linux_distribution", return_value="arch"),
            patch("g2dtool.install.shutil.which", return_value="/usr/bin/pacman"),
        ):
            code = run_install(
                start=self.root,
                dry_run=True,
                yes=True,
                run_command=fake_runner,
                find_tool=lambda name: "/usr/bin/pacman" if name == "pacman" else None,
            )
        self.assertEqual(code, 1)
        text = output.getvalue()
        self.assertIn("[DRY-RUN] sudo pacman -S --needed godot", text)
        self.assertNotIn("sudo pacman -S --needed godot", "".join(" ".join(c) for c in executed))

    def test_venv_preparation_is_idempotent(self) -> None:
        executed: list[tuple[str, ...]] = []

        def fake_runner(command):
            executed.append(tuple(command))
            if command and str(command[0]).endswith("godot") and command[1:] == ("--version",):
                return CommandResult(0, "4.3.stable\n", "")
            return CommandResult(0, "", "")

        venv = self.root / ".venv" / ("Scripts" if os.name == "nt" else "bin")
        venv.mkdir(parents=True)
        (venv / ("python.exe" if os.name == "nt" else "python")).write_text("", encoding="utf-8")

        code = run_install(
            start=self.root,
            dry_run=False,
            yes=True,
            run_command=fake_runner,
            find_tool=lambda name: "/fake/godot" if name in {"godot4", "godot"} else None,
        )
        self.assertEqual(code, 0)
        self.assertFalse(any(str(cmd[0]).endswith("venv") for cmd in executed), executed)

    def test_arch_install_is_optional_and_confirmed_with_yes(self) -> None:
        executed: list[tuple[str, ...]] = []

        def fake_runner(command):
            executed.append(tuple(command))
            if command and str(command[0]).endswith("godot") and command[1:] == ("--version",):
                return CommandResult(1, "", "not found")
            return CommandResult(0, "", "")

        with (
            patch("g2dtool.install._linux_distribution", return_value="arch"),
            patch("g2dtool.install.shutil.which", return_value="/usr/bin/pacman"),
        ):
            code = run_install(
                start=self.root,
                dry_run=False,
                yes=True,
                run_command=fake_runner,
                find_tool=lambda name: (
                    "/usr/bin/pacman" if name == "pacman" else "/fake/godot"
                ),
            )

        self.assertEqual(code, 1)
        self.assertTrue(("sudo", "pacman", "-S", "--needed", "godot") in executed)

    def test_non_arch_shows_manual_steps(self) -> None:
        output = io.StringIO()
        with (
            redirect_stdout(output),
            patch("g2dtool.install._linux_distribution", return_value="debian"),
            patch("g2dtool.install.shutil.which", return_value="/usr/bin/pip"),
        ):
            code = run_install(
                start=self.root,
                dry_run=True,
                yes=True,
                run_command=lambda command: CommandResult(0, "", ""),
                find_tool=lambda name: "/fake-tool" if name == "godot" else None,
            )

        self.assertEqual(code, 1)
        self.assertIn("Bitte installieren Sie Godot 4 manuell.", output.getvalue())


if __name__ == "__main__":
    unittest.main()
