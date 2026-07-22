import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("decision_state.py")


class DecisionStateTest(unittest.TestCase):
    def run_cli(self, *args: str) -> None:
        subprocess.run([sys.executable, str(SCRIPT), *args], check=True)

    def test_change_invalidates_only_transitive_descendants(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            self.run_cli("init", str(state), "--title", "Test")
            self.run_cli("add", str(state), "--id", "audience", "--question", "Audience?", "--type", "review", "--option", "dev=Developers", "--option", "team=Teams", "--choice", "dev")
            self.run_cli("add", str(state), "--id", "storage", "--question", "Storage?", "--type", "review", "--option", "json=JSON", "--option", "sqlite=SQLite", "--choice", "json", "--depends-on", "audience")
            self.run_cli("add", str(state), "--id", "architecture", "--question", "Architecture?", "--type", "human", "--option", "skill=Skill::Thin workflow wrapper", "--option", "plugin=Plugin::Installable bundle", "--depends-on", "storage")
            self.run_cli("add", str(state), "--id", "unrelated", "--question", "Unrelated?", "--type", "auto", "--option", "yes=Yes", "--choice", "yes")
            self.run_cli("choose", str(state), "audience", "team")

            nodes = {node["id"]: node for node in json.loads(state.read_text())["nodes"]}
            self.assertEqual(nodes["audience"]["status"], "confirmed")
            self.assertEqual(nodes["storage"]["status"], "invalidated")
            self.assertEqual(nodes["architecture"]["status"], "invalidated")
            self.assertEqual(nodes["unrelated"]["choice"], "yes")

            rendered = Path(directory) / "tree.html"
            self.run_cli("render", str(state), str(rendered))
            fragment = rendered.read_text()
            self.assertIn("sendFollowUpMessage", fragment)
            self.assertIn("Architecture?", fragment)
            self.assertIn("<details", fragment)
            self.assertIn("Thin workflow wrapper", fragment)
            self.assertIn("data-expand-all", fragment)
            self.assertIn("data-option-toggle", fragment)


if __name__ == "__main__":
    unittest.main()
