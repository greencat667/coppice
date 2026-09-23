"""Tests for scripts/doctor.py. Run from the repo root:  python3 -m unittest discover tests"""
import contextlib
import datetime as dt
import io
import os
import shutil
import sys
import tempfile
import time
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import doctor  # noqa: E402

TODAY = dt.date(2026, 9, 23)


def age(path: Path, days: int):
    t = time.mktime((TODAY - dt.timedelta(days=days)).timetuple())
    os.utime(path, (t, t))


class Workspace:
    """A fresh copy of the starter workspace in a temp folder."""

    def __enter__(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.ws = self.tmp / "ws"
        shutil.copytree(REPO / "workspace", self.ws)
        return self.ws

    def __exit__(self, *exc):
        shutil.rmtree(self.tmp)


def checks(rep, severity=None):
    return {f.check for f in rep.findings if severity is None or f.severity == severity}


class FreshWorkspace(unittest.TestCase):
    def test_starter_workspace_is_clean(self):
        with Workspace() as ws:
            rep = doctor.run(ws, TODAY)
            self.assertEqual(rep.count("error"), 0, [f.message for f in rep.findings])
            self.assertEqual(rep.count("warn"), 0, [f.message for f in rep.findings])

    def test_startup_budget_measured(self):
        with Workspace() as ws:
            rep = doctor.run(ws, TODAY)
            self.assertLess(rep.stats["startup_tokens"]["main"], 4000)


class ExampleWorkspace(unittest.TestCase):
    def test_example_is_clean(self):
        rep = doctor.run(REPO / "examples" / "workspace", dt.date(2026, 9, 28))
        self.assertEqual([f.message for f in rep.findings if f.severity in ("error", "warn")], [])
        self.assertEqual(set(rep.stats["startup_tokens"]), {"work", "personal"})


class BrokenWorkspace(unittest.TestCase):
    def test_missing_required_file(self):
        with Workspace() as ws:
            (ws / "soul.md").unlink()
            self.assertIn("required-files", checks(doctor.run(ws, TODAY), "error"))

    def test_root_clutter(self):
        with Workspace() as ws:
            (ws / "notes-final-v2.md").write_text("stray")
            (ws / ".hidden").write_text("dotfiles are ignored")
            rep = doctor.run(ws, TODAY)
            msgs = [f.message for f in rep.findings if f.check == "root-clutter"]
            self.assertEqual(len(msgs), 1)
            self.assertIn("notes-final-v2.md", msgs[0])

    def test_tasks_budget_and_narrative(self):
        with Workspace() as ws:
            t = ws / "TASKS.md"
            t.write_text(t.read_text() + "\n- ✅ (2026-09-01) — did the thing, then another, because reasons\n"
                         + ("- filler line to push the file over budget\n" * 500))
            rep = doctor.run(ws, TODAY)
            self.assertIn("tasks-budget", checks(rep, "error"))
            self.assertIn("tasks-narrative", checks(rep, "warn"))

    def test_startup_budget_exceeded(self):
        with Workspace() as ws:
            (ws / "memory" / "recent.md").write_text("# Recent\n\n## 2026-09-22 — big\n\n" + "word " * 40000)
            self.assertIn("startup-budget", checks(doctor.run(ws, TODAY), "error"))

    def test_old_recent_entries_warn_then_fix(self):
        with Workspace() as ws:
            r = ws / "memory" / "recent.md"
            r.write_text("# Recent sessions\n\n## 2026-09-20 — new\n\n- keep me\n\n## 2026-07-02 — old\n\n- move me\n\n"
                         "## 2026-06-15 — older\n\n- move me too\n")
            self.assertIn("recent-window", checks(doctor.run(ws, TODAY), "warn"))
            rep = doctor.run(ws, TODAY, fix=True)
            self.assertNotIn("recent-window", checks(rep))
            self.assertEqual(len(rep.fixes), 1)
            text = r.read_text()
            self.assertIn("keep me", text)
            self.assertNotIn("move me", text)
            self.assertIn("move me", (ws / "memory" / "archive" / "2026-07.md").read_text())
            self.assertIn("move me too", (ws / "memory" / "archive" / "2026-06.md").read_text())

    def test_projects_index_and_logs(self):
        with Workspace() as ws:
            (ws / "projects" / "003 - Orphan").mkdir()
            good = ws / "projects" / "004 - Listed"
            good.mkdir()
            (good / "log.md").write_text("# log\n")
            idx = ws / "memory" / "projects.md"
            idx.write_text(idx.read_text().replace("**Next project number: 001**", "**Next project number: 002**")
                           + "\n| 004 | Listed | Project | Active | `projects/004 - Listed/` | goal | next |\n"
                           + "| 007 | Ghost | Project | Active | `projects/007 - Ghost/` | goal | next |\n")
            rep = doctor.run(ws, TODAY)
            self.assertIn("project-log", checks(rep, "error"))       # 003 has no log
            self.assertIn("next-number", checks(rep, "error"))       # 002 but 007 is listed
            msgs = " ".join(f.message for f in rep.findings if f.check == "projects-index")
            self.assertIn("003 - Orphan", msgs)                      # folder not in index
            self.assertIn("007", msgs)                               # index row with no folder

    def test_projects_fix(self):
        with Workspace() as ws:
            (ws / "projects" / "005 - No Log").mkdir()
            idx = ws / "memory" / "projects.md"
            idx.write_text(idx.read_text() + "\n| 005 | No Log | Project | Active | `projects/005 - No Log/` | g | n |\n")
            rep = doctor.run(ws, TODAY, fix=True)
            self.assertTrue((ws / "projects" / "005 - No Log" / "log.md").exists())
            self.assertIn("Next project number: 006", idx.read_text())
            self.assertEqual(rep.count("error"), 0, [f.message for f in rep.findings])

    def test_stale_active_project_log(self):
        with Workspace() as ws:
            d = ws / "projects" / "002 - Quiet"
            d.mkdir()
            (d / "log.md").write_text("# log\n")
            age(d / "log.md", 45)
            idx = ws / "memory" / "projects.md"
            idx.write_text(idx.read_text().replace("Next project number: 001", "Next project number: 003")
                           .replace("| 001 | [Name] |", "| 002 | Quiet |").replace("`projects/001 - Name/`", "`projects/002 - Quiet/`"))
            self.assertIn("project-log", checks(doctor.run(ws, TODAY), "info"))

    def test_broken_link(self):
        with Workspace() as ws:
            (ws / "context" / "notes.md").write_text("See [the plan](../projects/009%20-%20Gone/plan.md) and [ok](README.md).\n")
            rep = doctor.run(ws, TODAY)
            msgs = [f.message for f in rep.findings if f.check == "links"]
            self.assertEqual(len(msgs), 1)
            self.assertIn("009", msgs[0])

    def test_secrets_found_and_masked(self):
        with Workspace() as ws:
            fake_github = "gh" + "p_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"   # built at runtime; not a real token
            fake_assign = "api_key: " + "9f8e7d6c5b4a" + "39281706afbecd12"
            (ws / "context" / "board.md").write_text(f"token here {fake_github}\n{fake_assign}\n")
            rep = doctor.run(ws, TODAY)
            hits = [f for f in rep.findings if f.check == "secrets"]
            self.assertEqual(len(hits), 2)
            for f in hits:
                self.assertNotIn(fake_github, f.message)
                self.assertNotIn("39281706afbecd12", f.message)

    def test_placeholders_are_not_secrets(self):
        with Workspace() as ws:
            (ws / "context" / "setup-notes.md").write_text("api_key: YOUR_API_KEY_GOES_HERE_123\npassword = [your password here 12345]\n")
            self.assertNotIn("secrets", checks(doctor.run(ws, TODAY)))

    def test_heartbeat(self):
        with Workspace() as ws:
            hb = ws / "memory" / "heartbeat.md"
            hb.write_text(hb.read_text() + "| 2026-09-01 | archive-trim | ran | ok |\n| 2026-09-22 | doctor | failed | crashed |\n")
            rep = doctor.run(ws, TODAY)
            msgs = " ".join(f.message for f in rep.findings if f.check == "heartbeat")
            self.assertIn("archive-trim", msgs)      # weekly, last ran 22 days ago
            self.assertIn("failed", msgs)            # doctor's last run failed

    def test_working_inbox_and_stray_reports(self):
        with Workspace() as ws:
            f = ws / "working" / "draft.md"
            f.write_text("old draft")
            age(f, 12)
            (ws / "memory" / "skill-gaps-2026-09-20.md").write_text("report")
            (ws / "memory" / "weekly-scan-2026-09-13.md").write_text("report")
            rep = doctor.run(ws, TODAY)
            self.assertIn("working-inbox", checks(rep, "warn"))
            self.assertIn("reports", checks(rep, "warn"))


class RealWorldNoise(unittest.TestCase):
    """False positives found by running the doctor against a real, long-lived workspace."""

    def test_code_projects_are_not_workspace_notes(self):
        with Workspace() as ws:
            code = ws / "projects" / "001 - App" / "working" / "app"
            code.mkdir(parents=True)
            (ws / "projects" / "001 - App" / "log.md").write_text("# log\n")
            (code / "package.json").write_text("{}")
            (code / "README.md").write_text("See [docs](docs/missing.md).\n")
            (code / "fixture.pem").write_text("x")
            (code / "test_keys.md").write_text("-----BEGIN RSA PRIVATE KEY-----\n")
            idx = ws / "memory" / "projects.md"
            idx.write_text(idx.read_text().replace("Next project number: 001", "Next project number: 002")
                           .replace("`projects/001 - Name/`", "`projects/001 - App/`").replace("| 001 | [Name] |", "| 001 | App |"))
            rep = doctor.run(ws, TODAY)
            self.assertNotIn("links", checks(rep))
            self.assertNotIn("secrets", checks(rep, "error"))
            self.assertIn("secrets", checks(rep, "info"))          # summarised, not dropped

    def test_captured_sources_links_skipped(self):
        with Workspace() as ws:
            for sub in ("inputs", "raw"):
                d = ws / "context" / sub
                d.mkdir()
                (d / "saved-page.md").write_text("[a](/wiki/Somewhere) [b](images/x.png)\n")
            self.assertNotIn("links", checks(doctor.run(ws, TODAY)))

    def test_wiki_style_links_without_extension(self):
        with Workspace() as ws:
            (ws / "context" / "a.md").write_text("[b](b)\n")
            (ws / "context" / "b.md").write_text("hello\n")
            self.assertNotIn("links", checks(doctor.run(ws, TODAY)))

    def test_several_project_roots_numbered_separately(self):
        with Workspace() as ws:
            setup = ws / "setup.md"
            setup.write_text(setup.read_text().replace("project_roots:                # folders holding numbered project folders; list several to number them separately\n  - projects",
                                                       "project_roots:\n  - work-projects\n  - personal-projects"))
            for root, n in (("work-projects", "003 - Report"), ("personal-projects", "010 - Novel")):
                d = ws / root / n
                d.mkdir(parents=True)
                (d / "log.md").write_text("# log\n")
            idx = ws / "memory" / "projects.md"
            idx.write_text("# Projects\n\nNext project number (work-projects): 004\nNext project number (personal-projects): 005\n\n## Active\n\n"
                           "| # | Project | Folder |\n|---|---|---|\n| 003 | Report | `work-projects/003 - Report/` |\n"
                           "| 010 | Novel | `personal-projects/010 - Novel/` |\n")
            rep = doctor.run(ws, TODAY)
            msgs = [f.message for f in rep.findings if f.check == "next-number"]
            self.assertEqual(len(msgs), 1, msgs)                    # only personal-projects is wrong
            self.assertIn("personal-projects", msgs[0])
            self.assertNotIn("projects-index", checks(rep))
            rep = doctor.run(ws, TODAY, fix=True)
            self.assertIn("Next project number (personal-projects): 011", idx.read_text())
            self.assertIn("Next project number (work-projects): 004", idx.read_text())

    def test_link_targets_with_brackets(self):
        with Workspace() as ws:
            d = ws / "context" / "Album (Deluxe Edition)"
            d.mkdir()
            (d / "notes.md").write_text("x")
            (ws / "context" / "a.md").write_text("[deluxe](Album%20(Deluxe%20Edition)/notes.md)\n")
            self.assertNotIn("links", checks(doctor.run(ws, TODAY)))

    def test_ignore_globs(self):
        with Workspace() as ws:
            saved = ws / "context" / "saved-pages"
            saved.mkdir()
            (saved / "page.md").write_text("[x](/somewhere/else)\n")
            self.assertIn("links", checks(doctor.run(ws, TODAY)))
            setup = ws / "setup.md"
            setup.write_text(setup.read_text().replace('  # - "*/saved-pages/*"', '  - "*/saved-pages/*"'))
            self.assertNotIn("links", checks(doctor.run(ws, TODAY)))

    def test_many_stray_files_grouped(self):
        with Workspace() as ws:
            for i in range(30):
                (ws / f"stray-{i}.md").write_text("x")
            msgs = [f for f in doctor.run(ws, TODAY).findings if f.check == "root-clutter"]
            self.assertEqual(len(msgs), 1)
            self.assertIn("30 file(s)", msgs[0].message)


class CommandLine(unittest.TestCase):
    def test_exit_codes_report_and_heartbeat(self):
        with Workspace() as ws:
            with contextlib.redirect_stdout(io.StringIO()):
                code = doctor.main(["-w", str(ws), "--today", "2026-09-23", "--report", "reports/doctor.md", "--heartbeat"])
            self.assertEqual(code, 0)
            self.assertTrue((ws / "reports" / "doctor.md").exists())
            self.assertIn("| 2026-09-23 | doctor | ran |", (ws / "memory" / "heartbeat.md").read_text())
            (ws / "setup.md").unlink()
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(doctor.main(["-w", str(ws), "--today", "2026-09-23"]), 1)


if __name__ == "__main__":
    unittest.main()
