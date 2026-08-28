"""Tests for the reviewable GitHub main-branch protection policy."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPOSITORY_ROOT / ".github" / "branch-protection-main.json"
REQUIRED_CHECKS = {
    "Linux / Arch Linux",
    "Linux / Debian 13",
    "macos-latest / Python 3.11",
    "macos-latest / Python 3.14",
    "ubuntu-latest / Python 3.11",
    "ubuntu-latest / Python 3.14",
    "windows-latest / Python 3.11",
    "windows-latest / Python 3.14",
}
GITHUB_ACTIONS_APP_ID = 15368


class BranchProtectionPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    def test_policy_requires_pull_requests_without_blocking_solo_maintenance(self) -> None:
        reviews = self.policy["required_pull_request_reviews"]

        self.assertEqual(reviews["required_approving_review_count"], 0)
        self.assertNotIn("bypass_pull_request_allowances", reviews)
        self.assertTrue(self.policy["enforce_admins"])

    def test_policy_requires_every_ci_job_from_github_actions(self) -> None:
        status_checks = self.policy["required_status_checks"]
        checks = status_checks["checks"]

        self.assertTrue(status_checks["strict"])
        self.assertNotIn("contexts", status_checks)
        self.assertEqual({check["context"] for check in checks}, REQUIRED_CHECKS)
        self.assertEqual(
            {check["app_id"] for check in checks},
            {GITHUB_ACTIONS_APP_ID},
        )

    def test_policy_blocks_history_and_review_bypasses(self) -> None:
        self.assertTrue(self.policy["required_linear_history"])
        self.assertTrue(self.policy["required_conversation_resolution"])
        self.assertFalse(self.policy["allow_force_pushes"])
        self.assertFalse(self.policy["allow_deletions"])
        self.assertFalse(self.policy["lock_branch"])


if __name__ == "__main__":
    unittest.main()
