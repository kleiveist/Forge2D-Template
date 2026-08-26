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

    def test_bootstrap_script_has_clean_test_mode_shutdown(self) -> None:
        script_text = (GODOT_ROOT / "src" / "bootstrap.gd").read_text(
            encoding="utf-8"
        )

        self.assertIn('TEST_MODE_ARGUMENT := "--test-mode"', script_text)
        self.assertIn("OS.get_cmdline_user_args()", script_text)
        self.assertIn("get_tree().quit(EXIT_SUCCESS)", script_text)


if __name__ == "__main__":
    unittest.main()
