"""Static contracts for native Godot exports in GitHub Actions."""

from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPOSITORY_ROOT / ".github" / "workflows" / "ci.yml"


class ExportCiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_native_matrix_covers_each_supported_export_host(self) -> None:
        self.assertIn(
            "os: [ubuntu-latest, windows-latest, macos-latest]",
            self.workflow,
        )
        self.assertIn('python-version: ["3.11", "3.14"]', self.workflow)
        self.assertIn("matrix.python-version == '3.11'", self.workflow)
        for system, target in (
            ('"Linux"', '"linux"'),
            ('"Windows"', '"windows"'),
            ('"Darwin"', '"macos"'),
        ):
            with self.subTest(system=system):
                self.assertIn(system, self.workflow)
                self.assertIn(target, self.workflow)

    def test_export_templates_are_official_checksum_verified_and_complete(self) -> None:
        self.assertIn(
            'templates_name = f"Godot_v{version}-stable_export_templates.tpz"',
            self.workflow,
        )
        self.assertIn("No SHA-512 entry found for {templates_name}", self.workflow)
        self.assertIn("templates_digest = hashlib.sha512()", self.workflow)
        self.assertIn("if templates_actual != templates_expected:", self.workflow)
        for template in (
            "linux_release.x86_64",
            "windows_release_x86_64.exe",
            "macos.zip",
        ):
            self.assertIn(f'"{template}"', self.workflow)

    def test_native_export_validates_exact_non_empty_output(self) -> None:
        self.assertIn(
            '[sys.executable, "tools/control.py", "export", target]',
            self.workflow,
        )
        self.assertIn("if not artifact.is_file():", self.workflow)
        self.assertIn("if artifact.stat().st_size == 0:", self.workflow)
        for artifact in (
            "artifacts/exports/linux/Forge2D-Template.x86_64",
            "artifacts/exports/windows/Forge2D-Template.exe",
            "artifacts/exports/macos/Forge2D-Template.zip",
        ):
            self.assertIn(artifact, self.workflow)

    def test_validated_exports_are_uploaded_with_bounded_retention(self) -> None:
        self.assertIn("uses: actions/upload-artifact@v7", self.workflow)
        self.assertIn("name: forge2d-template-${{ runner.os }}", self.workflow)
        self.assertIn("path: artifacts/exports/", self.workflow)
        self.assertIn("if-no-files-found: error", self.workflow)
        self.assertIn("retention-days: 7", self.workflow)


if __name__ == "__main__":
    unittest.main()
