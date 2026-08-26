"""Provide the command-line interface for Forge2D repository tooling."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from g2dtool import __version__
from g2dtool.doctor import collect_doctor_report, format_doctor_report


EXIT_OK = 0
EXIT_REQUIREMENT_MISSING = 1
EXIT_USAGE = 2

WELCOME_TEXT = """\
🧭 Forge2D developer entry point

🛠️  Prepare or activate the tooling environment
  python3 -m venv .venv
  . .venv/bin/activate
  python -m pip install --no-deps -e .

🔎 Inspect the repository
  g2d --help
  g2d version
  g2d doctor

🧪 Run the Python tests
  python -m unittest discover -s tools/tests -v

🎮 Run the Godot smoke scene
  godot4 --headless --path game -- --test-mode

📚 Open the documentation index
  docs/README.md
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="g2d",
        description="Inspect and maintain a Forge2D repository.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    version_parser = commands.add_parser("version", help="Show the g2d version.")
    version_parser.set_defaults(handler=_show_version)

    doctor_parser = commands.add_parser(
        "doctor",
        help="Check the repository and required local tools.",
    )
    doctor_parser.set_defaults(handler=_run_doctor)
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    """Run the CLI and return a stable process exit code."""

    options = build_parser().parse_args(arguments)
    return int(options.handler(options))


def welcome() -> int:
    """Print the concise developer onboarding screen for the `Forge2D` alias."""

    print(WELCOME_TEXT)
    return EXIT_OK


def _show_version(_options: argparse.Namespace) -> int:
    print(f"g2d {__version__}")
    return EXIT_OK


def _run_doctor(_options: argparse.Namespace) -> int:
    report = collect_doctor_report()
    print(format_doctor_report(report))
    return report.exit_code
