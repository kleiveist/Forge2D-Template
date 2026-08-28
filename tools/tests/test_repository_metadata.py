"""Tests for the reviewed GitHub repository metadata contract."""

from __future__ import annotations

import json
from pathlib import Path
import re
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
METADATA_PATH = REPOSITORY_ROOT / ".github" / "repository-metadata.json"
GUIDE_PATH = REPOSITORY_ROOT / "docs" / "repository-metadata.md"
EXPECTED_DESCRIPTION = (
    "Minimal Godot 4 2D game template with repository-local Python tooling "
    "for setup, checks, exports, and releases."
)
EXPECTED_TOPICS = (
    "2d-game",
    "game-development",
    "game-template",
    "gdscript",
    "godot",
    "godot-4",
    "python",
)
TOPIC_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class RepositoryMetadataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    def test_contract_has_only_reviewed_fields(self) -> None:
        self.assertEqual(
            set(self.metadata),
            {"schema_version", "description", "homepage", "topics"},
        )
        self.assertEqual(self.metadata["schema_version"], 1)

    def test_description_is_concise_and_matches_readme_identity(self) -> None:
        description = self.metadata["description"]
        readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")
        readme_phrase = EXPECTED_DESCRIPTION[0].lower() + EXPECTED_DESCRIPTION[1:]

        self.assertEqual(description, EXPECTED_DESCRIPTION)
        self.assertLessEqual(len(description), 160)
        self.assertNotIn("\n", description)
        self.assertIn(readme_phrase, " ".join(readme.split()))

    def test_topics_are_focused_unique_and_github_compatible(self) -> None:
        topics = self.metadata["topics"]

        self.assertEqual(tuple(topics), EXPECTED_TOPICS)
        self.assertEqual(topics, sorted(topics))
        self.assertEqual(len(topics), len(set(topics)))
        self.assertLessEqual(len(topics), 20)
        for topic in topics:
            with self.subTest(topic=topic):
                self.assertRegex(topic, TOPIC_PATTERN)
                self.assertLessEqual(len(topic), 50)

    def test_homepage_is_intentionally_omitted(self) -> None:
        guide = GUIDE_PATH.read_text(encoding="utf-8")

        self.assertIsNone(self.metadata["homepage"])
        self.assertIn("Homepage | Not configured", guide)
        self.assertIn("There is no maintained canonical website", guide)
        self.assertIn("expected homepage value is `null`", guide)

    def test_guide_documents_api_audit_and_template_customization(self) -> None:
        guide = GUIDE_PATH.read_text(encoding="utf-8")
        required_text = (
            ".github/repository-metadata.json",
            EXPECTED_DESCRIPTION,
            "gh api --method PATCH",
            "gh api --method PUT",
            "--jq '{description, homepage, topics, is_template}'",
            "Replace canonical owner/repository URLs",
            "security/advisories/new",
            "branch protection and private vulnerability reporting",
        )
        for topic in EXPECTED_TOPICS:
            required_text += (f"`{topic}`",)

        for text in required_text:
            with self.subTest(text=text):
                self.assertIn(text, guide)

    def test_documentation_entry_points_link_the_metadata_guide(self) -> None:
        entry_points = (
            REPOSITORY_ROOT / "README.md",
            REPOSITORY_ROOT / "docs" / "README.md",
            REPOSITORY_ROOT / "docs" / "index.md",
        )
        for path in entry_points:
            with self.subTest(path=path.relative_to(REPOSITORY_ROOT)):
                self.assertIn(
                    "repository-metadata.md",
                    path.read_text(encoding="utf-8"),
                )


if __name__ == "__main__":
    unittest.main()
