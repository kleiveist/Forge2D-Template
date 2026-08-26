"""Tests for `tools/control.py` bootstrap behavior."""

from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest


class ControlTests(unittest.TestCase):
    def test_control_starts_from_nested_directory(self) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        control_path = repository_root / "tools" / "control.py"

        with TemporaryDirectory() as temp:
            nested = Path(temp) / "nested" / "deep"
            nested.mkdir(parents=True)
            result = subprocess.run(
                [sys.executable, str(control_path), "--help"],
                cwd=nested,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("python tools/control.py doctor", result.stdout)

    def test_control_can_run_version_without_install(self) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        control_path = repository_root / "tools" / "control.py"

        with TemporaryDirectory() as temp:
            nested = Path(temp) / "nested"
            nested.mkdir()
            result = subprocess.run(
                [sys.executable, str(control_path), "version"],
                cwd=nested,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("g2d", result.stdout)
