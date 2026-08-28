"""Tests for safe cross-platform local installation behavior."""

from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from _source_path import add_source_root

add_source_root()

from g2dtool.install import (
    CommandResult,
    SystemAction,
    SystemPlan,
    _apply_system_plan,
    run_install,
)


class FakeRunner:
    """Return controlled probe/install results and record every child command."""

    def __init__(
        self,
        *,
        apt_godot_major: int | None = None,
        bootstrap_ready: bool = True,
        create_venv: bool = False,
        fail_package_manager: bool = False,
        fail_dependency_install: bool = False,
    ) -> None:
        self.apt_godot_major = apt_godot_major
        self.bootstrap_ready = bootstrap_ready
        self.create_venv = create_venv
        self.fail_package_manager = fail_package_manager
        self.fail_dependency_install = fail_dependency_install
        self.executed: list[tuple[str, ...]] = []

    def __call__(self, command) -> CommandResult:
        arguments = tuple(map(str, command))
        self.executed.append(arguments)

        if arguments[1:] == ("-c", "import venv"):
            return self._bootstrap_result("venv module unavailable")
        if arguments[1:] == ("-m", "ensurepip", "--version"):
            return self._bootstrap_result("ensurepip unavailable", "pip 24.0")
        if arguments[:3] == ("apt-cache", "policy", "godot"):
            if self.apt_godot_major is None:
                return CommandResult(100, "", "No packages found")
            return CommandResult(
                0,
                "godot:\n"
                "  Installed: (none)\n"
                f"  Candidate: {self.apt_godot_major}.3.0-1\n",
                "",
            )
        if arguments[-1:] == ("--version",) and "godot" in arguments[0].lower():
            return CommandResult(0, "4.7.2.stable\n", "")
        if self.fail_package_manager and any(
            name in arguments for name in ("apt-get", "pacman", "winget", "brew")
        ):
            return CommandResult(42, "", "permission denied by package manager")
        if len(arguments) >= 3 and arguments[1:3] == ("-m", "venv"):
            if self.create_venv:
                venv = Path(arguments[-1])
                binary = venv / "bin" / "python"
                binary.parent.mkdir(parents=True, exist_ok=True)
                binary.write_text("", encoding="utf-8")
            return CommandResult(0, "", "")
        if "pip" in arguments:
            if (
                self.fail_dependency_install
                and "install" in arguments
                and any(value.startswith("requests") for value in arguments)
            ):
                return CommandResult(1, "", "package index is unavailable")
            if "--version" in arguments:
                return CommandResult(0, "pip 24.0 from .venv\n", "")
            if "show" in arguments:
                return CommandResult(0, "Name: package\nVersion: 1.0\n", "")
            return CommandResult(0, "", "")
        return CommandResult(0, "", "")

    def _bootstrap_result(self, failure: str, output: str = "") -> CommandResult:
        if self.bootstrap_ready:
            return CommandResult(0, output, "")
        return CommandResult(1, "", failure)


class InstallTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repository"
        (self.root / ".git").mkdir(parents=True)
        (self.root / "config").mkdir()
        (self.root / "config" / "project.toml").write_text(
            "schema_version = 1\n\n[project]\ntemplate_id = \"forge2d-template\"\n"
            'display_name = "Forge2D Template"\nversion = "0.1.0"\n'
            'repository_language = "en"\ndefault_cli_name = "g2d"\n'
            'godot_project_path = "game/project.godot"\nlicense_status = "selected"\n',
            encoding="utf-8",
        )
        (self.root / "config" / "toolchain.toml").write_text(
            "schema_version = 1\n\n[python]\nminimum_version = \"3.11\"\n"
            'runtime_dependencies = ["requests>=2"]\n'
            'development_dependencies = ["pytest>=8,<9"]\n\n'
            "[godot]\nrequired_major = 4\nexecutable = \"\"\n"
            'executable_candidates = ["godot4", "godot"]\n',
            encoding="utf-8",
        )
        (self.root / "game").mkdir()
        (self.root / "game" / "project.godot").write_text(
            '[application]\nrun/main_scene="res://scenes/bootstrap.tscn"\n',
            encoding="utf-8",
        )
        (self.root / "tools" / "src" / "g2dtool").mkdir(parents=True)
        (self.root / "pyproject.toml").write_text(
            "[project]\ndependencies = []\n",
            encoding="utf-8",
        )

    def test_linux_apt_dry_run_plans_only_verified_godot_4(self) -> None:
        runner = FakeRunner(apt_godot_major=4)
        output = self._dry_run(
            runner,
            system="Linux",
            distribution="ubuntu",
            tools=("apt-get", "apt-cache", "sudo"),
        )

        self.assertIn("sudo apt-get update", output)
        self.assertIn(
            "sudo apt-get install --yes --no-install-recommends godot",
            output,
        )
        self.assertFalse(any("apt-get" in command for command in runner.executed))

    def test_linux_apt_refuses_godot_3_candidate(self) -> None:
        runner = FakeRunner(apt_godot_major=3)
        output = self._dry_run(
            runner,
            system="Linux",
            distribution="debian",
            tools=("apt-get", "apt-cache", "sudo"),
        )

        self.assertIn("APT offers Godot 3.x", output)
        self.assertIn("refusing the incompatible package", output)
        self.assertNotIn("apt-get install", output)
        self.assertIn("requires manual installation", output)

    def test_linux_pacman_dry_run_uses_idempotent_noninteractive_command(self) -> None:
        runner = FakeRunner()
        output = self._dry_run(
            runner,
            system="Linux",
            distribution="arch",
            tools=("pacman", "sudo"),
        )

        self.assertIn(
            "sudo pacman -S --needed --noconfirm godot",
            output,
        )
        self.assertFalse(any("pacman" in command for command in runner.executed))

    def test_windows_dry_run_uses_exact_winget_package_and_agreements(self) -> None:
        runner = FakeRunner()
        output = self._dry_run(
            runner,
            system="Windows",
            tools=("winget",),
        )

        self.assertIn("winget install --id GodotEngine.GodotEngine --exact", output)
        self.assertIn("--source winget", output)
        self.assertIn("--accept-package-agreements", output)
        self.assertIn("--accept-source-agreements", output)
        self.assertIn(str(Path("Scripts") / "python.exe"), output)
        self.assertFalse(any("winget" in command for command in runner.executed))

    def test_macos_dry_run_uses_homebrew_cask(self) -> None:
        runner = FakeRunner()
        output = self._dry_run(
            runner,
            system="Darwin",
            tools=("brew",),
        )

        self.assertIn("brew install --cask godot", output)
        self.assertFalse(any("brew" in command for command in runner.executed))

    def test_dry_run_never_prompts_executes_changes_or_creates_venv(self) -> None:
        runner = FakeRunner()
        before = sorted(path.relative_to(self.root) for path in self.root.rglob("*"))

        output = StringIO()
        with redirect_stdout(output):
            code = run_install(
                start=self.root,
                dry_run=True,
                yes=False,
                run_command=runner,
                find_tool=self._finder("pacman", "sudo"),
                confirm=lambda _question: self.fail("dry-run must not prompt"),
                system_name="Linux",
                distribution="arch",
                python_executable="/fake/python",
                is_elevated=False,
            )

        after = sorted(path.relative_to(self.root) for path in self.root.rglob("*"))
        self.assertEqual(code, 0)
        self.assertEqual(before, after)
        self.assertFalse((self.root / ".venv").exists())
        self.assertFalse(
            any(
                any(name in command for name in ("apt-get", "pacman", "winget", "brew"))
                for command in runner.executed
            )
        )
        self.assertIn("Dry-run complete; no changes were made", output.getvalue())

    def test_dry_run_plans_apt_venv_repair_when_bootstrap_is_missing(self) -> None:
        runner = FakeRunner(bootstrap_ready=False)
        output = self._dry_run(
            runner,
            system="Linux",
            distribution="ubuntu",
            tools=("apt-get", "apt-cache", "sudo", "godot4"),
        )

        self.assertIn("python3-venv", output)
        self.assertIn("Create repository .venv", output)

    def test_healthy_venv_avoids_unneeded_system_bootstrap_repair(self) -> None:
        venv_python = self.root / ".venv" / "bin" / "python"
        venv_python.parent.mkdir(parents=True)
        venv_python.write_text("", encoding="utf-8")
        runner = FakeRunner(bootstrap_ready=False)
        output = self._dry_run(
            runner,
            system="Linux",
            distribution="ubuntu",
            tools=("apt-get", "apt-cache", "sudo", "godot4"),
        )

        self.assertIn("existing .venv pip remains usable", output)
        self.assertNotIn("python3-venv", output)
        self.assertNotIn("apt-get update", output)

    def test_old_python_dry_run_plans_winget_python_and_requires_rerun(self) -> None:
        runner = FakeRunner()
        output = StringIO()
        with redirect_stdout(output):
            code = run_install(
                start=self.root,
                dry_run=True,
                yes=True,
                run_command=runner,
                find_tool=self._finder("winget"),
                system_name="Windows",
                python_version=(3, 10),
                python_executable="C:/Python310/python.exe",
            )

        self.assertEqual(code, 0)
        text = output.getvalue()
        self.assertIn("Python.Python.3.11", text)
        self.assertIn("py -3.11 tools/control.py install", text)
        self.assertNotIn("Install local tooling in .venv", text)

    def test_old_python_without_package_manager_fails_with_solution(self) -> None:
        runner = FakeRunner()
        output = StringIO()
        with redirect_stdout(output):
            code = run_install(
                start=self.root,
                dry_run=True,
                yes=True,
                run_command=runner,
                find_tool=self._finder(),
                system_name="OtherOS",
                python_version=(3, 10),
                python_executable="python",
            )

        self.assertEqual(code, 1)
        self.assertIn("Python 3.11 or newer is required", output.getvalue())
        self.assertIn("Run `python3.11 tools/control.py install`", output.getvalue())

    def test_yes_executes_plan_without_calling_confirm(self) -> None:
        runner = FakeRunner()
        plan = SystemPlan(
            actions=(
                SystemAction(
                    "Install Godot",
                    ("winget", "install", "GodotEngine.GodotEngine"),
                    "Install it manually.",
                ),
            ),
            notes=(),
            godot_planned=True,
        )

        applied = _apply_system_plan(
            plan,
            dry_run=False,
            yes=True,
            confirm=lambda _question: self.fail("--yes must bypass confirmation"),
            run_command=runner,
        )

        self.assertTrue(applied)
        self.assertIn(
            ("winget", "install", "GodotEngine.GodotEngine"),
            runner.executed,
        )

    def test_declined_system_plan_executes_nothing(self) -> None:
        runner = FakeRunner()
        plan = SystemPlan(
            actions=(
                SystemAction(
                    "Install Godot",
                    ("brew", "install", "--cask", "godot"),
                    "Install it manually.",
                ),
            ),
            notes=(),
            godot_planned=True,
        )

        applied = _apply_system_plan(
            plan,
            dry_run=False,
            yes=False,
            confirm=lambda _question: "n",
            run_command=runner,
        )

        self.assertFalse(applied)
        self.assertEqual(runner.executed, [])

    def test_yes_recreates_only_broken_local_venv_and_uses_venv_pip(self) -> None:
        (self.root / ".venv").mkdir()
        runner = FakeRunner(create_venv=True)
        output = StringIO()

        with redirect_stdout(output):
            code = run_install(
                start=self.root,
                dry_run=False,
                yes=True,
                run_command=runner,
                find_tool=self._finder("godot4", "pytest"),
                system_name="Linux",
                distribution="other",
                python_executable="/fake/python",
                is_elevated=False,
            )

        self.assertEqual(code, 0, output.getvalue())
        venv_command = next(command for command in runner.executed if "venv" in command)
        self.assertIn("--clear", venv_command)
        venv_python = (self.root / ".venv" / "bin" / "python").resolve()
        pip_commands = [command for command in runner.executed if "pip" in command]
        self.assertTrue(pip_commands)
        self.assertTrue(
            all(Path(command[0]).resolve() == venv_python for command in pip_commands)
        )
        self.assertTrue(any("show" in command and "pytest" in command for command in pip_commands))
        self.assertNotIn(("/fake/python", "-m", "pip"), pip_commands)

    def test_broken_venv_is_not_replaced_after_declined_confirmation(self) -> None:
        (self.root / ".venv").mkdir()
        runner = FakeRunner()
        output = StringIO()

        with redirect_stdout(output):
            code = run_install(
                start=self.root,
                dry_run=False,
                yes=False,
                run_command=runner,
                find_tool=self._finder("godot4"),
                confirm=lambda _question: "n",
                system_name="Linux",
                distribution="other",
                python_executable="/fake/python",
                is_elevated=False,
            )

        self.assertEqual(code, 1)
        self.assertIn("Existing virtual environment is incomplete", output.getvalue())
        self.assertFalse(any("--clear" in command for command in runner.executed))

    def test_healthy_venv_is_reused_and_declared_packages_are_verified(self) -> None:
        venv_python = self.root / ".venv" / "bin" / "python"
        venv_python.parent.mkdir(parents=True)
        venv_python.write_text("", encoding="utf-8")
        runner = FakeRunner()

        code = run_install(
            start=self.root,
            dry_run=False,
            yes=True,
            run_command=runner,
            find_tool=self._finder("godot4", "pytest"),
            system_name="Linux",
            distribution="other",
            python_executable="/fake/python",
            is_elevated=False,
        )

        self.assertEqual(code, 0)
        self.assertFalse(
            any(len(command) >= 3 and command[1:3] == ("-m", "venv") for command in runner.executed)
        )
        self.assertTrue(any("check" in command for command in runner.executed if "pip" in command))
        self.assertTrue(any("requests" in command for command in runner.executed))
        self.assertTrue(any("pytest" in command for command in runner.executed))

    def test_package_manager_failure_reports_cause_command_and_recovery(self) -> None:
        runner = FakeRunner(fail_package_manager=True)
        output = StringIO()

        with redirect_stdout(output):
            code = run_install(
                start=self.root,
                dry_run=False,
                yes=True,
                run_command=runner,
                find_tool=self._finder("pacman", "sudo"),
                system_name="Linux",
                distribution="arch",
                python_executable="/fake/python",
                is_elevated=False,
            )

        self.assertEqual(code, 1)
        text = output.getvalue()
        self.assertIn("exited with code 42", text)
        self.assertIn("permission denied by package manager", text)
        self.assertIn("sudo pacman -S", text)
        self.assertIn("Synchronize Arch repositories", text)

    def test_python_package_failure_reports_venv_only_recovery(self) -> None:
        venv_python = self.root / ".venv" / "bin" / "python"
        venv_python.parent.mkdir(parents=True)
        venv_python.write_text("", encoding="utf-8")
        runner = FakeRunner(fail_dependency_install=True)
        output = StringIO()

        with redirect_stdout(output):
            code = run_install(
                start=self.root,
                dry_run=False,
                yes=True,
                run_command=runner,
                find_tool=self._finder("godot4"),
                system_name="Linux",
                distribution="other",
                python_executable="/fake/python",
                is_elevated=False,
            )

        self.assertEqual(code, 1)
        text = output.getvalue()
        self.assertIn("Install declared Python packages into .venv", text)
        self.assertIn("package index is unavailable", text)
        pip_commands = [command for command in runner.executed if "pip" in command]
        self.assertTrue(
            all(
                Path(command[0]).resolve() == venv_python.resolve()
                for command in pip_commands
            )
        )

    def test_missing_bootstrap_without_manager_has_actionable_error(self) -> None:
        runner = FakeRunner(bootstrap_ready=False)
        output = StringIO()

        with redirect_stdout(output):
            code = run_install(
                start=self.root,
                dry_run=True,
                yes=True,
                run_command=runner,
                find_tool=self._finder("godot4"),
                system_name="Linux",
                distribution="unknown",
                python_executable="/fake/python",
                is_elevated=False,
            )

        self.assertEqual(code, 1)
        self.assertIn("cannot create a pip-enabled virtual environment", output.getvalue())
        self.assertIn("standard venv and ensurepip", output.getvalue())

    def test_invalid_toolchain_configuration_is_reported_as_user_error(self) -> None:
        toolchain_path = self.root / "config" / "toolchain.toml"
        toolchain_path.write_text(
            toolchain_path.read_text(encoding="utf-8").replace(
                'minimum_version = "3.11"',
                'minimum_version = "not-a-version"',
            ),
            encoding="utf-8",
        )
        output = StringIO()

        with redirect_stdout(output):
            code = run_install(
                start=self.root,
                dry_run=True,
                yes=True,
                run_command=FakeRunner(),
                find_tool=self._finder(),
            )

        self.assertEqual(code, 1)
        self.assertIn("Cannot read toolchain requirements", output.getvalue())
        self.assertIn("Review", output.getvalue())

    def test_ci_runs_side_effect_free_dry_run_on_all_native_platforms(self) -> None:
        repository = Path(__file__).resolve().parents[2]
        workflow = (repository / ".github" / "workflows" / "ci.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "os: [ubuntu-latest, windows-latest, macos-latest]",
            workflow,
        )
        self.assertIn("Verify side-effect-free installer dry run", workflow)
        self.assertIn(
            '[sys.executable, "tools/control.py", "install", "--dry-run", "--yes"]',
            workflow,
        )
        self.assertIn('raise SystemExit("Installer dry-run created .venv")', workflow)

    def _dry_run(
        self,
        runner: FakeRunner,
        *,
        system: str,
        tools: tuple[str, ...],
        distribution: str | None = None,
    ) -> str:
        output = StringIO()
        venv_existed = (self.root / ".venv").exists()
        with redirect_stdout(output):
            code = run_install(
                start=self.root,
                dry_run=True,
                yes=True,
                run_command=runner,
                find_tool=self._finder(*tools),
                confirm=lambda _question: self.fail("dry-run must not prompt"),
                system_name=system,
                distribution=distribution,
                python_executable="/fake/python",
                is_elevated=False,
            )
        self.assertEqual(code, 0, output.getvalue())
        self.assertEqual((self.root / ".venv").exists(), venv_existed)
        return output.getvalue()

    @staticmethod
    def _finder(*tools: str):
        available = {name: f"/fake/{name}" for name in tools}
        return available.get


if __name__ == "__main__":
    unittest.main()
