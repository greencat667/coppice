# Example workspace — Robin Arden (fictional)

A filled-in [Coppice](https://github.com/greencat667/coppice) workspace, as it might look two weeks after setup. **Robin, Hollowbrook Community Energy and everyone else here are invented.** It exists to show what the templates look like in use.

Worth looking at:

- **`soul.md`** — a profile about one page long, with no tool details in it.
- **`setup.md`** — two contexts (work Mon–Thu, personal Fri–Sun) and two separately numbered project folders.
- **`TASKS-work.md`** — current state only; the history is in each project's `log.md`.
- **`memory/flags.md`** — one item that has escalated to rung 2, so the briefing now proposes an action rather than repeating the flag.
- **`memory/learning-log.md`** — two live experiments; the settled one has moved to the archive.
- **`work-projects/002 - Member Survey 2026/status-board.md`** — a fast-moving project with its current state on one page.

Run the health check on it from the repository root:

```bash
python3 scripts/doctor.py --workspace examples/workspace --today 2026-09-28
```
