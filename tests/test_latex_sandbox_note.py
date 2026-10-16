"""Guards for the sandbox-local LaTeX setup note."""

import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class LatexSandboxNoteTests(unittest.TestCase):
    def test_setup_documents_workspace_local_tex_writes(self):
        setup = (REPO / "SETUP.md").read_text(encoding="utf-8")
        self.assertIn("### Compiling inside the Codex sandbox", setup)
        self.assertIn("only for runs inside a sandbox that blocks writes outside the repository", setup)
        self.assertIn("never use it in a normal shell", setup)
        validation = "Test-Path (Join-Path $install 'miktex/bin') -PathType Container"
        self.assertIn(validation, setup)
        self.assertIn('throw "MiKTeX install path', setup)
        self.assertLess(
            setup.index(validation), setup.index("$env:MIKTEX_USERINSTALL = $install")
        )
        self.assertIn("a missing package cannot trigger an install outside the repository", setup)
        self.assertIn(
            '"[Core]`nLastUserMaintenance=1`n[MPM]`nAutoInstall=0"', setup
        )
        for variable in ("MIKTEX_USERINSTALL", "MIKTEX_USERCONFIG", "MIKTEX_USERDATA", "LastUserMaintenance", "TEXMFVAR"):
            with self.subTest(variable=variable):
                self.assertIn(variable, setup)

    def test_compile_workflows_link_to_setup_note(self):
        target = "SETUP.md#compiling-inside-the-codex-sandbox"
        for command in ("apply.md", "add-template.md"):
            with self.subTest(command=command):
                text = (REPO / ".claude" / "commands" / command).read_text(encoding="utf-8")
                self.assertIn(target, text)

    def test_custom_latex_compile_discards_stale_pdfs(self):
        command = (REPO / ".claude/commands/add-template.md").read_text(encoding="utf-8")
        stale = command.index("Remove-Item 'build/<file>.pdf'")
        compile_ = command.index("lualatex -interaction=nonstopmode -output-directory=build", stale)
        check = command.index("if (-not $? -or $LASTEXITCODE -ne 0)", compile_)
        move = command.index("Move-Item 'build/<file>.pdf'", check)
        self.assertLess(stale, compile_)
        self.assertLess(compile_, check)
        self.assertLess(check, move)


if __name__ == "__main__":
    unittest.main()
