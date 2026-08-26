"""Tests for project configuration loading and validation."""

from pathlib import Path
from tempfile import TemporaryDirectory
import textwrap
import unittest

from _source_path import add_source_root

add_source_root()

from g2dtool.config import ProjectConfigError, load_project_config


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class ProjectConfigTests(unittest.TestCase):
    def test_loads_and_validates_baseline_configuration(self) -> None:
        config = load_project_config(REPOSITORY_ROOT / "config" / "project.toml")

        self.assertEqual(config.schema_version, 1)
        self.assertEqual(config.template_id, "forge2d")
        self.assertEqual(config.display_name, "Forge2D")
        self.assertEqual(config.repository_language, "en")
        self.assertEqual(config.default_cli_name, "g2d")
        self.assertEqual(config.godot_project_path.as_posix(), "game/project.godot")
        self.assertEqual(config.license_status, "undecided")

    def test_rejects_unsupported_schema(self) -> None:
        self.assert_invalid_config("schema_version = 2", "schema_version")

    def test_rejects_absolute_godot_path(self) -> None:
        replacement = 'godot_project_path = "/opt/forge2d/project.godot"'
        self.assert_invalid_config(replacement, "repository-relative")

    def assert_invalid_config(self, replacement: str, message: str) -> None:
        baseline = textwrap.dedent(
            """\
            schema_version = 1

            [project]
            template_id = "forge2d"
            display_name = "Forge2D"
            repository_language = "en"
            default_cli_name = "g2d"
            godot_project_path = "game/project.godot"
            license_status = "undecided"
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


if __name__ == "__main__":
    unittest.main()
