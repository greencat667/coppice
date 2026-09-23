# Setup

> Contexts, tools, where things live, and budgets. No secrets: credentials are listed by name only.

---

## Contexts

| Context | When | Tasks file | Recent sessions |
|---|---|---|---|
| work | Mon–Thu | `TASKS-work.md` | `memory/recent-work.md` |
| personal | Fri–Sun | `TASKS-personal.md` | `memory/recent-personal.md` |

## Folders

| Folder | Holds |
|---|---|
| `work-projects/` | Co-op projects, numbered separately |
| `personal-projects/` | Robin's own projects, numbered separately |
| `memory/` | Projects index, recent sessions, archive, learning log, glossary, people, flags, heartbeat |
| `context/` | Reference material: the co-op's bid boilerplate, data policy, brand notes |
| `reports/` | Output from scheduled tasks |
| `working/` | Temporary inbox |

## Tools and connections

| Tool | How the assistant reaches it | Notes |
|---|---|---|
| Calendar | Google Calendar connector | Work and personal are separate calendars; check both on work days, as board events sit in the personal one |
| Email | Not connected | Robin forwards anything relevant into the conversation |
| Newsletter platform | Its API, via curl | Only for reading subscriber counts; never for sending |

## Credentials (names only)

| Name | Used for | Kept in |
|---|---|---|
| `NEWSLETTER_API_KEY` | Reading newsletter subscriber counts | macOS Keychain, service "coppice-newsletter" |

## Scheduled tasks

| Task | When | Writes to |
|---|---|---|
| morning-briefing | Mon–Thu 07:45 | the conversation, `memory/flags.md`, heartbeat |
| weekly-review | Friday 16:00 | the conversation, heartbeat |
| archive-trim | weekly, Monday 07:30 | `memory/archive/`, heartbeat |
| doctor | weekly, Monday 07:40 | `reports/doctor-YYYY-MM-DD.md`, heartbeat |

## Other assistants

None. One assistant works in this folder.

## Budgets

```yaml
budgets:
  startup_tokens: 8000
  tasks_kb: 15
  recent_days: 21
  learning_log_kb: 12
  reports_days: 60
  stale_flag_days: 5
project_roots:
  - work-projects
  - personal-projects
ignore:
  # - "*/saved-pages/*"
root_allowed:
  - START-HERE.md
  - AGENTS.md
  - CLAUDE.md
  - soul.md
  - setup.md
  - TASKS*.md
  - README.md
```

---

*Last updated: 2026-09-15 — added the newsletter API*
