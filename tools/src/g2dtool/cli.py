"""Provide the command-line interface for Forge2D Template repository tooling."""

from __future__ import annotations

from collections.abc import Sequence
import argparse
import textwrap

from g2dtool import __version__
from g2dtool.check import run_check
from g2dtool.config import ProjectConfigError
from g2dtool.doctor import collect_doctor_report, format_doctor_report
from g2dtool.logger import error, print_help_line
from g2dtool.godot import (
    FAIL,
    PASS,
    build_godot_editor_command,
    build_godot_run_command,
    build_godot_test_command,
    discover_godot,
    run_godot_command,
)
from g2dtool.install import run_install
from g2dtool.repository import discover_repository_layout

EXIT_OK = 0
EXIT_REQUIREMENT_MISSING = 1
EXIT_USAGE = 2
EXIT_INTERRUPTED = 130

WELCOME_TEXT = textwrap.dedent(
    """\
    🧭 Forge2D Template developer entry point

    🔍 Inspect the repository
      python tools/control.py --help
      python tools/control.py doctor
      python tools/control.py install
      python tools/control.py check

    🎮 Run or test the project
      python tools/control.py godot4
      python tools/control.py godot4 test
      python tools/control.py forge2d-template run
      python tools/control.py Forge2D-Template run
    """
)


def build_parser(prog: str = "g2d") -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="Inspect and maintain a Forge2D Template repository.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              python tools/control.py doctor
              python tools/control.py install
              python tools/control.py install --dry-run
              python tools/control.py check
              python tools/control.py godot4 test
              python tools/control.py forge2d-template run
              python tools/control.py Forge2D-Template run
            """
        ),
    )
    commands = parser.add_subparsers(dest="command", required=True)

    version_parser = commands.add_parser("version", help="show the tooling version")
    version_parser.set_defaults(handler=_show_version)

    doctor_parser = commands.add_parser(
        "doctor", help="diagnose the Forge2D Template local and external tooling"
    )
    doctor_parser.set_defaults(handler=_run_doctor)

    check_parser = commands.add_parser(
        "check", help="run doctor, Python tests, and Godot smoke test"
    )
    check_parser.set_defaults(handler=_run_check)

    install_parser = commands.add_parser(
        "install", help="prepare a local development environment"
    )
    install_parser.add_argument("--dry-run", action="store_true", help="show planned steps")
    install_parser.add_argument("--yes", action="store_true", help="auto-accept prompts")
    install_parser.set_defaults(handler=_run_install)

    godot_parser = commands.add_parser(
        "godot4", aliases=["godot"], help="run godot commands for this repository"
    )
    godot_parser.add_argument(
        "mode",
        nargs="?",
        choices=("editor", "run", "test"),
        default="editor",
        help="godot4 command mode",
    )
    godot_parser.add_argument("args", nargs=argparse.REMAINDER)
    godot_parser.set_defaults(handler=_run_godot_command)

    template_parser = commands.add_parser(
        "forge2d-template",
        aliases=["Forge2D-Template"],
        help="alias for running the template project",
    )
    template_parser.add_argument(
        "mode",
        nargs="?",
        choices=("run",),
        default="run",
        help="run mode",
    )
    template_parser.add_argument("args", nargs=argparse.REMAINDER)
    template_parser.set_defaults(handler=_run_template_project)

    return parser


def main(arguments: Sequence[str] | None = None, prog: str = "g2d") -> int:
    """Run the CLI and return a stable process exit code."""

    try:
        options = build_parser(prog=prog).parse_args(arguments)
        return int(options.handler(options))
    except SystemExit as error:
        raise
    except ProjectConfigError as error:
        error(f"Error: {error}")
        return EXIT_USAGE
    except KeyboardInterrupt:
        error("Aborted.")
        return EXIT_INTERRUPTED
    except Exception as exc:
        error(f"Internal error: {exc}")
        return EXIT_USAGE


def welcome() -> int:
    """Print the concise developer onboarding screen."""

    print(WELCOME_TEXT)
    return EXIT_OK


def _show_version(_options: argparse.Namespace) -> int:
    print(f"g2d {__version__}")
    return EXIT_OK


def _run_doctor(_options: argparse.Namespace) -> int:
    report = collect_doctor_report()
    print(format_doctor_report(report))
    return report.exit_code


def _run_check(_options: argparse.Namespace) -> int:
    return run_check()


def _run_install(options: argparse.Namespace) -> int:
    return run_install(
        dry_run=options.dry_run,
        yes=options.yes,
    )


def _run_godot_command(options: argparse.Namespace) -> int:
    layout = discover_repository_layout()
    project_file = layout.game_directory / "project.godot"
    user_arguments = _normalize_arguments(options.args)

    result = discover_godot(layout.repository_root)
    if result.status != PASS:
        error("Godot 4 wurde nicht gefunden.")
        print()
        print_help_line("Prüfen:")
        print_help_line("  python tools/control.py doctor")
        print()
        print_help_line("Installieren:")
        print_help_line("  python tools/control.py install")
        return EXIT_REQUIREMENT_MISSING
    if result.executable is None:
        return EXIT_REQUIREMENT_MISSING

    if options.mode == "editor":
        command = build_godot_editor_command(
            result.executable, layout.game_directory, user_arguments
        )
    elif options.mode == "run":
        command = build_godot_run_command(
            result.executable, layout.game_directory, user_arguments
        )
    elif options.mode == "test":
        command = build_godot_test_command(
            result.executable, layout.game_directory, project_file, user_arguments
        )
    else:
        raise RuntimeError(f"Unsupported godot mode: {options.mode}")

    return _run_external_command(command)


def _run_template_project(options: argparse.Namespace) -> int:
    options.mode = "run"
    return _run_godot_command(options)


def _run_external_command(command: Sequence[str]) -> int:
    try:
        return run_godot_command(command)
    except FileNotFoundError:
        error("Godot executable not found.")
        return EXIT_REQUIREMENT_MISSING
    except KeyboardInterrupt:
        error("Aborted.")
        return EXIT_INTERRUPTED


def _normalize_arguments(arguments: Sequence[str]) -> tuple[str, ...]:
    if arguments and arguments[0] == "--":
        return tuple(arguments[1:])
    return tuple(arguments)
