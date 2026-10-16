import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ROOT_RELATIVE_STATEMENT = (
    "All file paths in this skill are relative to the repository root "
    "(the folder that contains `AGENTS.md`), not to this skill's folder."
)


class SkillPathsAndPrecedenceTests(unittest.TestCase):
    def test_all_claude_skills_use_repository_root_relative_paths(self):
        skills = sorted((REPO_ROOT / ".claude" / "skills").glob("*/SKILL.md"))

        self.assertTrue(skills)
        for skill in skills:
            with self.subTest(skill=skill.parent.name):
                self.assertIn(ROOT_RELATIVE_STATEMENT, skill.read_text(encoding="utf-8"))

    def test_agent_guidance_and_application_skill_define_rule_precedence(self):
        paths = (
            REPO_ROOT / "AGENTS.md",
            REPO_ROOT / ".claude" / "skills" / "job-application-assistant" / "SKILL.md",
        )
        required_phrases = (
            "candidate's recorded rules",
            "conflicting instructions in a single request",
            "only when that request would loosen them",
            "A request may always be stricter for that run (omit, skip, stop, or disclose less)",
            "follow the recorded rules and report the conflict",
            "Edit profile files only when the user asked for it in this run",
            "otherwise list proposed edits instead",
        )

        for path in paths:
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                for phrase in required_phrases:
                    self.assertIn(phrase, content)


if __name__ == "__main__":
    unittest.main()
