# Rules

Every standing rule in a Coppice workspace, with the failure that produced it and how it's kept.

None of these were designed up front. Each one exists because a working system broke in a particular way, and a one-off fix didn't hold. The "Why" line records that failure, so you can judge whether the rule applies to you before deleting it.

**How it's kept** says whether the rule is enforced by a check (`coppice doctor`), by a scheduled task, or only by the session protocol in `START-HERE.md`. Prefer the first two. Rules that depend on someone remembering them get broken; that's rule 20.

---

## Startup and loading

### 1. The startup read is small and fixed

Read `soul.md`, `setup.md`, and one context's tasks and recent-sessions files. Nothing else at startup.

**Why:** The startup read grew by accretion until it reached about 90,000 tokens. With a local model, "read start here" took over twelve minutes before any work began. Cloud models hid the cost rather than removing it: every session paid for context it didn't use.
**How it's kept:** `budgets.startup_tokens` in `setup.md`, checked by `doctor`.

### 2. Depth loads on demand

Indexes at startup; detail only when the task needs it. The projects index, project logs, the glossary, people files and reference documents are all load-on-demand.

**Why:** Most of what was being read at startup was project detail relevant to one session in twenty.
**How it's kept:** The load-on-demand table in `START-HERE.md`.

### 3. Don't ask for what the files already answer

Check the startup files, then the glossary and people files, before asking. If it isn't there, ask, and offer to add it.

**Why:** Re-explaining context every session is the problem this whole system exists to solve.
**How it's kept:** `START-HERE.md`.

### 4. When unsure which context applies, read all of them

**Why:** Reading one context's files when the request crossed into another produced confident answers from missing information. The extra reading costs less than that.
**How it's kept:** `START-HERE.md`.

---

## Working memory

### 5. Tasks files hold current state only

Each entry: what it is, where it stands, one `Next:` line, a link to the project log. No dated history.

**Why:** Tasks files are read every session, so each "✅ (date) — did X because Y" gets paid for again every day. One tasks file grew to nearly 150KB, most of it history already recorded in project logs. A one-time cleanup didn't hold: it regrew the same way within weeks, until this became a standing rule.
**How it's kept:** `budgets.tasks_kb`, checked by `doctor`, which also flags dated "✅" lines in tasks files.

### 6. Recent sessions keep a rolling window

Keep the last three weeks by default. Older entries move to `memory/archive/YYYY-MM.md`, one file per month. The archive is load-on-demand.

**Why:** The recent-sessions file reached 180KB. It's read every session, but the value of an entry falls off fast after a few weeks.
**How it's kept:** The `archive-trim` scheduled task weekly, with the end-of-session protocol as backup. `doctor` checks `budgets.recent_days`.

### 7. One fact, one home

Every rule, setting and piece of reference information lives in exactly one file. Everywhere else links to it.

**Why:** The same working patterns were written into three files and drifted apart until they disagreed. A README described a folder layout that no longer existed. Stale numbers ("the next project will be 026") lingered months after they were wrong.
**How it's kept:** `docs/layers.md` says where each kind of thing lives. `doctor` checks internal links and the next-project-number line.

### 8. Split the person from the machine

`soul.md` is about the human: rhythm, style, values. `setup.md` is about tools, IDs, paths and budgets.

**Why:** Calendar IDs and install paths mixed into the profile meant it changed weekly for mechanical reasons, which made it hard to see when something about the *person* had changed.
**How it's kept:** The templates.

---

## Files and projects

### 9. Nothing gets saved in the workspace root

Only the files listed in `root_allowed` in `setup.md`. Everything else goes in a project, `context/`, `reports/`, or temporarily `working/`.

**Why:** "Just this once" saves to the root added up to dozens of loose files, with no way to tell which ones mattered.
**How it's kept:** `doctor` lists anything in the root that isn't allowed.

### 10. `working/` is an inbox, not a home

Anything left there at the end of a session gets filed into a project or flagged to the person.

**Why:** Without a filing step, a temporary folder becomes a permanent one.
**How it's kept:** The end-of-session protocol. `doctor` reports files in `working/` older than a week.

