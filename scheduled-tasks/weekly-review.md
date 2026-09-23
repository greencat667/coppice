---
name: weekly-review
description: Weekly review — what moved, what's stuck, the learning log's promote/prune/park pass, and one question about the system itself
schedule: At 16:00, only on Friday
cronExpression: 0 16 * * 5
enabled: true
---

You are running the weekly review for this Coppice workspace. It looks back over the week, clears what's stale, and looks after the system itself. It should take the person five minutes to read and act on.

## Step 0 — Check this task is wanted

Look for `weekly-review` in the **Scheduled tasks** table in `setup.md`. If it isn't there, the person either declined it or never set it up: **don't run it.** Say so in one line, offer to add it to the table if they'd like it, and write nothing, not even a heartbeat line.

(If the person asks for this in a conversation rather than it running on a schedule, just do it; the check is for unattended runs.)

## Step 1 — Read

1. `START-HERE.md`, `soul.md`, `setup.md`.
2. **Every** context's tasks and recent-sessions files, since this review crosses contexts.
3. `memory/projects.md`, `memory/flags.md` and `memory/learning-log.md`.
4. The latest `reports/doctor-*.md`, if there is one from this week.

## Step 2 — Write the review

Post it in the conversation:

**What moved.** Three to six lines: projects and tasks that changed state this week, from the recent-sessions files.

**What's stuck.** Items at rung 2 or 3 in `memory/flags.md`, and active projects in `memory/projects.md` with no recent-sessions mention for two weeks or more. Also list any project folder that isn't in `memory/projects.md` at all (the doctor report's `projects-index` warning shows these): a project nobody has indexed is stuck by definition. For each, one line and a suggested decision: *keep going* (with a next action), *park* (with a revisit date) or *close*.

**Learning log — promote, prune or park.** For each active entry:

- **Promote** if it's been confirmed several times. Write out the exact change to `START-HERE.md`, `soul.md` or a skill, for the person to approve. Don't make it yourself.
- **Prune** if it's been `trying` for more than about six weeks with no new evidence. Propose marking it `[discarded — reason]`.
- **Park** if it's still genuinely open. Leave it.

Keep this to one line per entry.

**Health.** One line from this week's doctor report: all clear, or the single most important warning.

**One question about the system.** Ask one of these, whichever fits the week best:

- *Is anything being done by memory that a check or a script could do?*
- *Which file did we read most this week that told us least?*
- *What kept getting re-explained?*

## Step 3 — Record

- Append to `memory/heartbeat.md`: `| YYYY-MM-DD | weekly-review | ran | N stuck, N learning-log proposals |`

## Rules

- Propose; don't change. Every change to tasks, projects, `soul.md`, `START-HERE.md` or the learning log waits for a yes. The only exception is marking learning-log entries the person explicitly approves in the conversation.
- Keep the review under a page.
