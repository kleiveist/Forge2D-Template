"""Tests for machine-independent paths in repository source."""

from pathlib import Path
import re
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATHS = (
    REPOSITORY_ROOT / "config",
    REPOSITORY_ROOT / "game",
    REPOSITORY_ROOT / "tools" / "src",
)
SOURCE_SUFFIXES = {".gd", ".godot", ".py", ".toml", ".tscn"}
USER_PATH_PATTERNS = (
    re.compile("/" + r"home/[A-Za-z0-9._-]+/"),
    re.compile("/" + r"Users/[A-Za-z0-9._-]+/"),
    re.compile(r"[A-Za-z]:\\Users\\[A-Za-z0-9._-]+\\"),
)
RUNTIME_PATHS = (
    REPOSITORY_ROOT / "game" / "features",
    REPOSITORY_ROOT / "game" / "scenes",
    REPOSITORY_ROOT / "game" / "services",
    REPOSITORY_ROOT / "game" / "shared",
    REPOSITORY_ROOT / "game" / "src",
)
DOCUMENTATION_ENTRY_POINTS = (
    REPOSITORY_ROOT / "README.md",
    REPOSITORY_ROOT / "AGENTS.md",
)


class SourceHygieneTests(unittest.TestCase):
    def test_source_and_configuration_have_no_hard_coded_user_paths(self) -> None:
        violations: list[str] = []
        files = [REPOSITORY_ROOT / "pyproject.toml"]
        for source_path in SOURCE_PATHS:
            if source_path.exists():
                files.extend(
                    path
                    for path in source_path.rglob("*")
                    if path.is_file() and path.suffix in SOURCE_SUFFIXES
                )

        for path in files:
            contents = path.read_text(encoding="utf-8")
            if any(pattern.search(contents) for pattern in USER_PATH_PATTERNS):
                violations.append(path.relative_to(REPOSITORY_ROOT).as_posix())

        self.assertEqual(violations, [])

    def test_source_does_not_use_shell_true(self) -> None:
        targets = (
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "cli.py",
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "doctor.py",
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "install.py",
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "godot.py",
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "export.py",
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "release.py",
        )
        for target in targets:
            self.assertNotIn("shell=True", target.read_text(encoding="utf-8"))

    def test_source_does_not_use_break_system_packages(self) -> None:
        targets = (
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "install.py",
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "cli.py",
            REPOSITORY_ROOT / "tools" / "src" / "g2dtool" / "doctor.py",
        )
        for target in targets:
            self.assertNotIn("--break-system-packages", target.read_text(encoding="utf-8"))

    def test_runtime_has_no_direct_global_scene_changes(self) -> None:
        violations = self._gdscript_violations(
            re.compile(r"\bchange_scene_(?:to_file|to_packed)\s*\(")
        )
        self.assertEqual(violations, [])

    def test_runtime_has_no_physical_input_codes(self) -> None:
        patterns = (
            re.compile(r"\bInput\.is_(?:key|physical_key)_pressed\s*\("),
            re.compile(r"\bInput\.is_mouse_button_pressed\s*\("),
            re.compile(
                r"\bInputEvent(?:Key|JoypadButton|JoypadMotion|MouseButton|"
                r"MouseMotion|ScreenTouch|ScreenDrag|MagnifyGesture|PanGesture)\b"
            ),
            re.compile(
                r"\b(?:KEY|JOY_BUTTON|JOY_AXIS|MOUSE_BUTTON)_[A-Z0-9_]+\b"
            ),
        )
        violations: list[str] = []
        for pattern in patterns:
            violations.extend(self._gdscript_violations(pattern))
        self.assertEqual(sorted(set(violations)), [])

    def test_runtime_has_no_fixed_viewport_constants(self) -> None:
        violations = self._gdscript_violations(
            re.compile(r"(?<![0-9])(?:960|540)(?![0-9])")
        )
        self.assertEqual(violations, [])

    def test_runtime_has_no_forbidden_global_service_types(self) -> None:
        forbidden = re.compile(
            r"\b(?:class_name\s+)?(?:EventBus|ServiceLocator|GameState)\b"
        )
        violations = self._gdscript_violations(forbidden)
        self.assertEqual(violations, [])

    def test_features_do_not_import_other_features(self) -> None:
        features_root = REPOSITORY_ROOT / "game" / "features"
        violations: list[str] = []
        if features_root.exists():
            for path in features_root.rglob("*.gd"):
                feature_name = path.relative_to(features_root).parts[0]
                contents = path.read_text(encoding="utf-8")
                for imported_feature in re.findall(
                    r'res://features/([^/"\']+)/', contents
                ):
                    if imported_feature != feature_name:
                        violations.append(path.relative_to(REPOSITORY_ROOT).as_posix())
        self.assertEqual(violations, [])

    def test_documentation_relative_links_resolve(self) -> None:
        violations: list[str] = []
        docs_root = REPOSITORY_ROOT / "docs"
        link_pattern = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
        paths = sorted(docs_root.rglob("*.md")) + [
            path for path in DOCUMENTATION_ENTRY_POINTS if path.exists()
        ]
        for path in paths:
            for target in link_pattern.findall(path.read_text(encoding="utf-8")):
                target = target.strip().strip("<>").split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.exists():
                    relative_path = path.relative_to(REPOSITORY_ROOT).as_posix()
                    violations.append(f"{relative_path} -> {target}")
        self.assertEqual(violations, [])

    def test_documentation_architecture_separates_template_and_game_areas(self) -> None:
        required_paths = (
            "docs/index.md",
            "docs/README.md",
            "docs/forge2d-template/index.md",
            "docs/forge2d-template/forge2d-template.md",
            "docs/forge2d-template/tooling/installation.md",
            "docs/forge2d-template/tooling/branch-protection.md",
            "docs/forge2d-template/tooling/exporting.md",
            "docs/forge2d-template/tooling/gdscript-style-guide.md",
            "docs/forge2d-template/tooling/input.md",
            "docs/forge2d-template/tooling/python-style-guide.md",
            "docs/forge2d-template/tooling/releasing.md",
            "docs/forge2d-template/tooling/repository-metadata.md",
            "docs/forge2d-template/architecture/runtime-overview.md",
            "docs/forge2d-template/decisions/decisions.md",
            "docs/forge2d-template/plans/plans.md",
            "docs/forge2d-template/plans/M08_documentation_architecture.md",
            "docs/forge2d-template/plans/M09_coding_standards.md",
            "docs/forge2d-template/plans/M10_export_system.md",
            "docs/forge2d-template/plans/M11_input_baseline.md",
            "docs/forge2d-template/plans/M12_community_health.md",
            "docs/forge2d-template/plans/M13_repository_metadata.md",
            "docs/forge2d-template/releases/releases.md",
            "docs/forge2d-template/releases/v0.1.0.md",
            "docs/forge2d-template/reports/reports.md",
            "docs/developer/index.md",
            "docs/developer/developer.md",
            "docs/developer/features/_feature-template.md",
            "docs/developer/decisions/_adr-template.md",
            "docs/developer/plans/_execplan-template.md",
            "docs/player-guide/index.md",
            "docs/player-guide/player-guide.md",
            "docs/player-guide/_topic-template.md",
            "docs/in-game-help/index.md",
            "docs/in-game-help/in-game-help.md",
            "docs/in-game-help/_help-topic-template.md",
            "docs/case-studies/index.md",
            "docs/case-studies/case-studies.md",
            "docs/case-studies/_case-study-template.md",
            "docs/release-manual/index.md",
            "docs/release-manual/release-manual.md",
            "docs/release-manual/_release-template.md",
        )
        missing = [
            path for path in required_paths if not (REPOSITORY_ROOT / path).is_file()
        ]
        self.assertEqual(missing, [])

        root_docs = REPOSITORY_ROOT / "docs"
        unexpected_root_pages = sorted(
            path.name
            for path in root_docs.glob("*.md")
            if path.name not in {"README.md", "index.md"}
        )
        self.assertEqual(unexpected_root_pages, [])

        developer_index = (REPOSITORY_ROOT / "docs" / "developer" / "index.md")
        self.assertIn(
            "../forge2d-template/architecture/runtime-overview.md",
            developer_index.read_text(encoding="utf-8"),
        )

        root_readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("- 📚 [Documentation hub](docs/index.md)", root_readme)
        self.assertNotIn("## 📁 Forge2D Template", root_readme)

    def test_mermaid_fences_are_balanced(self) -> None:
        violations: list[str] = []
        docs_root = REPOSITORY_ROOT / "docs"
        for path in docs_root.rglob("*.md"):
            in_mermaid = False
            for line in path.read_text(encoding="utf-8").splitlines():
                marker = line.strip()
                if marker == "```mermaid":
                    if in_mermaid:
                        violations.append(path.relative_to(REPOSITORY_ROOT).as_posix())
                    in_mermaid = True
                elif marker == "```" and in_mermaid:
                    in_mermaid = False
            if in_mermaid:
                violations.append(path.relative_to(REPOSITORY_ROOT).as_posix())
        self.assertEqual(sorted(set(violations)), [])

    @staticmethod
    def _gdscript_violations(pattern: re.Pattern[str]) -> list[str]:
        violations: list[str] = []
        for runtime_path in RUNTIME_PATHS:
            if not runtime_path.exists():
                continue
            for path in runtime_path.rglob("*.gd"):
                if pattern.search(path.read_text(encoding="utf-8")):
                    violations.append(path.relative_to(REPOSITORY_ROOT).as_posix())
        return violations


if __name__ == "__main__":
    unittest.main()