### 11. Every project has an append-only log

`projects/NNN-short-name/log.md`: a dated entry per session that touched the project. Never edit old entries; add a correcting one.

**Why:** The log is where history goes so that tasks files and recent sessions can stay small (rules 5 and 6). When logs were skipped, the task files quietly diverged from what had actually happened, and nobody could reconstruct why.
**How it's kept:** The end-of-session protocol. `doctor` flags project folders with no `log.md`, and active projects whose log hasn't changed in 30 days.

### 12. Fast-moving projects get a status board

A small `status-board.md`, overwritten rather than appended, showing current state at a glance.

**Why:** Long-running projects with many workstreams kept pushing detail back into the tasks file, because the log was too long to scan. A compact current-state file let the task entry shrink to one line.
**How it's kept:** Judgement: add one when a project's task entry starts growing again.

### 13. Match the weight to the work

Three tiers: **Project** (an end state, full folder), **Light** (one file), **Tracker** (ongoing, no end state; one line in the tasks file).

**Why:** Giving every piece of work a numbered folder, a log, an index entry and a card on a board was overhead that small or ongoing work never repaid. Running an ongoing responsibility as a "project" with exit criteria confused both.
**How it's kept:** The `new-project` skill asks which tier is needed.

### 14. Creating a project has a checklist

Folder and `index.md` · first `log.md` entry · row in `memory/projects.md` · next-number line updated · tasks entry. External board card too, if you use one.

Take the number from the index and advance the next-number line **in the same step**, before building anything else. Then check no folder already starts with that number.

**Why:** When momentum is high and the context is full, one of these steps gets skipped, and the index and the folders drift apart. When the next-number line lagged behind, sessions handed out numbers that were already taken: one real workspace ended up with eleven numbers shared by two or three folders each. Logs and task entries then went into the wrong folder, and renumbering later meant rewriting every reference.
**How it's kept:** The `new-project` skill runs the checklist. `doctor` checks that folders and index rows match, corrects a next-number line that has fallen behind, and reports any number used by more than one folder.

---

## Safety and ownership

### 15. No secrets in any file, ever

Credentials are named in `setup.md` and kept in the OS keychain or a `.env` file that is never committed or shared.

**Why:** API tokens written into a setup note were later copied into scheduled-task prompts, and then into a backup of those prompts. Every copy was another place the secret could leak from. Once a secret is in a file, the file's whole future is a risk.
**How it's kept:** `doctor` scans every file for credential patterns. `START-HERE.md` tells the assistant to stop and tell the person if it finds one.

### 16. The person owns `soul.md`

The assistant proposes changes; it never makes them silently.

**Why:** A profile quietly rewritten by the thing it describes stops being trustworthy, even when each change is small and well meant.
**How it's kept:** `START-HERE.md`.

### 17. Confirm before anything outward-facing or irreversible

Sending, publishing, deleting, spending, or acting across several projects or systems at once: say what you're about to do, then wait for a yes.

**Why:** These are the actions where a mistake can't be taken back, and where the person's judgement adds most.
**How it's kept:** `START-HERE.md`, plus the assistant's own safeguards.

### 18. Stop when something's missing

If an expected file or piece of context isn't there, or an action would touch more than one project or an external system, stop, say what you were doing and why you stopped.

**Why:** Guessing to fill a gap produces output that looks right and isn't, and is much harder to catch than a question.
**How it's kept:** `START-HERE.md`.

### 19. When two assistants share a workspace, ownership is written down

If more than one assistant (or person) works on the same files, each shared piece of work records who currently owns it, e.g. an `owner:` field in a `STATE.yaml`. Nobody edits what they don't own, and handing over is an explicit step.

**Why:** Two assistants editing the same files in turn overwrote each other's work, and a quality step that neither owned was silently skipped until it became a required, named field.
**How it's kept:** The state file itself. See `docs/patterns.md` → *Handoff contract*.

---

## Keeping the system healthy

### 20. Rules you can check beat rules you remember

When something keeps going wrong, reach for structure (a script, a state file, a schema, a scheduled check) before rewriting the instructions.

