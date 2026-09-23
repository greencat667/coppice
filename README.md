# Coppice

*A self-tending workspace for working with an AI assistant: plain files, lean by design, cut back so it keeps growing.*

Coppicing is cutting a tree back regularly so it regrows vigorously and lives for centuries. This workspace works the same way. Plain markdown files give your assistant persistent context about you and your work. A few standing rules, a weekly trim and a health check keep those files small enough to stay useful, instead of slowly silting up.

It grew out of eight months of daily use as a personal AI setup in Claude Cowork. Nearly every rule in it exists because something broke without it; [`docs/rules.md`](docs/rules.md) records what.

> **Status: under construction.** Phase 1 (templates and docs) is done. The `coppice doctor` health check, scheduled tasks, setup skill and a worked example are next. See [Roadmap](#roadmap).

## What you get

- **A profile of you** (`soul.md`): your rhythm, style and values, owned by you.
- **A session protocol** (`START-HERE.md`) the assistant follows: a small, fixed read at startup, everything else on demand, and a short routine at the end of each session.
- **Working memory that stays small:** tasks files that hold current state only, a three-week window of recent sessions, and a monthly archive.
- **Projects** with a lean index, numbered folders and append-only logs.
- **A learning loop:** the assistant notices corrections that generalise, logs them, and proposes the confirmed ones as changes you approve.
- **Budgets** for every file read at startup, so the startup read stays under about 8,000 tokens. That's fast even on a local model.

## How it's organised

| Layer | Answers | Lives in |
|---|---|---|
| Profile | Who is this person? | `soul.md` |
| Setup | What tools, contexts and limits apply? | `setup.md` |
| Protocol | What happens at the start and end of a session? | `START-HERE.md` |
| Now | What's live, and what's next? | `TASKS*.md` |
| Recently | What happened in the last few weeks? | `memory/recent*.md` |
| Projects | What's in flight? | `memory/projects.md`, `projects/` |
| Reference | Who's who, what the jargon means | `memory/glossary.md`, `memory/people/`, `context/` |
| Learning | How is the assistant adjusting? | `memory/learning-log.md` |

The full model, including where every kind of information goes, is in [`docs/layers.md`](docs/layers.md).

## Getting started

Until the setup skill lands, set it up by hand. It takes about 15 minutes.

1. Make an empty folder for your workspace. Somewhere stable, backed up, and **not** a public git repository: it will hold notes about your life and work.
2. Copy everything in [`workspace/`](workspace/) into it.
3. Copy the three files in [`docs/`](docs/) into your workspace's `context/coppice/` folder, so the assistant can read them.
4. Fill in `soul.md` and `setup.md`. Or open the folder in Cowork or Claude Code and say *"Interview me to fill in soul.md and setup.md"*.
5. Start a session: *"Read START HERE and let's go."*

It works with Claude Cowork and Claude Code, and with other assistants that read `AGENTS.md`. No connectors are required. Calendar, task-board and messaging integrations are optional, and described in `setup.md`.

## Repository

```
coppice/
├── workspace/          # The starter workspace: copy its contents into your folder
│   ├── START-HERE.md   # Session protocol
│   ├── AGENTS.md       # Pointer for assistants that look for AGENTS.md or CLAUDE.md
│   ├── CLAUDE.md
│   ├── soul.md         # Your profile (template)
│   ├── setup.md        # Contexts, tools, credential names, budgets (template)
│   ├── TASKS.md        # Current state only (template)
│   ├── memory/         # Projects index, recent sessions, learning log, glossary, people, heartbeat, archive
│   ├── projects/       # _template/ for new projects
│   ├── context/        # Reference material, including context/coppice/ for these docs
│   ├── reports/        # Output from scheduled tasks
│   └── working/        # Temporary inbox
└── docs/
    ├── rules.md        # Every rule, why it exists, and how it's kept
    ├── layers.md       # The layer model and "where does this go?"
    └── patterns.md     # Named ways of working: critique passes, evidence mode, handoffs…
```

## Roadmap

- [x] **Phase 1:** starter workspace templates; rules, layers and patterns docs
- [ ] **Phase 2:** `coppice doctor`, a health check for budgets, root clutter, logs, links, secrets and heartbeats, run weekly as a scheduled task
- [ ] **Phase 3:** scheduled-task templates (briefings with escalation, weekly review, archive trim); `coppice-setup`, `new-project` and `end-of-session` skills; a fictional worked-example workspace
- [ ] **Phase 4:** tested from an empty folder with a fresh session, and with a local model
- [ ] **Phase 5:** published

## Pairs well with

- [llm-wiki-skills-claude](https://github.com/greencat667/llm-wiki-skills-claude) — a knowledge wiki layer, maintained by the assistant
- [skill-gap-detector](https://github.com/greencat667/skill-gap-detector-skill-claude) — spots repeated work worth turning into a skill
- [autorefine](https://github.com/greencat667/autorefine-skill-claude) — reviews a session for wasted effort
- [futures-innovation-toolkit](https://github.com/greencat667/futures-innovation-toolkit) — a library of skills to use inside the workspace

## License

MIT — see [LICENSE](LICENSE). Not actively maintained once published; fork freely.
