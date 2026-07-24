import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("decision_state.py")
ROOT = SCRIPT.parent.parent
TEMPLATE = ROOT / "assets" / "decision-tree.html"
SKILL = ROOT / "SKILL.md"


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

    def test_rejects_native_schema_synonyms(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            self.run_cli("init", str(state), "--title", "Test")
            self.run_cli(
                "add", str(state), "--id", "release", "--question", "Release?",
                "--type", "auto", "--option", "tag=Tag",
                "--assessment", self.assessment("tag"),
            )
            valid = json.loads(state.read_text())
            invalid_values = (
                ("status", "resolved", "Invalid type or status"),
                ("actor", "agent", "Invalid actor"),
                ("assessment-status", "current", "Invalid assessment status"),
            )
            for field, value, message in invalid_values:
                with self.subTest(field=field):
                    candidate = json.loads(json.dumps(valid))
                    if field == "assessment-status":
                        candidate["nodes"][0]["options"][0]["assessment"]["status"] = value
                    else:
                        candidate["nodes"][0][field] = value
                    state.write_text(json.dumps(candidate))
                    result = subprocess.run(
                        [sys.executable, str(SCRIPT), "render", str(state), str(Path(directory) / "tree.html")],
                        capture_output=True,
                        text=True,
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(message, result.stderr)

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
            self.assertIn("Thin workflow wrapper", fragment)
            self.assertIn("data-expand-all", fragment)
            self.assertIn("data-option-toggle", fragment)
            self.assertIn("Recommended", fragment)
            self.assertIn('input.disabled = excluded || invalidated', fragment)
            self.assertIn('const firstInvalidated = state.nodes.find', fragment)
            self.assertEqual(fragment.count('"status": "invalidated"'), 6)
            self.assertIn("Reassess path", fragment)
            self.assertIn("Reassess invalidated decision", fragment)

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
            self.assertIn("await window.openai.sendFollowUpMessage({ prompt, title })", fragment)
            self.assertIn('sendToCodex(prompt, "Apply decision", "Decision sent to Codex.")', fragment)
            self.assertIn('"Decision sent to Codex."', fragment)
            self.assertEqual(
                fragment.count('feedback.textContent = `Codex connection failed. Copy this prompt: ${prompt}`'),
                2,
            )
            self.assertNotIn("data-reassess=", fragment)

    def test_render_uses_the_canonical_template_contract(self) -> None:
        self.assertTrue(TEMPLATE.is_file())
        template = TEMPLATE.read_text()
        self.assertEqual(template.count("__LET_HIM_GRILL_STATE_JSON__"), 1)
        self.assertEqual(template.count("__LET_HIM_GRILL_STATE_PATH_JSON__"), 1)

        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            self.run_cli("init", str(state), "--title", "Canonical <template>")
            self.run_cli(
                "add", str(state), "--id", "surface", "--question", "Surface?",
                "--type", "auto", "--option", "native=Native Codex",
                "--assessment", self.assessment("native"),
            )

            rendered = Path(directory) / "tree.html"
            self.run_cli("render", str(state), str(rendered))
            fragment = rendered.read_text()

            self.assertIn('data-template="let-him-grill-v1"', fragment)
            self.assertIn('${autonomous} autonomous', fragment)
            self.assertIn('if (node.status === "confirmed") return "Confirmed"', fragment)
            self.assertIn(r"Canonical \u003ctemplate>", fragment)
            self.assertNotIn("Canonical <template>", fragment)
            self.assertIn(json.dumps(str(state.resolve())), fragment)
            self.assertNotIn("__LET_HIM_GRILL_", fragment)

        skill = SKILL.read_text()
        self.assertIn("assets/decision-tree.html", skill)
        self.assertIn("__LET_HIM_GRILL_STATE_JSON__", skill)
        self.assertIn("__LET_HIM_GRILL_STATE_PATH_JSON__", skill)
        self.assertIn("never invent synonyms", skill)
        self.assertNotIn("sendFollowUpMessage", SCRIPT.read_text())

    def test_skill_requires_a_confirmed_handoff_before_implementation(self) -> None:
        skill = SKILL.read_text()
        self.assertIn("summarize confirmed human decisions", skill)
        self.assertIn("Ask the user to confirm that summary", skill)
        self.assertIn("Do not implement the discussed plan", skill)
        self.assertIn("creating a duplicate", skill)

    def test_render_finds_template_in_an_installed_skill_layout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skill = Path(directory) / "let-him-grill"
            (skill / "scripts").mkdir(parents=True)
            (skill / "assets").mkdir()
            shutil.copy2(SCRIPT, skill / "scripts" / SCRIPT.name)
            shutil.copy2(TEMPLATE, skill / "assets" / TEMPLATE.name)
            output = Path(directory) / "tree.html"

            subprocess.run(
                [
                    sys.executable,
                    str(skill / "scripts" / SCRIPT.name),
                    "render",
                    str(ROOT / "examples" / "decisions.json"),
                    str(output),
                ],
                check=True,
            )

            self.assertIn('data-template="let-him-grill-v1"', output.read_text())


if __name__ == "__main__":
    unittest.main()
