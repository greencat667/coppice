#!/usr/bin/env python3
"""coppice trim: the weekly cut-back. Run by the archive-trim scheduled task.

Moves what has aged out of the files read every session, so they stay small:

  - recent-session entries older than budgets.recent_days → memory/archive/YYYY-MM.md
  - learning-log entries marked [graduated …] or [discarded …] → memory/archive/learning-log-archive.md
  - heartbeat lines older than 60 days → deleted
  - generated reports in reports/ older than budgets.reports_days → deleted

    python3 trim.py                  # trim the current folder
    python3 trim.py --dry-run        # say what would happen, change nothing
    python3 trim.py --heartbeat      # also record the run in memory/heartbeat.md

Only generated files (reports, heartbeat lines) are ever deleted. Everything else is moved.
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import doctor  # noqa: E402  (same folder; shares the parsers)

HEARTBEAT_KEEP_DAYS = 60
LL_ENTRY = re.compile(r"^### .*$", re.M)
LL_SECTION = re.compile(r"^#{1,3} ", re.M)
LL_DONE = re.compile(r"\[(graduated|discarded)[^\]]*\]", re.I)


def trim_recent(ws, budgets, contexts, today, dry, actions):
    cutoff = today - dt.timedelta(days=budgets["recent_days"])
    for path in sorted({c["recent"] for c in contexts}):
        p = ws / path
        if not p.exists():
            continue
        pre, entries = doctor.split_dated_entries(doctor.read(p))
        old = [(d, e) for d, e in entries if d < cutoff]
        if not old:
            continue
        months = sorted({f"{d:%Y-%m}" for d, _ in old})
        actions.append(f"Moved {len(old)} entr{'y' if len(old) == 1 else 'ies'} from `{path}` to `memory/archive/` ({', '.join(months)}).")
        if dry:
            continue
        archive = ws / "memory" / "archive"
        archive.mkdir(parents=True, exist_ok=True)
        for month in months:
            ap = archive / f"{month}.md"
            existing = doctor.read(ap) if ap.exists() else f"# Archive — {month}\n\n"
            items = [e.rstrip() + "\n" for d, e in old if f"{d:%Y-%m}" == month]
            ap.write_text(existing.rstrip() + "\n\n" + "\n".join(items), encoding="utf-8")
        p.write_text(pre + "".join(e for d, e in entries if d >= cutoff), encoding="utf-8")


def trim_learning_log(ws, dry, actions):
    p = ws / "memory" / "learning-log.md"
    if not p.exists():
        return
    text = doctor.read(p)
    if not LL_ENTRY.search(text):
        return
    # An entry runs to the next heading of any level up to ###, so a section
    # heading after the last entry (## Discarded, say) stays in the log.
    cuts = [m.start() for m in LL_SECTION.finditer(text)]
    starts = [0] + cuts if not cuts or cuts[0] != 0 else cuts
    keep, done = [], []
    for i, s in enumerate(starts):
        chunk = text[s: starts[i + 1] if i + 1 < len(starts) else len(text)]
        head = LL_ENTRY.match(chunk)
        (done if head and LL_DONE.search(head.group(0)) else keep).append(chunk)
    if not done:
        return
    actions.append(f"Moved {len(done)} graduated or discarded learning-log entr{'y' if len(done) == 1 else 'ies'} to "
                   "`memory/archive/learning-log-archive.md`.")
    if dry:
        return
    ap = ws / "memory" / "archive" / "learning-log-archive.md"
    ap.parent.mkdir(parents=True, exist_ok=True)
    existing = doctor.read(ap) if ap.exists() else "# Learning log — archive\n\nGraduated and discarded entries, with their verdicts.\n\n"
    ap.write_text(existing.rstrip() + "\n\n" + "".join(c.rstrip() + "\n\n" for c in done), encoding="utf-8")
    p.write_text("".join(keep).rstrip() + "\n", encoding="utf-8")


def trim_heartbeat(ws, today, dry, actions):
    p = ws / "memory" / "heartbeat.md"
    if not p.exists():
        return
    cutoff = today - dt.timedelta(days=HEARTBEAT_KEEP_DAYS)
    lines, dropped = [], 0
    for line in doctor.read(p).splitlines():
        m = doctor.HEARTBEAT_ROW.match(line.strip())
        if m and dt.date.fromisoformat(m.group(1)) < cutoff:
            dropped += 1
            continue
        lines.append(line)
    if dropped:
        actions.append(f"Deleted {dropped} heartbeat line(s) older than {HEARTBEAT_KEEP_DAYS} days.")
        if not dry:
            p.write_text("\n".join(lines) + "\n", encoding="utf-8")


def trim_reports(ws, budgets, today, dry, actions):
    rdir = ws / "reports"
    if not rdir.is_dir():
        return
    old = [p for p in rdir.rglob("*") if p.is_file() and not p.name.startswith(".")
           and (today - dt.date.fromtimestamp(p.stat().st_mtime)).days > budgets["reports_days"]]
    if old:
        actions.append(f"Deleted {len(old)} report(s) in `reports/` older than {budgets['reports_days']} days.")
        if not dry:
            for p in old:
                p.unlink()


def run(ws: Path, today: dt.date, dry: bool = False) -> list[str]:
    setup = doctor.read(ws / "setup.md")
    budgets, _, _ = doctor.parse_budgets(setup)
    contexts = doctor.parse_contexts(setup)
    actions: list[str] = []
    trim_recent(ws, budgets, contexts, today, dry, actions)
    trim_learning_log(ws, dry, actions)
    trim_heartbeat(ws, today, dry, actions)
    trim_reports(ws, budgets, today, dry, actions)
    return actions


def main(argv=None):
    ap = argparse.ArgumentParser(description="Weekly cut-back for a Coppice workspace.")
    ap.add_argument("--workspace", "-w", default=".")
    ap.add_argument("--dry-run", action="store_true", help="report what would change; change nothing")
    ap.add_argument("--heartbeat", action="store_true", help="append a line to memory/heartbeat.md")
    ap.add_argument("--today", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    ws = Path(args.workspace).expanduser().resolve()
    if not (ws / "setup.md").exists():
        print(f"No setup.md in {ws} — is this a Coppice workspace?", file=sys.stderr)
        return 2
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    actions = run(ws, today, dry=args.dry_run)
    prefix = "Would have: " if args.dry_run else ""
    print("\n".join(f"- {prefix}{a}" for a in actions) if actions else "- Nothing to trim.")
    if args.heartbeat and not args.dry_run:
        hb = ws / "memory" / "heartbeat.md"
        if not hb.exists():
            hb.write_text("# Heartbeat\n\n| When | Task | Result | Note |\n|---|---|---|---|\n", encoding="utf-8")
        text = doctor.read(hb)
        note = f"{len(actions)} change(s)" if actions else "nothing to trim"
        hb.write_text(text.rstrip("\n") + f"\n| {today} | archive-trim | {'ran' if actions else 'skipped'} | {note} |\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
