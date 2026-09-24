"""Tests for scripts/trim.py. Run from the repo root:  python3 -m unittest discover tests"""
import contextlib
import io
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_doctor import TODAY, Workspace, age  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import doctor  # noqa: E402
import trim  # noqa: E402


class Trim(unittest.TestCase):
    def test_fresh_workspace_nothing_to_trim(self):
        with Workspace() as ws:
            self.assertEqual(trim.run(ws, TODAY), [])

    def test_everything_aged_out_is_moved_or_deleted(self):
        with Workspace() as ws:
            (ws / "memory" / "recent.md").write_text("# Recent\n\n## 2026-09-21 — keep\n\n- a\n\n## 2026-08-01 — old\n\n- b\n")
            (ws / "memory" / "learning-log.md").write_text(
                "# Learning log\n\n## Active\n\n### 2026-09-01 — live one [trying]\n\nkeep\n\n"
                "### 2026-06-01 — settled [graduated → START-HERE 2026-09-10]\n\ngone\n\n"
                "### 2026-05-01 — nope [discarded]\n\ngone too\n")
            hb = ws / "memory" / "heartbeat.md"
            hb.write_text(hb.read_text() + "| 2026-06-01 | doctor | ran | old |\n| 2026-09-21 | doctor | ran | new |\n")
            old_report = ws / "reports" / "doctor-2026-06-01.md"
            old_report.write_text("old")
            age(old_report, 100)
            new_report = ws / "reports" / "doctor-2026-09-21.md"
            new_report.write_text("new")

            dry = trim.run(ws, TODAY, dry=True)
            self.assertEqual(len(dry), 4)
            self.assertTrue(old_report.exists())             # dry run changes nothing

            self.assertEqual(len(trim.run(ws, TODAY)), 4)
            self.assertNotIn("old", (ws / "memory" / "recent.md").read_text().split("keep")[1])
            self.assertIn("## 2026-08-01", (ws / "memory" / "archive" / "2026-08.md").read_text())
            ll = (ws / "memory" / "learning-log.md").read_text()
            self.assertIn("live one", ll)
            self.assertNotIn("settled", ll)
            arch = (ws / "memory" / "archive" / "learning-log-archive.md").read_text()
            self.assertIn("settled", arch)
            self.assertIn("nope", arch)
            self.assertNotIn("2026-06-01 | doctor", hb.read_text())
            self.assertIn("2026-09-21 | doctor", hb.read_text())
            self.assertFalse(old_report.exists())
            self.assertTrue(new_report.exists())

            self.assertEqual(trim.run(ws, TODAY), [])         # idempotent
            self.assertNotIn("recent-window", {f.check for f in doctor.run(ws, TODAY).findings})

    def test_section_headings_stay_in_the_learning_log(self):
        with Workspace() as ws:
            ll = ws / "memory" / "learning-log.md"
            ll.write_text("# Learning log\n\n## Active\n\n### 2026-09-01 — live [trying]\n\nkeep\n\n"
                          "### 2026-06-01 — last active one [graduated → setup.md]\n\ngone\n\n"
                          "## Discarded\n\n*Kept as a record.*\n\n## Strategic insights\n\n### 2026-03-03 — an insight\n\nstays\n")
            trim.run(ws, TODAY)
            text = ll.read_text()
            for s in ("## Discarded", "*Kept as a record.*", "## Strategic insights", "an insight", "live"):
                self.assertIn(s, text)
            self.assertNotIn("last active one", text)
            self.assertNotIn("## Discarded", (ws / "memory" / "archive" / "learning-log-archive.md").read_text())

    def test_cli_heartbeat(self):
        with Workspace() as ws:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(trim.main(["-w", str(ws), "--today", "2026-09-23", "--heartbeat"]), 0)
            self.assertIn("| 2026-09-23 | archive-trim | skipped |", (ws / "memory" / "heartbeat.md").read_text())


if __name__ == "__main__":
    unittest.main()
