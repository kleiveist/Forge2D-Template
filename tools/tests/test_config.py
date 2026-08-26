"""Tests for project and toolchain configuration validation."""

from pathlib import Path
from tempfile import TemporaryDirectory
import textwrap
import unittest

from _source_path import add_source_root

add_source_root()

from g2dtool.config import (
    ProjectConfigError,
    ToolchainConfigError,
    load_project_config,
    load_toolchain_config,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class ProjectConfigTests(unittest.TestCase):
    def test_loads_and_validates_baseline_project_configuration(self) -> None:
        config = load_project_config(REPOSITORY_ROOT / "config" / "project.toml")
        self.assertEqual(config.schema_version, 1)
        self.assertEqual(config.template_id, "forge2d-template")
        self.assertEqual(config.display_name, "Forge2D Template")
        self.assertEqual(config.version, "0.1.0")
        self.assertEqual(config.repository_language, "en")
        self.assertEqual(config.default_cli_name, "g2d")
        self.assertEqual(config.godot_project_path.as_posix(), "game/project.godot")
        self.assertEqual(config.license_status, "selected")

    def test_rejects_unsupported_schema(self) -> None:
        self.assert_invalid_config("schema_version = 2", "schema_version")

    def test_rejects_absolute_godot_path(self) -> None:
        replacement = 'godot_project_path = "/opt/forge2d-template/project.godot"'
        self.assert_invalid_config(replacement, "repository-relative")

    def assert_invalid_config(self, replacement: str, message: str) -> None:
        baseline = textwrap.dedent(
            """\
            schema_version = 1

            [project]
            template_id = "forge2d-template"
            display_name = "Forge2D Template"
            version = "0.1.0"
            repository_language = "en"
            default_cli_name = "g2d"
            godot_project_path = "game/project.godot"
            license_status = "selected"
            """
        )
        if replacement.startswith("schema_version"):
            baseline = baseline.replace("schema_version = 1", replacement)
        else:
            baseline = baseline.replace(
                'godot_project_path = "game/project.godot"', replacement
            )

        temporary_directory = TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        config_path = Path(temporary_directory.name) / "project.toml"
        config_path.write_text(baseline, encoding="utf-8")
        with self.assertRaisesRegex(ProjectConfigError, message):
            load_project_config(config_path)


class ToolchainConfigTests(unittest.TestCase):
    def test_toolchain_config_loads_expected_fields(self) -> None:
        config = load_toolchain_config(REPOSITORY_ROOT / "config" / "toolchain.toml")
        self.assertEqual(config.minimum_python_major, 3)
        self.assertEqual(config.minimum_python_minor, 11)
        self.assertEqual(config.development_dependencies, ("pytest>=8,<9",))
        self.assertEqual(config.required_godot_major, 4)
        self.assertEqual(config.godot_executable_candidates, ("godot4", "godot"))

    def test_toolchain_config_rejects_invalid_minimum_python(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "toolchain.toml"
            path.write_text(
                """\
[python]
minimum_version = "invalid"

[godot]
required_major = 4
executable_candidates = ["godot4", "godot"]
""",
                encoding="utf-8",
            )
            with self.assertRaises(ToolchainConfigError):
                load_toolchain_config(path)
