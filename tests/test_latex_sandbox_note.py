"""Guards for the sandbox-local LaTeX setup note."""

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class LatexSandboxNoteTests(unittest.TestCase):
    def test_setup_documents_workspace_local_tex_writes(self):
        setup = (REPO / "SETUP.md").read_text(encoding="utf-8")
        self.assertIn("### Compiling inside the Codex sandbox", setup)
        for variable in ("MIKTEX_USERINSTALL", "MIKTEX_USERCONFIG", "MIKTEX_USERDATA", "LastUserMaintenance", "TEXMFVAR"):
            with self.subTest(variable=variable):
                self.assertIn(variable, setup)

    def test_compile_workflows_link_to_setup_note(self):
        target = "SETUP.md#compiling-inside-the-codex-sandbox"
        for command in ("apply.md", "add-template.md"):
            with self.subTest(command=command):
                text = (REPO / ".claude" / "commands" / command).read_text(encoding="utf-8")
                self.assertIn(target, text)


if __name__ == "__main__":
    unittest.main()
