---
name: coppice-doctor
description: Weekly health check of the Coppice workspace — budgets, clutter, logs, links, secrets and heartbeats — with safe mechanical fixes
schedule: At 08:00, only on Monday
cronExpression: 0 8 * * 1
enabled: true
---

You are running the weekly health check for this Coppice workspace. Your job is to run `coppice doctor`, apply only its safe mechanical fixes, and tell the person what needs their judgement. You don't fix anything the doctor didn't fix itself.

## Step 1 — Run the doctor

From the workspace folder, run:

```bash
python3 context/coppice/doctor.py --fix --report reports/doctor-$(date +%F).md --heartbeat
```

- `--fix` applies only mechanical fixes: moving old recent-session entries to `memory/archive/`, correcting a next-project-number line that's fallen behind, and adding a stub `log.md` to a project folder that has none.
- `--report` writes the full report to `reports/`.
- `--heartbeat` records this run in `memory/heartbeat.md`.

If Python isn't available, don't try to reproduce the checks by hand. Write a line to `memory/heartbeat.md` — `| YYYY-MM-DD | coppice-doctor | failed | python3 not available |` — and tell the person.

## Step 2 — Report back

Post a short summary in the conversation:

1. **Anything in the Errors section first**, one line each. A possible secret is always first. Say which file, never repeat the value, and suggest moving it to the keychain or an uncommitted `.env` and rotating it if the file was ever shared.
2. **Fixes applied**, one line each.
3. **Warnings**, grouped: at most five lines, with a pointer to the full report for the rest.
4. **One suggestion**: the single warning that would most improve the workspace if fixed this week.

If the report says "All clear", say so in one line and stop.

## Rules

- Never delete, move or rewrite anything beyond what `doctor.py --fix` did.
- Never print a secret, even partly, beyond what the report already shows.
- If the doctor exits with an error you can't explain (not just "errors found"), record `failed` in the heartbeat with a few words on why, and say so.
