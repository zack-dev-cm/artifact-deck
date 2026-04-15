from __future__ import annotations

import base64
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pptx import Presentation


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "skill" / "artifact-deck" / "scripts"
ONE_BY_ONE_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl9WJ4AAAAASUVORK5CYII="
)


class ArtifactDeckSmokeTest(unittest.TestCase):
    def test_end_to_end_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            (tmp_path / "changes.md").write_text(
                "- CI passed on the release branch.\n- Release notes were aligned.\n",
                encoding="utf-8",
            )
            (tmp_path / "risks.md").write_text(
                "- VirusTotal is still pending on one package.\n- Need sign-off before the launch post.\n",
                encoding="utf-8",
            )
            screenshot_path = tmp_path / "proof.png"
            screenshot_path.write_bytes(base64.b64decode(ONE_BY_ONE_PNG))

            manifest_path = tmp_path / "manifest.json"
            check_path = tmp_path / "check.json"
            build_path = tmp_path / "build.json"
            deck_path = tmp_path / "deck.pptx"
            summary_path = tmp_path / "summary.md"

            self.run_script(
                "init_artifact_deck_manifest.py",
                "--title",
                "Artifact Deck Demo",
                "--subtitle",
                "Launch review",
                "--section",
                f"What Changed={tmp_path / 'changes.md'}",
                "--section",
                f"Risks And Asks={tmp_path / 'risks.md'}",
                "--image",
                f"Browser Proof={screenshot_path}|Upload confirmation after publish",
                "--out",
                str(manifest_path),
            )
            self.run_script("check_artifact_deck_inputs.py", "--manifest", str(manifest_path), "--out", str(check_path))
            self.run_script(
                "build_artifact_deck.py",
                "--manifest",
                str(manifest_path),
                "--deck-out",
                str(deck_path),
                "--out",
                str(build_path),
            )
            self.run_script(
                "render_artifact_deck_summary.py",
                "--manifest",
                str(manifest_path),
                "--check",
                str(check_path),
                "--build",
                str(build_path),
                "--out",
                str(summary_path),
            )

            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            check = json.loads(check_path.read_text(encoding="utf-8"))
            build = json.loads(build_path.read_text(encoding="utf-8"))
            summary = summary_path.read_text(encoding="utf-8")
            deck = Presentation(str(deck_path))

            self.assertEqual(manifest["title"], "Artifact Deck Demo")
            self.assertEqual(check["status"], "ok")
            self.assertEqual(build["slide_count"], 4)
            self.assertEqual(build["image_slide_count"], 1)
            self.assertEqual(len(deck.slides), 4)
            self.assertIn("Artifact Deck Summary", summary)
            self.assertIn("What Changed", summary)
            self.assertIn("Browser Proof", summary)

    def test_missing_input_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            manifest_path = tmp_path / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "title": "Broken deck",
                        "subtitle": "",
                        "slides": [{"title": "Status", "bullets": ["One item"]}],
                        "images": [{"title": "Screenshot", "path": str(tmp_path / "missing.png"), "caption": ""}],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            check_path = tmp_path / "check.json"
            self.run_script("check_artifact_deck_inputs.py", "--manifest", str(manifest_path), "--out", str(check_path))
            check = json.loads(check_path.read_text(encoding="utf-8"))
            self.assertEqual(check["status"], "fix-required")
            self.assertEqual(check["error_count"], 1)

    def run_script(self, script_name: str, *args: str) -> None:
        script_path = SCRIPTS / script_name
        subprocess.run([sys.executable, str(script_path), *args], check=True, cwd=REPO_ROOT)


if __name__ == "__main__":
    unittest.main()
