"""Tests for `tools/control.py` bootstrap behavior."""

from pathlib import Path
from tempfile import TemporaryDirectory
from contextlib import redirect_stderr
from io import StringIO
import importlib.util
import subprocess
import sys
import unittest
from unittest.mock import patch


class ControlTests(unittest.TestCase):
    def test_control_rejects_old_python_before_importing_tooling(self) -> None:
        repository_root = Path(__file__).resolve().parents[2]
        control_path = repository_root / "tools" / "control.py"
        spec = importlib.util.spec_from_file_location("control_under_test", control_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        output = StringIO()

        with (
            patch.object(
                module.sys,
                "version_info",
                type("Version", (), {"major": 3, "minor": 10})(),
            ),
            patch.object(module, "_bootstrap_python_path") as bootstrap,
            redirect_stderr(output),
        ):
            code = module.main([])

        self.assertEqual(code, 1)
        bootstrap.assert_not_called()
        self.assertIn("requires Python >= 3.11", output.getvalue())
        self.assertIn("operating-system package manager", output.getvalue())

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
