---
name: archive-trim
description: Weekly cut-back — moves aged-out recent sessions and settled learning-log entries to the archive, and clears old heartbeat lines and reports
schedule: At 07:30, only on Monday
cronExpression: 30 7 * * 1
enabled: true
---

You are running the weekly cut-back for this Coppice workspace. It keeps the files read every session small by moving what has aged out of them. It's the coppicing: regular, modest, and done by a script so it doesn't depend on anyone remembering.

## Step 0 — Check this task is wanted

Look for `archive-trim` in the **Scheduled tasks** table in `setup.md`. If it isn't there, the person either declined it or never set it up: **don't run it.** Say so in one line, offer to add it to the table if they'd like it, and write nothing, not even a heartbeat line.

(If the person asks for this in a conversation rather than it running on a schedule, just do it; the check is for unattended runs.)

## Step 1 — Run the trim

From the workspace folder:

```bash
python3 context/coppice/trim.py --heartbeat
```

This:

- moves recent-session entries older than `budgets.recent_days` into `memory/archive/YYYY-MM.md`
- moves learning-log entries marked `[graduated …]` or `[discarded …]` into `memory/archive/learning-log-archive.md`
- deletes heartbeat lines older than 60 days
- deletes generated reports in `reports/` older than `budgets.reports_days`
- records the run in `memory/heartbeat.md`

It only deletes generated files. Everything else is moved, never deleted.

If Python isn't available, append `| YYYY-MM-DD | archive-trim | failed | python3 not available |` to `memory/heartbeat.md` and say so. Don't attempt the trim by hand.

## Step 2 — Report

Post the script's output in the conversation in one short block. If it trimmed nothing, one line is enough.
