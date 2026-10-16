"""Guard the public fork's attribution and Codex onboarding."""

import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent


class ForkAttributionTests(unittest.TestCase):
    def test_readme_credits_upstream_and_onboards_codex(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        self.assertIn("https://github.com/MadsLorentzen/ai-job-search", readme)
        self.assertIn("## What this fork adds\n", readme)
        self.assertIn("### Quick start with Codex\n", readme)

    def test_license_keeps_original_and_fork_copyright(self):
        license_text = (REPO / "LICENSE").read_text(encoding="utf-8")
        self.assertIn("Copyright (c) 2026 Mads Lorentzen\n", license_text)
        self.assertIn(
            "Copyright (c) 2026 Dev Aaryan (Codex support and other changes in this fork)\n",
            license_text,
        )

    def test_contributing_starts_with_fork_note(self):
        contributing = (REPO / "CONTRIBUTING.md").read_text(encoding="utf-8")
        self.assertTrue(contributing.startswith("> This fork adds OpenAI Codex CLI support"))


if __name__ == "__main__":
    unittest.main()
