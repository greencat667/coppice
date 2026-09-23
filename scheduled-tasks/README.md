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
| [`doctor.md`](doctor.md) | Weekly | Runs `coppice doctor --fix` and reports what needs a human decision |

*More tasks arrive in phase 3: morning briefing (with escalation), context-day briefing, weekly review, archive trim.*
