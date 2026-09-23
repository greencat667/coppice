---
name: end-of-session
description: >
  Close a working session in a Coppice workspace so the next session starts with the right context — tasks updated to current state, project logs appended, the projects index and recent-sessions file updated, corrections that generalise offered to the learning log, and the working/ inbox filed. Triggers on: "end of session", "wrap up", "let's wrap", "update memory files", "log this session", "save where we got to", "that's it for today", "tidy up before I go". Use at the end of any working session in a workspace with START-HERE.md. Keeps history out of the files read every session, which is what keeps them small.
---

# End of session

The five minutes that make the next session work. Everything here comes from the protocol in `START-HERE.md`. This skill runs it carefully and shows what changed.

## 1. Gather

Look back over the session and list:

- **Work done**, per project, with the decisions made and why
- **Task changes:** new, finished, changed and blocked items
- **Project changes:** created, status changed, closed
- **Corrections:** moments where the person redirected you ("no, like this")
- **Files created**, and where they are

## 2. Write, in this order

1. **Project logs.** Append one dated entry to each touched project's `log.md`: what was done, what was decided, why. This is where history goes, so be specific. Never edit old entries.
2. **Status boards.** If a touched project has a `status-board.md`, overwrite the rows that changed.
3. **Tasks.** Update the right context's tasks file to **current state only**: what it is, where it stands, `Next:`, a link to `log.md`. Remove finished items. Their story is already in the log.
   - If you catch yourself writing "✅ (date) — did X…" in a tasks file, stop: that sentence belongs in the log.
4. **Projects index.** Update `memory/projects.md` for any status change or new project, and check the next-number line.
5. **Recent sessions.** Add one short entry at the top of the context's recent-sessions file (newest first): `## YYYY-MM-DD — short title`, then three to five bullets covering what happened, what changed, and the key decisions.
6. **Inbox.** For each file in `working/`, move it to the right project (with approval if it's not obvious) or list it for the person to decide.

If the session touched more than one context, update each context's files.

## 3. Offer, don't impose

- **Correction scan.** From the corrections you listed, pick at most two that would apply to future sessions too. Offer each as a learning-log entry in one line: *"Worth adding to the learning log? — [observation] → [adjustment to try]"*. Write it as `[trying]` only if they say yes.
- **Knowledge.** If the session produced an idea that will stay true whichever project it came from, and the workspace has a knowledge wiki (see `setup.md`), offer to add it. Skip this for routine sessions.
- **Graduation.** If an existing learning-log entry came up again and held, say so: *"That's the third time for [entry] — ready to confirm it?"*

## 4. Check and confirm

- If Python is available, run `python3 context/coppice/doctor.py`. If it reports a budget, log or index problem this session caused, fix it now. Mention any other errors in one line.
- Finish with one short block:

```
Updated: [files]
Next session starts with: [the most important Next: line]
```

## Rules

- Current state in tasks; history in logs. Always.
- Never rewrite `soul.md` or `START-HERE.md` here. Propose changes instead.
- Don't write secrets anywhere, even in a log entry describing what was set up.
- Keep the recent-sessions entry short. It's read every session for three weeks.
