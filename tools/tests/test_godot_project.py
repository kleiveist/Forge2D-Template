"""Static consistency tests for the Godot project boundary."""

from pathlib import Path
import re
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GODOT_ROOT = REPOSITORY_ROOT / "game"


class GodotProjectTests(unittest.TestCase):
    def test_project_has_existing_main_scene(self) -> None:
        project_text = (GODOT_ROOT / "project.godot").read_text(encoding="utf-8")
        match = re.search(r'run/main_scene="res://([^\"]+)"', project_text)

        self.assertIsNotNone(match)
        assert match is not None
        self.assertTrue((GODOT_ROOT / match.group(1)).is_file())

    def test_bootstrap_scene_references_existing_script(self) -> None:
        scene_text = (GODOT_ROOT / "scenes" / "bootstrap.tscn").read_text(
            encoding="utf-8"
        )
        match = re.search(r'path="res://([^\"]+\.gd)"', scene_text)

        self.assertIsNotNone(match)
        assert match is not None
        self.assertTrue((GODOT_ROOT / match.group(1)).is_file())
        self.assertNotIn("res://addons/", scene_text)

    def test_bootstrap_scene_uses_the_production_bootstrap_script(self) -> None:
        script_text = (GODOT_ROOT / "src" / "bootstrap.gd").read_text(
            encoding="utf-8"
        )

        self.assertIn("class_name Forge2DTemplateBootstrap", script_text)
        self.assertNotIn("get_tree().quit", script_text)

    def test_bootstrap_has_a_dedicated_integration_test_runner(self) -> None:
        runner = GODOT_ROOT / "tests" / "bootstrap_integration_test.gd"
        self.assertTrue(runner.is_file())
        runner_text = runner.read_text(encoding="utf-8")
        self.assertIn('ProjectSettings.get_setting("application/run/main_scene"', runner_text)
        self.assertIn("bootstrap.get_script()", runner_text)
        self.assertIn("bootstrap.get_node_or_null", runner_text)
        self.assertNotIn("Forge2DTemplateBootstrap", runner_text)
        self.assertIn("quit(1)", runner_text)


if __name__ == "__main__":
    unittest.main()
