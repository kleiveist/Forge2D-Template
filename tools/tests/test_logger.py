"""Tests for emoji output helpers."""

import unittest

from _source_path import add_source_root

add_source_root()

from g2dtool.logger import (
    dry_run,
    help_line,
    join_command,
    log_status,
)


class LoggerTests(unittest.TestCase):
    def test_status_line_includes_emoji_and_status_label(self) -> None:
        line = log_status("pass", "repository", "found")
        self.assertEqual(line, "✅ [PASS] repository: found")

    def test_dry_run_prefix_keeps_keyword(self) -> None:
        line = dry_run("sudo pacman -S --needed godot")
        self.assertEqual(line, "🛠️ [DRY-RUN] sudo pacman -S --needed godot")

    def test_help_line_keeps_message(self) -> None:
        line = help_line("python tools/control.py doctor")
        self.assertEqual(line, "💡 [TIP] python tools/control.py doctor")

    def test_join_command_handles_objects(self) -> None:
        self.assertEqual(join_command(["python", "-m", "venv"]), "python -m venv")
