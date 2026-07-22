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

    def assessment(
        self,
        option: str,
        triage: str = "recommended",
        risk: str = "low",
        reversible: bool = True,
    ) -> str:
        value = {
            "triage": triage,
            "reason": "Best fit for the stated constraints.",
            "confidence": 0.9,
            "reversible": reversible,
            "effort": "low",
            "risk": risk,
            "impact": "Keeps downstream work small.",
            "preferredWhen": "Prefer when simplicity matters most.",
        }
        return f"{option}={json.dumps(value)}"

    def test_auto_selects_only_a_safe_recommended_option(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            self.run_cli("init", str(state), "--title", "Test")
            self.run_cli(
                "add", str(state), "--id", "storage", "--question", "Storage?",
                "--type", "auto", "--option", "json=JSON", "--option", "cloud=Cloud",
                "--assessment", self.assessment("json"),
                "--assessment", self.assessment("cloud", "situational", "medium", False),
            )
            self.run_cli(
                "add", str(state), "--id", "provider", "--question", "Provider?",
                "--type", "human", "--option", "one=One", "--option", "two=Two",
                "--assessment", self.assessment("one"),
                "--assessment", self.assessment("two", "solid-alternative"),
            )
            self.run_cli(
                "add", str(state), "--id", "region", "--question", "Region?",
                "--type", "blocked", "--option", "eu=EU", "--option", "us=US",
                "--assessment", self.assessment("eu", "situational"),
                "--assessment", self.assessment("us", "situational"),
            )

            nodes = {node["id"]: node for node in json.loads(state.read_text())["nodes"]}
            self.assertEqual(nodes["storage"]["choice"], "json")
            self.assertEqual(nodes["storage"]["actor"], "ai")
            self.assertIsNone(nodes["provider"]["choice"])
            self.assertEqual(nodes["provider"]["status"], "pending")
            self.assertIsNone(nodes["region"]["choice"])

            rendered = Path(directory) / "tree.html"
            self.run_cli("render", str(state), str(rendered))
            self.assertIn("Blocked", rendered.read_text())

            ambiguous = subprocess.run(
                [
                    sys.executable, str(SCRIPT), "add", str(state),
                    "--id", "ambiguous", "--question", "Ambiguous?", "--type", "auto",
                    "--option", "one=One", "--option", "two=Two",
                    "--assessment", self.assessment("one"),
                    "--assessment", self.assessment("two"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(ambiguous.returncode, 0)
            self.assertIn("exactly one", ambiguous.stderr)

    def test_excluded_option_cannot_be_selected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            self.run_cli("init", str(state), "--title", "Test")
            self.run_cli(
                "add", str(state), "--id", "unsafe", "--question", "Unsafe?", "--type", "review",
                "--option", "safe=Safe", "--option", "unsafe=Unsafe",
                "--assessment", self.assessment("safe"),
                "--assessment", self.assessment("unsafe", "excluded", "high", False),
                "--choice", "safe",
            )
            result = subprocess.run(
                [
                    sys.executable, str(SCRIPT), "choose", str(state), "unsafe", "unsafe",
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("excluded", result.stderr)

    def test_change_invalidates_only_transitive_descendants(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            self.run_cli("init", str(state), "--title", "Test")
            self.run_cli("add", str(state), "--id", "audience", "--question", "Audience?", "--type", "review", "--option", "dev=Developers", "--option", "team=Teams", "--assessment", self.assessment("dev"), "--assessment", self.assessment("team", "solid-alternative"), "--choice", "dev")
            self.run_cli("add", str(state), "--id", "storage", "--question", "Storage?", "--type", "review", "--option", "json=JSON", "--option", "sqlite=SQLite", "--assessment", self.assessment("json"), "--assessment", self.assessment("sqlite", "solid-alternative"), "--choice", "json", "--depends-on", "audience")
            self.run_cli("add", str(state), "--id", "architecture", "--question", "Architecture?", "--type", "human", "--option", "skill=Skill::Thin workflow wrapper", "--option", "plugin=Plugin::Installable bundle", "--assessment", self.assessment("skill"), "--assessment", self.assessment("plugin", "solid-alternative"), "--depends-on", "storage")
            self.run_cli("add", str(state), "--id", "unrelated", "--question", "Unrelated?", "--type", "auto", "--option", "yes=Yes", "--assessment", self.assessment("yes"))
            self.run_cli("choose", str(state), "audience", "team")

            nodes = {node["id"]: node for node in json.loads(state.read_text())["nodes"]}
            self.assertEqual(nodes["audience"]["status"], "confirmed")
            self.assertEqual(nodes["storage"]["status"], "invalidated")
            self.assertEqual(nodes["architecture"]["status"], "invalidated")
            self.assertEqual(nodes["unrelated"]["choice"], "yes")
            self.assertEqual(nodes["storage"]["options"][0]["assessment"]["status"], "invalidated")

            stale = subprocess.run(
                [sys.executable, str(SCRIPT), "choose", str(state), "storage", "sqlite"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn("reassess", stale.stderr)

            rendered = Path(directory) / "tree.html"
            self.run_cli("render", str(state), str(rendered))
            fragment = rendered.read_text()
            self.assertIn("sendFollowUpMessage", fragment)
            self.assertIn("Architecture?", fragment)
            self.assertIn("<details", fragment)
            self.assertIn("Thin workflow wrapper", fragment)
            self.assertIn("data-expand-all", fragment)
            self.assertIn("data-option-toggle", fragment)
            self.assertIn("Recommended", fragment)

    def test_rendered_action_uses_codex_follow_up_bridge_with_safe_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            self.run_cli("init", str(state), "--title", "Test")
            self.run_cli(
                "add", str(state), "--id", "release", "--question", "Release?",
                "--type", "review", "--option", "tag=Tag only", "--option", "page=Release page",
                "--assessment", self.assessment("tag"),
                "--assessment", self.assessment("page", "solid-alternative"),
                "--choice", "tag",
            )

            rendered = Path(directory) / "tree.html"
            self.run_cli("render", str(state), str(rendered))
            fragment = rendered.read_text()

            self.assertIn(f"const statePath = {json.dumps(str(state.resolve()))}", fragment)
            self.assertIn('await window.openai.sendFollowUpMessage({ prompt, title: "Apply decision" })', fragment)
            self.assertIn('feedback.textContent = "Decision sent to Codex."', fragment)
            self.assertEqual(
                fragment.count('feedback.textContent = `Codex connection failed. Copy this prompt: ${prompt}`'),
                2,
            )


if __name__ == "__main__":
    unittest.main()
