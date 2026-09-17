import importlib.util
from pathlib import Path
import sys
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "delegate.py"
SPEC = importlib.util.spec_from_file_location("delegate", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class DelegateCommandTest(unittest.TestCase):
    def args(self, mode="read-only", **overrides):
        values = {
            "mode": mode,
            "cwd": "/repo",
            "model": None,
            "add_dirs": [],
            "timeout": 7,
            "out_file": None,
            "aider_files": [],
            "aider_reads": [],
        }
        values.update(overrides)
        return values

    def build(self, agent, mode="read-only", **overrides):
        return MODULE.build_cmd(agent, "PROMPT", **self.args(mode, **overrides))[0]

    def test_all_includes_aider(self):
        self.assertEqual(("codex", "claude", "gemini", "antigravity", "aider"), MODULE.AGENTS)

    def test_gemini_read_only_uses_plan_and_sandbox(self):
        command = self.build("gemini")
        self.assertIn("gemini", command)
        self.assertIn("-p", command)
        self.assertIn("--approval-mode", command)
        self.assertIn("plan", command)
        self.assertIn("--sandbox", command)
        self.assertNotIn("--yolo", command)

    def test_gemini_edit_uses_auto_edit_without_yolo(self):
        command = self.build("gemini", mode="edit", add_dirs=["/extra/context"])
        self.assertIn("--approval-mode", command)
        self.assertIn("auto_edit", command)
        self.assertIn("--include-directories", command)
        self.assertIn("/extra/context", command)
        self.assertNotIn("--yolo", command)

    def test_aider_read_only_has_no_write_side_effects(self):
        command = self.build("aider")
        self.assertIn("--dry-run", command)
        self.assertIn("--no-git", command)
        self.assertIn("--no-gitignore", command)
        self.assertIn("--no-auto-commits", command)
        self.assertIn("--input-history-file", command)
        self.assertIn("/dev/null", command)

    def test_aider_edit_requires_explicit_files(self):
        with self.assertRaisesRegex(ValueError, "--aider-file"):
            self.build("aider", mode="edit")
        command = self.build("aider", mode="edit", aider_files=["src/app.py"])
        self.assertIn("--file", command)
        self.assertIn("src/app.py", command)
        self.assertNotIn("--dry-run", command)

    def test_explicit_model_opts_out_of_default_zai_route(self):
        command = self.build("aider", model="openai/gpt-4o")
        self.assertIn("openai/gpt-4o", command)
        self.assertNotIn("--openai-api-base", command)

    def test_selected_skill_is_read_only_context(self):
        command = self.build("aider", aider_reads=["/repo/SKILL.md"])
        self.assertIn("--read", command)
        self.assertIn("/repo/SKILL.md", command)


if __name__ == "__main__":
    unittest.main()
