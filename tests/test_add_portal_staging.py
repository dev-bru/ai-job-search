"""Guard the writable-skill-folder fallback in /add-portal."""

import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent


class AddPortalStagingTests(unittest.TestCase):
    def test_workflow_documents_staging_and_install_commands(self):
        content = (REPO / ".claude/commands/add-portal.md").read_text(encoding="utf-8")
        self.assertIn("build/portal-staging/", content)
        self.assertIn("mv build/portal-staging/<name> .agents/skills/<name>", content)
        self.assertIn(
            "Move-Item build/portal-staging/<name> .agents/skills/<name> -ErrorAction Stop",
            content,
        )
        self.assertIn("Before scaffolding, try creating", content)
        self.assertIn("not writable", content)


if __name__ == "__main__":
    unittest.main()
