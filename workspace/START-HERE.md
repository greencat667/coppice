# Start Here

You are working in a **Coppice** workspace: plain files that give you persistent context about the person you're helping and the work in progress. This file is the session protocol. Follow it before anything else.

## At the start of every session

1. Read `soul.md` — who the person is and how they like to work.
2. Read `setup.md` — their tools, contexts, and the size budgets this workspace keeps to.
3. Work out today's **context** from the table in `setup.md`, then read that context's tasks file and recent-sessions file. If the context is unclear, or the request crosses contexts, read every context's pair. Reading too little is worse than reading a little extra.

That's the whole startup read. **Don't ask for anything these files already answer.**

## Load on demand, not at startup

| When you need… | Read |
|---|---|
| Project status or a project number | `memory/projects.md` |
| Detail on one project | that project's `index.md`, then `log.md` |
| A name or term you don't recognise | `memory/glossary.md`, then `memory/people/` — ask only if it's in neither, and offer to add it |
| How the assistant has been adjusting its approach | `memory/learning-log.md` |
| Reference material (strategy docs, briefs, policies) | `context/` |
| The knowledge wiki, if there is one | its own schema file first (see `setup.md`) |

## Rules that always apply

- **Tasks files hold current state only.** Each entry: what it is, where it stands, one `Next:` line, a link to the project's `log.md`. History goes in `log.md`, never in tasks.
- **Nothing gets saved in the workspace root.** Project files go in the project's folder. Anything without a home goes in `working/` and gets filed or flagged before the session ends.
- **No secrets in any file.** Refer to credentials by name as listed in `setup.md`. If you find a secret written into a file, stop and tell the person.
- **`soul.md` belongs to the person.** Propose changes to it; never rewrite it silently.
- **Confirm before anything outward-facing or irreversible**, e.g. sending, publishing or deleting, or acting across several projects or systems at once.

The full rule set, with the reason behind each rule, is in `context/coppice/rules.md`. You don't need to read it to follow this file.

## Stop and check if

- a file or piece of context you expected isn't there
- an action would affect more than one project, or any external system
- you're asked to use a system `setup.md` says isn't connected

Say what you were trying to do and why you stopped.

## At the end of every session

1. **Tasks** — update the current context's tasks file: new, changed and finished items, current state only.
2. **Project logs** — append a dated entry to the `log.md` of every project you worked on: what was done, what was decided and why.
3. **Projects index** — update `memory/projects.md` if a status changed or a project was created. Keep the next-number line correct.
4. **Recent sessions** — add a short entry to the context's recent-sessions file: what happened, what changed, key decisions.
5. **Correction scan** — look back over the session for moments where the person corrected or redirected you. If one would generalise into a rule, offer it as a learning-log entry: *"Worth adding to the learning log?"* One or two at most.
6. **File the inbox** — anything left in `working/` gets filed into a project or flagged.

Trimming old recent-session entries into `memory/archive/` is handled by the `archive-trim` scheduled task. Do it by hand only if that task hasn't run for more than a week.

## Working patterns

Named ways of working the person can ask for, such as *two-pass critique* or *evidence mode*, are defined in `context/coppice/patterns.md`. Use one when it's asked for, or offer it when it clearly fits. For where a new piece of information belongs, see the table in `context/coppice/layers.md`.
