# coppice doctor

A health check for a Coppice workspace. It checks every rule in [`rules.md`](rules.md) that can be checked mechanically, reports what it finds, and with `--fix` repairs only the mechanical problems. Everything that needs judgement is left to you.

It's one Python file using only the standard library (Python 3.9+). The setup copies it to `context/coppice/doctor.py` in your workspace.

```bash
python3 context/coppice/doctor.py                  # check this workspace
python3 context/coppice/doctor.py --fix            # also apply safe fixes
python3 context/coppice/doctor.py --report reports/doctor-2026-09-28.md --heartbeat
python3 context/coppice/doctor.py --json           # machine-readable output
```

The exit code is `1` if any error was found, `0` otherwise, so it can gate other scripts.

## What it checks

| Check | Severity | Rule | `--fix` |
|---|---|---|---|
| `START-HERE.md`, `soul.md` and `setup.md` exist | error | 1 | — |
| Each context's tasks and recent files exist | error | 1 | — |
| Startup read is within `budgets.startup_tokens` | error | 1 | — |
| Tasks files are within `budgets.tasks_kb` | error | 5 | — |
| Tasks files contain dated "✅" history lines | warn | 5 | — |
| Recent-sessions entries are within `budgets.recent_days` | warn | 6 | Moves old entries to `memory/archive/YYYY-MM.md` |
| Learning log is within `budgets.learning_log_kb` | warn | 24 | — |
| Only `root_allowed` files are in the workspace root | warn | 9 | — |
| Nothing has sat in `working/` for more than 7 days | warn | 10 | — |
| Every project folder has a `log.md` | error | 11 | Adds a stub log |
| Project folders and `memory/projects.md` agree | warn | 14 | — |
| No two project folders share a number | warn | 7 | — |
| The next-project-number line is ahead of every existing project | error | 7, 14 | Corrects the number |
| Active projects have had a log entry in the last 30 days | note | 11 | — |
| Markdown links inside the workspace resolve | warn | 7 | — |
| No credentials in any text file | error | 15 | — |
| Every scheduled task in `setup.md` has a recent heartbeat, and its last run didn't fail | warn | 21 | — |
| Generated reports aren't written into `memory/` | warn | 25 | — |
| Reports older than `budgets.reports_days` | note | 25 | — (`archive-trim` deletes them) |
| `soul.md` and `setup.md` were updated in the last 180 days | note | 16 | — |

## What it skips, and why

These exclusions come from running the doctor against a real workspace that had been in daily use for eight months. The first run produced hundreds of false alarms.

- **Code projects** (any folder with a `.git`, `package.json`, `pyproject.toml`, `CMakeLists.txt` and so on) aren't workspace notes. Their links aren't checked, and any possible secrets inside them are summarised as one note per project rather than dozens of errors, because they're usually test fixtures.
- **Captured sources** (`inputs/`, `raw/`, `archive/`, `snapshots/`, and folders starting with `_`) hold saved web pages and old material whose links point at the original site. Their links aren't checked. They are still scanned for secrets, because saved pages and session captures do sometimes contain live tokens.
- **Anything you list under `ignore:`** in the budgets block of `setup.md` is skipped entirely, e.g. `"*/saved-pages/*"`.
- **Wiki-style links** without a `.md` extension resolve if the `.md` file exists.

## How secret detection works

The doctor looks for well-known token formats (GitHub, Anthropic, OpenAI-style, Slack, AWS, Google, private keys) and for assignments such as `api_key: …` or `token = …` with a long mixed-character value. Values that look like placeholders (`YOUR_API_KEY`, `[your token]`, `xxxx`) are ignored.

It never prints a value in full: the report shows the first four characters and the length. If you've knowingly left a credential in a file for now, list that file under `secrets_accepted:` in `setup.md`. Its findings then become a single reminder note instead of errors on every run. Any new secret anywhere else is still an error. It will miss some secrets and occasionally flag something harmless, so treat it as a smoke alarm, not a guarantee.

## Several project folders

If you number work and personal projects separately, list both folders under `project_roots:` in `setup.md` and keep one next-number line per folder in `memory/projects.md`:

```
Next project number (work-projects): 012
Next project number (personal-projects): 031
```

## Tests

```bash
python3 -m unittest discover tests
```

The suite builds fresh copies of the starter workspace, breaks them in specific ways, and checks that the doctor catches each problem. It also checks that the starter workspace itself comes back clean, and includes cases for the false alarms found in real use.
