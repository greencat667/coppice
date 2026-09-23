---
name: morning-briefing
description: Short start-of-day briefing for today's context — calendar, what's due, what's stuck — with flags that escalate instead of repeating
schedule: At 07:45 on weekdays
cronExpression: 45 7 * * 1-5
enabled: true
---

You are writing the morning briefing for the person this Coppice workspace belongs to. It should take them under a minute to read, and end with one clear thing to do first.

## Step 0 — Check this task is wanted

Look for `morning-briefing` in the **Scheduled tasks** table in `setup.md`. If it isn't there, the person either declined it or never set it up: **don't run it.** Say so in one line, offer to add it to the table if they'd like it, and write nothing, not even a heartbeat line.

(If the person asks for this in a conversation rather than it running on a schedule, just do it; the check is for unattended runs.)

## Step 1 — Read

1. `START-HERE.md`, then follow its startup read: `soul.md`, `setup.md`, and **today's context's** tasks and recent-sessions files. Work out today's context from the Contexts table in `setup.md`.
2. `memory/flags.md`.
3. If `setup.md` lists a connected calendar, today's events for this context. If it lists more than one calendar, check all of them. If there's no calendar connection, skip this and don't mention it.

If today matches no context (e.g. a day off), write a one-line briefing saying so, record the heartbeat as `skipped`, and stop.

## Step 2 — Decide what to flag

Look for, in this order:

- **Clashes and prep:** meetings that overlap, or that need something prepared that isn't in the tasks file yet.
- **Due or overdue:** items in the tasks file with a date today or earlier.
- **Stuck:** items in *Waiting on someone* whose nudge date has passed, and 🔴 items with no change in recent sessions for several days.
- **Anything `soul.md` says to watch for on this day** (e.g. "flag class prep on Wednesday mornings").

Flag at most five things. Fewer is better.

**Nothing to flag is a normal day.** Say so in one line (*"Nothing due or stuck today."*) and still give a **First thing**: usually the nearest deadline's next step.

## Step 3 — Escalate, don't repeat

For each item you're flagging, find its row in `memory/flags.md` (or add one at rung 1):

- If it was also flagged on the **previous scheduled briefing** (the last one that ran, e.g. yesterday, or Friday if today is Monday), add one to **Times at this rung**. Otherwise reset the count to 1. Escalation counts consecutive briefings, not calendar days.
- When **Times at this rung** reaches `budgets.stale_flag_days` from `setup.md`, move it up a rung and reset the count.
- Write it differently depending on its rung:
  - **Rung 1:** flag it plainly.
  - **Rung 2:** don't just re-flag it. Propose **one specific action** that would unstick it today, e.g. a named person to chase, a smaller first step, or a decision to make.
  - **Rung 3:** ask directly whether to **park it** (move it to Paused with a revisit date) or **drop it**. Say how long it's been flagged.

Remove rows for items that are now done, parked or dropped. Update **Last flagged** for everything you flagged today.

## Step 4 — Write the briefing

Post it in the conversation. Keep to this shape:

```
**[Day, date] — [context]**

[Calendar: one line per event worth mentioning, with clashes marked. Omit if there's no calendar.]

🔴 [Item] — [one line]. [Rung 2: "Suggest: …" / Rung 3: "Flagged N days — park or drop?"]
🟡 [Item] — [one line]

**First thing:** [one concrete action, sized to the morning]
```

Follow the tone in `soul.md`. No summaries of things that are fine, no motivational filler.

## Step 5 — Record

- Save `memory/flags.md`.
- Append to `memory/heartbeat.md`: `| YYYY-MM-DD | morning-briefing | ran | N flags, top: [item] |`
- **Don't** add an entry to the recent-sessions file. A briefing isn't a session, and daily briefing entries are the fastest way to bloat it.

## Rules

- Don't change the tasks file. Suggest changes; the person or a working session makes them.
- Don't flag work from another context unless it has a hard deadline today.
- If a file the startup read needs is missing, say so in the briefing and record the heartbeat as `failed`.
