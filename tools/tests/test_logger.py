"""Tests for emoji output helpers."""

import unittest

from _source_path import add_source_root

add_source_root()

from g2dtool.logger import (
    _print,
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

    def test_print_replaces_unicode_on_encoding_error(self) -> None:
        class FailingThenRecoveringStream:
            def __init__(self) -> None:
                self.encoding = "cp1252"
                self.calls: list[str] = []
                self._attempt = 0

            def write(self, _text: str) -> int:
                if self._attempt == 0:
                    self._attempt += 1
                    raise UnicodeEncodeError("cp1252", "💥", 0, 1, "cannot encode")
                self.calls.append(_text)
                return len(_text)

            def flush(self) -> None:
                pass

        stream = FailingThenRecoveringStream()
        _print("🚀 testing unicode", stream=stream)

        self.assertGreaterEqual(len(stream.calls), 1)
        self.assertNotIn("🚀", "".join(stream.calls))
