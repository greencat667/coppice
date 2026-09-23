# Scheduled tasks

Templates for tasks that run on a schedule. Each file has a frontmatter block (`name`, `description`, `schedule`, `cronExpression`, `enabled`) and the prompt to run.

To set one up in Claude Cowork, open the file and ask Claude to *"create a scheduled task with this cron expression and this prompt"*, or use `/schedule`. Then add the task to the **Scheduled tasks** table in your `setup.md`, so the doctor knows how often to expect a heartbeat.

**Every scheduled task writes a heartbeat.** Its last step appends one line to `memory/heartbeat.md`:

```
| 2026-09-28 | task-name | ran | a few words on what happened |
```

Use `ran`, `skipped` (nothing to do) or `failed` (with the reason). `coppice doctor` uses these lines to spot tasks that have quietly stopped running (rule 21 in `docs/rules.md`).

| Task | When | What it does |
|---|---|---|
| [`morning-briefing.md`](morning-briefing.md) | Weekdays | Today's context: calendar, what's due, what's stuck. Flags escalate through `memory/flags.md` instead of repeating |
| [`weekly-review.md`](weekly-review.md) | Friday afternoon | What moved, what's stuck, the learning log's promote/prune/park pass, one question about the system |
| [`archive-trim.md`](archive-trim.md) | Monday morning | Runs `trim.py`: moves aged-out entries to the archive, clears old heartbeat lines and reports |
| [`doctor.md`](doctor.md) | Monday morning | Runs `doctor.py --fix` and reports what needs a human decision |

**Every template starts with a guard:** if the task isn't listed in `setup.md`'s Scheduled tasks table, it doesn't run. That way a declined task can't run by accident and leave misleading heartbeat lines.

The morning briefing's escalation counts **consecutive scheduled briefings**, not calendar days, so a Monday briefing follows on from Friday's.

Schedules are suggestions; change the cron expression to suit your week. Run `archive-trim` before `doctor` so the doctor sees the trimmed files.

These pair well with tasks published elsewhere: [session capture, wiki ripple and wiki lint](https://github.com/greencat667/llm-wiki-skills-claude), [signal monitoring](https://github.com/greencat667/trend-signal-monitor-skill-claude), [grant scanning](https://github.com/greencat667/grant-scanner-skill-claude) and [skill-gap detection](https://github.com/greencat667/skill-gap-detector-skill-claude). If you add one, have it write a heartbeat line and put its reports in `reports/`.
