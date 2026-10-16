"""Guard shell-specific workflow commands without reading candidate profiles."""

import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
FENCED_PROFILES = {
    "01-candidate-profile.md",
    "02-behavioral-profile.md",
    "03-writing-style.md",
}
SHELL_ONLY = re.compile(r"\$\{[^}\n]*:\?|&&|\brm\s+-|\bmkdir\s+-p\b")
FENCE = re.compile(r"^\s*(`{3,}|~{3,})([^`~]*)$")


def has_powershell_alternative(lines, lineno, window=25):
    """True when a ```powershell block starts within `window` lines after this bash line."""
    return any(line.strip().startswith("```powershell") for line in lines[lineno:lineno + window])


class CrossPlatformStepsTests(unittest.TestCase):
    def test_workflow_steps_have_no_unlabelled_bash_constructs(self):
        paths = sorted((REPO / ".claude/commands").glob("*.md"))
        paths += sorted(
            path for path in (REPO / ".claude/skills").rglob("*.md")
            if path.name not in FENCED_PROFILES
        )
        problems = []
        for path in paths:
            fence = None
            bash_only = False
            lines = path.read_text(encoding="utf-8").splitlines()
            for lineno, line in enumerate(lines, 1):
                match = FENCE.match(line)
                if match:
                    if fence is None:
                        fence = match.group(1)
                        bash_only = match.group(2).strip() == "bash"
                    elif match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence):
                        fence = None
                        bash_only = False
                    continue
                if SHELL_ONLY.search(line) or (fence and line.rstrip().endswith("\\")):
                    # A bash block may keep bash-only syntax only when a PowerShell alternative follows it.
                    if bash_only and has_powershell_alternative(lines, lineno):
                        continue
                    problems.append(f"{path.relative_to(REPO)}:{lineno}: {line.strip()}")
        self.assertEqual(problems, [])

    def test_web_research_example_uses_scratchpad_paths_without_bash_expansion(self):
        path = REPO / ".claude/skills/job-application-assistant/09-web-research.md"
        content = path.read_text(encoding="utf-8")
        self.assertNotIn("${SCRATCHPAD:?", content)
        self.assertNotIn("&&", content)
        self.assertFalse(any(line.rstrip().endswith("\\") for line in content.splitlines()))
        self.assertIn("curl.exe -sSL", content)
        self.assertIn("'<scratchpad path>/page.html'", content)


if __name__ == "__main__":
    unittest.main()
