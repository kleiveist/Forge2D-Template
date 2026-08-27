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

    def test_bootstrap_composes_the_application_root(self) -> None:
        scene_text = (GODOT_ROOT / "scenes" / "bootstrap.tscn").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            'path="res://scenes/app/application_root.tscn"', scene_text
        )
        self.assertIn("application_root_scene = ExtResource", scene_text)
        self.assertNotIn('[node name="Background"', scene_text)

    def test_application_root_has_the_minimal_composition_nodes(self) -> None:
        scene = GODOT_ROOT / "scenes" / "app" / "application_root.tscn"
        self.assertTrue(scene.is_file())
        scene_text = scene.read_text(encoding="utf-8")

        self.assertIn('[node name="ApplicationRoot" type="Node"]', scene_text)
        self.assertEqual(scene_text.count('[node name="RouteHost"'), 1)
        self.assertEqual(scene_text.count('[node name="PersistentUI"'), 1)
        self.assertEqual(scene_text.count('[node name="TransitionLayer"'), 1)
        self.assertIn('initial_route_id = &"template_home"', scene_text)
        self.assertIn('path="res://scenes/app/template_home.tscn"', scene_text)

    def test_scene_router_is_the_only_autoload(self) -> None:
        project_text = (GODOT_ROOT / "project.godot").read_text(encoding="utf-8")
        section = re.search(
            r"(?ms)^\[autoload\]\s*$\n(?P<body>.*?)(?=^\[[^]]+\]\s*$|\Z)",
            project_text,
        )

        self.assertIsNotNone(section)
        assert section is not None
        entries = re.findall(
            r'(?m)^([A-Za-z_][A-Za-z0-9_]*)="\*(res://[^"]+)"$',
            section.group("body"),
        )
        self.assertEqual(
            entries,
            [("SceneRouter", "res://services/scene_router.gd")],
        )
        self.assertTrue((GODOT_ROOT / "services" / "scene_router.gd").is_file())

    def test_route_resources_and_neutral_route_exist(self) -> None:
        required = (
            GODOT_ROOT / "shared" / "resources" / "route_entry.gd",
            GODOT_ROOT / "shared" / "resources" / "route_table.gd",
            GODOT_ROOT / "scenes" / "app" / "template_home.tscn",
        )
        for path in required:
            with self.subTest(path=path):
                self.assertTrue(path.is_file())

    def test_bootstrap_scene_uses_the_production_bootstrap_script(self) -> None:
        script_text = (GODOT_ROOT / "src" / "bootstrap.gd").read_text(
            encoding="utf-8"
        )

        self.assertIn("class_name Forge2DTemplateBootstrap", script_text)
        self.assertIn("signal composition_failed(error: Error, message: String)", script_text)
        self.assertIn("if application_root_scene == null:", script_text)
        self.assertIn("push_error", script_text)
        self.assertIn("composition_failed.emit(error, message)", script_text)
        self.assertNotIn("get_tree().quit", script_text)

    def test_bootstrap_has_a_dedicated_integration_test_runner(self) -> None:
        runner = GODOT_ROOT / "tests" / "bootstrap_integration_test.gd"
        self.assertTrue(runner.is_file())
        runner_text = runner.read_text(encoding="utf-8")
        self.assertIn('ProjectSettings.get_setting("application/run/main_scene"', runner_text)
        self.assertIn("bootstrap.get_script()", runner_text)
        self.assertIn("bootstrap.get_node_or_null", runner_text)
        self.assertNotIn("Forge2DTemplateBootstrap", runner_text)
        self.assertIn("res://tests/runtime/scene_router_test.gd", runner_text)
        self.assertIn("res://tests/runtime/application_root_test.gd", runner_text)
        self.assertIn("ApplicationRoot/RouteHost/TemplateHome", runner_text)
        self.assertIn("Forge2D bootstrap integration test: passed", runner_text)
        self.assertIn("quit(1)", runner_text)


if __name__ == "__main__":
    unittest.main()
