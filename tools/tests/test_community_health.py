"""Tests for repository community policies and GitHub contribution forms."""

from __future__ import annotations

from pathlib import Path
import re
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
GITHUB_ROOT = REPOSITORY_ROOT / ".github"
ISSUE_TEMPLATE_ROOT = GITHUB_ROOT / "ISSUE_TEMPLATE"
SECURITY_REPORT_URL = (
    "https://github.com/kleiveist/Forge2D-Template/security/advisories/new"
)
FORM_EXPECTATIONS = {
    "bug_report.yml": {
        "area",
        "version",
        "environment",
        "reproduction",
        "expected",
        "actual",
        "logs",
        "additional",
        "readiness",
    },
    "feature_request.yml": {
        "area",
        "problem",
        "proposal",
        "alternatives",
        "acceptance",
        "risk",
        "readiness",
    },
}
REQUIRED_FIELDS = {
    "bug_report.yml": {
        "area",
        "version",
        "environment",
        "reproduction",
        "expected",
        "actual",
    },
    "feature_request.yml": {
        "area",
        "problem",
        "proposal",
        "alternatives",
        "acceptance",
    },
}
ALLOWED_FORM_TYPES = {"checkboxes", "dropdown", "input", "markdown", "textarea"}


class CommunityHealthTests(unittest.TestCase):
    def test_required_community_files_exist(self) -> None:
        required_paths = (
            REPOSITORY_ROOT / "CONTRIBUTING.md",
            REPOSITORY_ROOT / "SECURITY.md",
            GITHUB_ROOT / "PULL_REQUEST_TEMPLATE.md",
            ISSUE_TEMPLATE_ROOT / "bug_report.yml",
            ISSUE_TEMPLATE_ROOT / "feature_request.yml",
            ISSUE_TEMPLATE_ROOT / "config.yml",
        )

        self.assertEqual([path for path in required_paths if not path.is_file()], [])

    def test_issue_forms_follow_the_reviewed_schema_subset(self) -> None:
        for filename, expected_ids in FORM_EXPECTATIONS.items():
            with self.subTest(form=filename):
                contents = self._read_issue_template(filename)
                self._assert_clean_yaml_layout(contents)
                self.assertTrue(self._top_level_value(contents, "name"))
                self.assertTrue(self._top_level_value(contents, "description"))
                self.assertTrue(self._top_level_value(contents, "title"))
                self.assertEqual(contents.count("\nbody:\n"), 1)

                field_types = re.findall(r"^  - type: ([a-z]+)$", contents, re.MULTILINE)
                field_ids = re.findall(
                    r"^    id: ([A-Za-z0-9_-]+)$",
                    contents,
                    re.MULTILINE,
                )
                self.assertGreater(len(field_types), len(field_ids))
                self.assertEqual(set(field_types) - ALLOWED_FORM_TYPES, set())
                self.assertEqual(set(field_ids), expected_ids)
                self.assertEqual(len(field_ids), len(set(field_ids)))

                for field_id in REQUIRED_FIELDS[filename]:
                    section = self._field_section(contents, field_id)
                    self.assertIn("\n    validations:\n      required: true\n", section)

                readiness = self._field_section(contents, "readiness")
                self.assertEqual(readiness.count("        - label:"), 3)
                self.assertEqual(readiness.count("          required: true"), 3)

    def test_bug_form_collects_reproducible_safe_reports(self) -> None:
        contents = self._read_issue_template("bug_report.yml")

        self.assertIn("Version or commit", contents)
        self.assertIn("Environment", contents)
        self.assertIn("Reproduction steps", contents)
        self.assertIn("Expected behavior", contents)
        self.assertIn("Actual behavior", contents)
        self.assertIn("render: shell", contents)
        self.assertIn(SECURITY_REPORT_URL, contents)
        self.assertIn("contains no vulnerability details or secrets", contents)

    def test_feature_form_collects_scope_tradeoffs_and_completion(self) -> None:
        contents = self._read_issue_template("feature_request.yml")

        self.assertIn("Problem or use case", contents)
        self.assertIn("Proposed capability", contents)
        self.assertIn("Alternatives considered", contents)
        self.assertIn("Acceptance criteria", contents)
        self.assertIn("Risks and dependencies", contents)
        self.assertIn("not specific to one downstream game", contents)

    def test_issue_chooser_deliberately_disables_blank_reports(self) -> None:
        config = self._read_issue_template("config.yml")
        contributing = self._read_repository_file("CONTRIBUTING.md")

        self.assertIn("blank_issues_enabled: false", config)
        self.assertIn("contact_links:", config)
        self.assertIn(f"url: {SECURITY_REPORT_URL}", config)
        self.assertIn("Blank issues are deliberately disabled", contributing)
        self.assertIn("maintainer-only", contributing)

    def test_contributing_policy_matches_repository_workflow(self) -> None:
        contents = self._read_repository_file("CONTRIBUTING.md")
        required_text = (
            "python tools/control.py install --dry-run",
            "python tools/control.py install --yes",
            "repository-local `.venv`",
            "docs/python-style-guide.md",
            "docs/gdscript-style-guide.md",
            "python tools/control.py style",
            "python tools/control.py check",
            "all eight Linux, Windows, and macOS CI jobs",
            "docs/branch-protection.md",
            "Never\n   push a contribution directly to protected `main`",
            "emoji followed by a concise,\n   imperative English summary",
        )

        for text in required_text:
            with self.subTest(text=text):
                self.assertIn(text, contents)

    def test_security_policy_uses_private_reporting_and_response_targets(self) -> None:
        contents = self._read_repository_file("SECURITY.md")
        normalized = " ".join(contents.split())

        self.assertIn("Protected `main` | Yes", contents)
        self.assertIn("Latest published `0.1.x` release | Yes", contents)
        self.assertIn(SECURITY_REPORT_URL, contents)
        self.assertIn("Do not disclose a suspected vulnerability in a public issue", contents)
        self.assertIn("within three business days", normalized)
        self.assertIn("within seven business days", normalized)
        self.assertIn("at least every seven days", normalized)
        self.assertIn("response targets, not a guarantee", normalized)
        self.assertIn("Maintainers of Forks", contents)
        self.assertNotIn("mailto:", contents)

    def test_pull_request_template_collects_validation_risk_and_hygiene(self) -> None:
        contents = (GITHUB_ROOT / "PULL_REQUEST_TEMPLATE.md").read_text(
            encoding="utf-8"
        )
        required_text = (
            "## Summary",
            "## Related issue",
            "Closes #",
            "## Validation",
            "python tools/control.py style",
            "python tools/control.py check",
            "## Documentation",
            "## Risk and recovery",
            "No secret, token, credential, personal data, or machine path",
            "Every new dependency has a reviewed purpose, risk, license, and alternative",
        )

        for text in required_text:
            with self.subTest(text=text):
                self.assertIn(text, contents)

    def test_entry_points_link_contribution_and_security_policies(self) -> None:
        entry_points = (
            REPOSITORY_ROOT / "README.md",
            REPOSITORY_ROOT / "docs" / "README.md",
            REPOSITORY_ROOT / "docs" / "index.md",
        )
        for path in entry_points:
            with self.subTest(path=path.relative_to(REPOSITORY_ROOT)):
                contents = path.read_text(encoding="utf-8")
                self.assertIn("CONTRIBUTING.md", contents)
                self.assertIn("SECURITY.md", contents)

    def test_community_markdown_relative_links_resolve(self) -> None:
        paths = (
            REPOSITORY_ROOT / "README.md",
            REPOSITORY_ROOT / "CONTRIBUTING.md",
            REPOSITORY_ROOT / "SECURITY.md",
            GITHUB_ROOT / "PULL_REQUEST_TEMPLATE.md",
        )
        link_pattern = re.compile(r"(?<!!)\[[^]]+\]\(([^)]+)\)")
        violations: list[str] = []

        for path in paths:
            for target in link_pattern.findall(path.read_text(encoding="utf-8")):
                normalized = target.strip().strip("<>").split("#", 1)[0]
                if not normalized or "://" in normalized or normalized.startswith("mailto:"):
                    continue
                resolved = (path.parent / normalized).resolve()
                if not resolved.exists():
                    relative_path = path.relative_to(REPOSITORY_ROOT).as_posix()
                    violations.append(f"{relative_path} -> {normalized}")

        self.assertEqual(violations, [])

    @staticmethod
    def _assert_clean_yaml_layout(contents: str) -> None:
        for line in contents.splitlines():
            if "\t" in line or line != line.rstrip():
                raise AssertionError(f"Invalid YAML whitespace: {line!r}")
            indentation = len(line) - len(line.lstrip(" "))
            if indentation % 2:
                raise AssertionError(f"YAML indentation is not two-space aligned: {line!r}")

    @staticmethod
    def _top_level_value(contents: str, key: str) -> str:
        match = re.search(rf"^{re.escape(key)}:\s+(.+)$", contents, re.MULTILINE)
        if match is None:
            raise AssertionError(f"Missing top-level issue-form key: {key}")
        return match.group(1).strip().strip('"')

    @staticmethod
    def _field_section(contents: str, field_id: str) -> str:
        marker = f"    id: {field_id}\n"
        start = contents.find(marker)
        if start < 0:
            raise AssertionError(f"Missing issue-form field: {field_id}")
        end = contents.find("\n  - type:", start)
        if end < 0:
            end = len(contents)
        return contents[start:end] + "\n"

    @staticmethod
    def _read_issue_template(filename: str) -> str:
        return (ISSUE_TEMPLATE_ROOT / filename).read_text(encoding="utf-8")

    @staticmethod
    def _read_repository_file(filename: str) -> str:
        return (REPOSITORY_ROOT / filename).read_text(encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
