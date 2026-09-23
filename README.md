# Coppice

*A self-tending workspace for working with an AI assistant: plain files, lean by design, cut back so it keeps growing.*

Coppicing is cutting a tree back regularly so it regrows vigorously and lives for centuries. This workspace works the same way. Plain markdown files give your assistant persistent context about you and your work. A few standing rules, a weekly trim and a health check keep those files small enough to stay useful, instead of slowly silting up.

It grew out of eight months of daily use as a personal AI setup in Claude Cowork. Nearly every rule in it exists because something broke without it; [`docs/rules.md`](docs/rules.md) records what.

## What you get

- **A profile of you** (`soul.md`): your rhythm, style and values, owned by you.
- **A session protocol** (`START-HERE.md`) the assistant follows: a small, fixed read at startup, everything else on demand, and a short routine at the end of each session.
- **Working memory that stays small:** tasks files that hold current state only, a three-week window of recent sessions, and a monthly archive.
- **Projects** with a lean index, numbered folders and append-only logs.
- **A learning loop:** the assistant notices corrections that generalise, logs them, and proposes the confirmed ones as changes you approve.
- **Budgets** for every file read at startup, so the startup read stays under about 8,000 tokens. That's fast even on a local model.
- **Scheduled tasks** that tend it: a weekly trim, a weekly health check, and optionally a morning briefing whose repeated flags escalate (flag → propose an action → ask whether to park it) instead of nagging, and a weekly review.
- **A health check** (`coppice doctor`) that checks the rules instead of relying on anyone remembering them: budgets, clutter, missing logs, project numbering, broken links, secrets written into files, and scheduled tasks that have quietly stopped. It fixes only the mechanical problems and reports the rest. See [`docs/doctor.md`](docs/doctor.md).

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

**Ask Claude to set it up.** Make an empty folder somewhere stable and backed up (**not** a public git repository: it will hold notes about your life and work), open it in Claude Cowork or Claude Code, and say:

> *"Set up a Coppice workspace in this folder. Follow `skills/coppice-setup/SKILL.md` from github.com/greencat667/coppice."*

Claude will copy the files in, interview you for `soul.md` and `setup.md` a few questions at a time, add your first tasks, and offer the scheduled tasks and companion skills. It finishes by running the health check. Level 0 takes about 15 minutes; see [`docs/maturity.md`](docs/maturity.md) for what to add when.

**Already have a setup of your own?** Say *"Adopt Coppice for my existing setup"*. The same skill surveys what you have, read-only, and writes a migration plan in small, approved steps. Secrets come first. Nothing moves without a yes.

**By hand:** copy everything in [`workspace/`](workspace/) into your folder; copy [`docs/`](docs/), [`scripts/doctor.py`](scripts/doctor.py) and [`scripts/trim.py`](scripts/trim.py) into its `context/coppice/`; fill in `soul.md` and `setup.md`; then start a session with *"Read START HERE and let's go."*

To see what a workspace looks like after two weeks of use, browse the fictional [`examples/workspace/`](examples/workspace/).

It works with Claude Cowork and Claude Code, and with other assistants that read `AGENTS.md`. No connectors are needed. Calendar, task-board and messaging integrations are optional, and described in `setup.md`.

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
├── docs/
│   ├── rules.md        # Every rule, why it exists, and how it's kept
│   ├── layers.md       # The layer model and "where does this go?"
│   ├── patterns.md     # Named ways of working: critique passes, evidence mode, handoffs…
│   ├── doctor.md       # What the health check checks, skips and fixes
│   ├── maturity.md     # Levels 0–3: what to add, and when
│   └── testing.md      # How it was tested, and what the tests found
├── scripts/
│   ├── doctor.py       # coppice doctor: the health check (Python 3.9+, standard library only)
│   ├── trim.py         # the weekly cut-back, run by the archive-trim task
│   └── make_example.py # regenerates examples/workspace
├── scheduled-tasks/    # morning-briefing, weekly-review, archive-trim, doctor
├── skills/             # coppice-setup (new / update / adopt), new-project, end-of-session
├── examples/workspace/ # A fictional workspace two weeks in
├── tests/              # python3 -m unittest discover tests
├── CONTRIBUTING.md
└── LICENSE
```

## How it was tested

The scripts have a test suite (`python3 -m unittest discover tests`) that runs on every push, on Python 3.9 and 3.12. The whole system was also put through a newcomer test: a fresh assistant session, with nothing but this repository and a fictional newcomer to play, set it up from scratch, used it for a compressed week, and ran adopt mode on a deliberately messy setup. It found one real bug and eleven rough edges, all now fixed. See [`docs/testing.md`](docs/testing.md).

## Pairs well with

- [llm-wiki-skills-claude](https://github.com/greencat667/llm-wiki-skills-claude) — a knowledge wiki layer, maintained by the assistant
- [skill-gap-detector](https://github.com/greencat667/skill-gap-detector-skill-claude) — spots repeated work worth turning into a skill
- [autorefine](https://github.com/greencat667/autorefine-skill-claude) — reviews a session for wasted effort
- [futures-innovation-toolkit](https://github.com/greencat667/futures-innovation-toolkit) — a library of skills to use inside the workspace

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Note that this repo isn't actively maintained, so responses to issues and PRs will be slow or may never come. Forking is the way to make it yours.

## License

MIT — see [LICENSE](LICENSE).
