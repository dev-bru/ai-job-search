"""Guards for Codex's thin entry points to the six core flows."""

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / ".agents" / "skills"
CANONICAL = {
    "setup": ".claude/commands/setup.md",
    "scrape": ".claude/skills/job-scraper/SKILL.md",
    "rank": ".claude/commands/rank.md",
    "apply": ".claude/commands/apply.md",
    "upskill": ".claude/skills/upskill/SKILL.md",
    "interview": ".claude/commands/interview.md",
}


class CodexEntryPointTests(unittest.TestCase):
    def test_exactly_one_entry_point_per_core_flow(self):
        names = {path.parent.name for path in SKILLS.glob("job-*/SKILL.md")}
        self.assertEqual(names, {f"job-{flow}" for flow in CANONICAL})

    def test_skills_point_to_canonical_specs_without_copying_steps(self):
        for flow, canonical in CANONICAL.items():
            with self.subTest(flow=flow):
                skill = SKILLS / f"job-{flow}" / "SKILL.md"
                text = skill.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"))
                frontmatter, separator, body = text[4:].partition("\n---\n")
                self.assertTrue(separator, "frontmatter must be closed")
                self.assertRegex(frontmatter, rf"(?m)^name: job-{flow}$")
                self.assertRegex(frontmatter, r"(?m)^description: >\n  \S")
                # /scrape treats every enabled .agents skill as a portal CLI.
                self.assertIn("enabled: false", frontmatter)
                self.assertNotIn("allowed-tools:", frontmatter)
                links = re.findall(r"\]\(([^)]+)\)", body)
                self.assertEqual(len(links), 1)
                target = (skill.parent / links[0]).resolve()
                self.assertEqual(target, (REPO / canonical).resolve())
                self.assertTrue(target.is_file())
                self.assertIn("Codex entry point", body)
                self.assertLess(len(body.splitlines()), 40)
                self.assertNotRegex(body, r"(?m)^\s*\d+\.\s")

    def test_agents_lists_every_entry_point(self):
        agents = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        for flow in CANONICAL:
            with self.subTest(flow=flow):
                self.assertIn(f".agents/skills/job-{flow}/SKILL.md", agents)


if __name__ == "__main__":
    unittest.main()