**Why:** Time and again the fix for an unreliable workflow wasn't a better prompt but structure around it: a required field, a checklist, a check that fails loudly. Rules that relied on memory held for a few weeks and then quietly lapsed.
**How it's kept:** This is why `coppice doctor` exists. The weekly review asks: *is anything here being done by memory that a check could do?*

### 21. Every scheduled task leaves a heartbeat

Each run appends one line to `memory/heartbeat.md`: when, which task, and whether it ran, was skipped or failed.

**Why:** Scheduled tasks disabled themselves or vanished without any error, and were only noticed weeks later when someone wondered why something hadn't happened.
**How it's kept:** Every scheduled-task template writes the line. `doctor` flags any task whose heartbeat is older than its schedule allows.

### 22. Repeated flags escalate

If a briefing raises the same item for `budgets.stale_flag_days` days in a row, it moves up a rung. First it flags. Then it proposes one specific unsticking action. Then it asks whether to park the item or drop it.

**Why:** A morning briefing flagged the same overdue deadline, in almost the same words, every day for weeks. After the first few days a repeated flag becomes background noise.
**How it's kept:** The briefing templates track how many days an item has been flagged.

### 23. Fix skills at the source

If a skill has a wrong step, fix the skill. Don't add a note elsewhere that says "ignore step 4 of that skill".

**Why:** An override file that contradicted an installed skill had to be remembered, and the next session that didn't read it produced the wrong output.
**How it's kept:** Keep your skills in a folder you control, and install from there.

### 24. The learning log cycles; it doesn't accumulate

Active entries only. Confirmed entries graduate into `START-HERE.md`, `soul.md` or a skill, as a proposal the person approves. Discarded ones move to the archive with their verdict.

**Why:** A learning log that kept everything grew to tens of kilobytes, with settled lessons buried among live experiments. Nothing graduated, because nothing forced a decision.
**How it's kept:** `budgets.learning_log_kb`, checked by `doctor`. The weekly review does one "promote, prune or park" pass.

### 25. Generated reports expire

Scheduled tasks write reports to `reports/`, not to `memory/`, and `archive-trim` deletes them after `budgets.reports_days`.

**Why:** A weekly report written into the memory folder produced a new file every week, until they outnumbered the files that were actually memory.
**How it's kept:** `archive-trim`; `doctor` flags reports written anywhere else.

## Paths and code

### 26. Code repos live with their project, and path-sensitive ones in `code/`

A repo (an app, a tool, a local server) goes in its project's folder, not the workspace root. A repo whose toolchain can't cope with spaces in its path goes in `code/<name>`, with a note in the project's log saying where it is. Before moving any repo that already exists, check what points at it.

**Why:** Loose repos piled up in the root of a real workspace, some of them gigabytes. Filing them was mostly easy, but a few broke when moved. An embedded-firmware toolchain (ESP-IDF) failed to build under a project folder whose name had spaces, and built again once moved to a path under `code/` with none. Other repos were wired into things outside the workspace: an MCP server registered in another app's config by absolute path, a Python virtualenv whose scripts record their own location, a cron job, and a server that was still running.
**How it's kept:** The adopt checklist in the `coppice-setup` skill. Record anything that must stay put in `setup.md`, with the reason.

### 27. Names are plain: lower-case, hyphens, no spaces

Folders and files the assistant creates use lower-case ASCII letters, digits and hyphens: `projects/012-renewable-energy/`, `outputs/funding-brief-v2.docx`. No spaces, accents, apostrophes, ampersands or brackets. The human-readable title goes in the index and the file itself, not the path. Dates in names are ISO (`2026-09-24`).

**Why:** Names like `NNN - Name` read well but cost something every time a tool touches them. In one workspace, links the assistant wrote to spaced folders didn't open until they were URL-encoded, every shell command needed careful quoting, and a firmware toolchain refused to build inside a spaced folder at all (rule 26). Plain names avoid all of that.
**How it's kept:** The `new-project` skill makes the slug. `doctor` notes folders with spaces or special characters, as one grouped note per folder, because renaming existing folders is optional: an adopted workspace can keep its old names and use plain ones for new projects only.

