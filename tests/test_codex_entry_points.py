"""Guards for Codex's thin entry points to all twelve workflows."""

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
    "outcome": ".claude/commands/outcome.md",
    "expand": ".claude/commands/expand.md",
    "html-report": ".claude/commands/html-report.md",
    "reset": ".claude/commands/reset.md",
    "add-template": ".claude/commands/add-template.md",
    "add-portal": ".claude/commands/add-portal.md",
}


class CodexEntryPointTests(unittest.TestCase):
    def test_exactly_one_entry_point_per_workflow(self):
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

    def test_readme_lists_codex_invocations(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        for flow in CANONICAL:
            with self.subTest(flow=flow):
                self.assertIn(f"| `/{flow}` | `$job-{flow}` |", readme)
        self.assertIn("`/skills`", readme)
        self.assertIn("`codex exec`", readme)


class RuntimeNeutralCommandTests(unittest.TestCase):
    def test_every_agent_tool_step_has_inline_fallback(self):
        for flow in ("apply", "rank"):
            command = (REPO / ".claude" / "commands" / f"{flow}.md").read_text(encoding="utf-8")
            steps = re.split(r"(?=^## Step \d+:)", command, flags=re.MULTILINE)
            agent_steps = [step for step in steps if "**Agent tool**" in step]
            self.assertTrue(agent_steps, f"{flow} has no Agent-tool step")
            for step in agent_steps:
                with self.subTest(flow=flow, step=step.splitlines()[0]):
                    after_tool = step.split("**Agent tool**", 1)[1]
                    note = re.search(
                        r"(?m)^\*\*Other runtimes without the Agent tool:\*\* (.+)$",
                        after_tool,
                    )
                    self.assertIsNotNone(note, "Agent-tool step needs its own fallback note")
                    fallback = note.group(1)
                    self.assertIn("inline", fallback)
                    self.assertIn("one item at a time", fallback)
                    if flow == "apply":
                        self.assertIn("separate pass", fallback)
                        self.assertIn("re-read the inputs fresh", fallback)
                        self.assertIn("do not reuse the drafting reasoning", fallback)

    def test_connector_sync_commands_are_claude_only(self):
        for flow, connector in (("gmail-sync", "Gmail"), ("notion-sync", "Notion")):
            with self.subTest(flow=flow):
                command = (REPO / ".claude" / "commands" / f"{flow}.md").read_text(encoding="utf-8")
                opening = "\n".join(command.splitlines()[:5])
                self.assertIn("**Claude Code only:**", opening)
                self.assertIn(f"Claude's {connector} connector", opening)
                self.assertIn("other runtimes must stop and say", opening)


if __name__ == "__main__":
    unittest.main()
