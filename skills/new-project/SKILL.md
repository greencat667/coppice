---
name: new-project
description: >
  Start a new piece of work in a Coppice workspace at the right weight — a Tracker line, a Light single file, or a full numbered Project folder — and run the creation checklist so the index, tasks and folders never drift apart. Triggers on: "new project", "start a project", "set up a project for", "create a project folder", "kick off [name]", "track this", "add a tracker for", "this needs a folder". Use whenever something new needs a home in a Coppice workspace (one with START-HERE.md and memory/projects.md). Not for creative-writing series or other workflows with their own kickoff skill.
---

# New project

Gives new work a home at the right weight, then runs the creation checklist. Most of the value is in two things: asking the tier question, and not skipping a step when momentum is high (rules 13 and 14 in `context/coppice/rules.md`).

## 1. Ask which tier

Ask one question, with your suggestion:

> "Does this have an end state, or does it just run? And is it more than a single document?"

| Tier | For | What gets created |
|---|---|---|
| **Tracker** | Ongoing, no end state (a budget, a relationship, a recurring duty) | One line in the tasks file's *Trackers* section |
| **Light** | Small, short, one output (under a day or two of work) | One file in `working/`, or in the relevant `context/` subfolder, listed in the *Light* section of `memory/projects.md` if it'll last more than a week |
| **Project** | An end state, several outputs or sessions | A numbered folder and the full checklist below |

If they're unsure, suggest the lighter tier. It's easy to promote later.

## 2. For a Project

1. **Root and number.** Read `setup.md` for `project_roots`. If there's more than one, ask which. Take the number from the matching "Next project number" line in `memory/projects.md`.
2. **Folder.** Copy `projects/_template/` (or the root's template) to `<root>/NNN - Name/`. Use a short, plain name.
3. **`index.md`.** Fill in the one-line description, status, goal and first next step.
4. **`brief/brief.md`.** Fill in the three lines: objective, approach, success. Draft them from the conversation and confirm them.
5. **`log.md`.** Write the first entry: date, why the project exists, the first step taken.
6. **Index row.** Add a row to *Active* in `memory/projects.md`, with the folder path in backticks.
7. **Next number.** Increment the matching "Next project number" line.
8. **Tasks entry.** Add a line to the right context's tasks file: current state, `Next:` and a link to `log.md`.
9. **External board** *(only if `setup.md` lists one)*. Offer to create a card. Don't create it without a yes.
10. **Check.** Run `python3 context/coppice/doctor.py` if Python is available, and confirm there are no `project-log`, `projects-index` or `next-number` findings. If Python isn't available, re-read the index row and next-number line yourself.

Then confirm in one short block: the folder, number, tier, first next step, and anything skipped (e.g. "no board card: you said no").

## 3. For a Tracker or Light

- **Tracker:** add the line to *Trackers* in the tasks file: current state plus **Next check:** date.
- **Light:** create the file with a three-line brief at the top. If it will last more than a week, list it under *Light* in `memory/projects.md` (no number).

## Rules

- One number per project, from the index, never guessed. If the index and the folders disagree, stop and point it out before creating anything.
- Never reuse a number, even from a deleted project.
- Don't create a project for something that's really a task. Say so, and add it as a task instead.
