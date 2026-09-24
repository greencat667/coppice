"""Regenerates examples/workspace, the fictional filled-in workspace, from workspace/ plus the content below.

Run from the repository root:  python3 scripts/make_example.py
"""
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
W = REPO / "examples" / "workspace"
if W.exists():
    shutil.rmtree(W)
shutil.copytree(REPO / "workspace", W)
for p in ["TASKS.md", "memory/recent.md"]:
    (W / p).unlink()
shutil.rmtree(W / "projects")


def w(path, text):
    p = W / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.lstrip("\n"), encoding="utf-8")


w("README.md", """
# Example workspace — Robin Arden (fictional)

A filled-in [Coppice](https://github.com/greencat667/coppice) workspace, as it might look two weeks after setup. **Robin, Hollowbrook Community Energy and everyone else here are invented.** It exists to show what the templates look like in use.

Worth looking at:

- **`soul.md`** — a profile about one page long, with no tool details in it.
- **`setup.md`** — two contexts (work Mon–Thu, personal Fri–Sun) and two separately numbered project folders.
- **`TASKS-work.md`** — current state only; the history is in each project's `log.md`.
- **`memory/flags.md`** — one item that has escalated to rung 2, so the briefing now proposes an action rather than repeating the flag.
- **`memory/learning-log.md`** — two live experiments; the settled one has moved to the archive.
- **`work-projects/002-member-survey-2026/status-board.md`** — a fast-moving project with its current state on one page.

Run the health check on it from the repository root:

```bash
python3 scripts/doctor.py --workspace examples/workspace --today 2026-09-28
```
""")

w("soul.md", """
# Soul — Robin Arden

> A briefing about Robin, the person being helped. Not a persona to adopt. Robin owns this file: suggest changes, don't make them.

---

## Who I am

- **Name:** Robin (they/them)
- **Role:** Programme coordinator at Hollowbrook Community Energy, a small member-owned co-op that puts solar on community buildings
- **What I'm responsible for:** our funding bids, member engagement, and keeping the volunteer installers' diary sane

## How I think and work

I start from the people involved and work out to the plan. If I don't know who a thing is for, I can't write it. I work in 45-minute blocks with a break, and I'm at my best before lunch.

I'm good at the relationships and the pitch. I'm slow at the admin around them: budgets, forms, chasing. That's where I want the most help.

### My rhythm

| When | What it's for | Notes |
|---|---|---|
| Mon–Thu | Co-op work | Mondays are for planning; the board meets on the first Thursday of the month |
| Fri–Sun | My own projects | Friday mornings are for the woodworking course; weekends are family time |

- The board papers go out the Monday before the board meeting, and I always start them too late. Flag them on the Wednesday before.
- I say yes to volunteer requests in the moment and then run out of week. If I'm about to commit to something new, ask what it replaces.

### Friction points

- **Starting the admin.** Once I've started, I'm fine. If I'm avoiding something, give me the smallest first step, not a pep talk.
- **Evenings.** I check email at night and then can't switch off. If I'm working after 8pm, say so once, briefly.

## How I like to be communicated with

- **Tone:** plain and warm. No exclamation marks, no "Great question".
- **Format:** short paragraphs or bullets; a table when comparing options.
- **Detail:** the answer first, then the reasoning if I ask.
- **Direction:** tell me what you'd do. I'll push back if I disagree.
- **Accountability:** if I said I'd do something by a date, remind me of the date, not just the task.

## What I care about

- Energy that's owned by the people who use it
- Members and volunteers being asked, not told
- Honest numbers in bids, even when rounder ones would look better
- Not burning out the few people who do most of the work

## Standing commitments

- Anything that goes to members, funders or the press gets read by me before it goes out.
- The co-op's data policy: no member personal data in documents shared outside the co-op, and never in an AI tool beyond first names.

## What good help looks like

- End with one concrete next step.
- Surface anything that's been waiting on someone else for more than a week.
- Give me a rough first draft early rather than a polished one late.

---

*Last updated: 2026-09-19 — added the evening-work note*
""")

w("setup.md", """
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
""")

w("TASKS-work.md", """
# Tasks — work

> Current state only. History is in each project's `log.md`.

## 🔴 Now

- **Solar for Schools bid** — case for support drafted (v2); the budget table still has placeholder installer costs. **Next:** get Marcus's revised quote for the second school roof, then finish the budget (bid due Fri 9 Oct). → [`log.md`](work-projects/001-solar-for-schools-bid/log.md)
- **Board papers for Thu 1 Oct** — agenda agreed with Dana. **Next:** draft the bid-update and survey-update items by Mon 28 Sept; papers go out Tue 29 Sept.

## 🟡 Soon

- **Member Survey 2026** — survey live, 212 responses so far. **Next:** reminder email to members who haven't opened it, Thu 1 Oct. → [`status-board.md`](work-projects/002-member-survey-2026/status-board.md)
- **Volunteer installer rota, October** — three gaps. **Next:** post the gaps in the volunteers' group on Mon 28 Sept. → [`rota`](working/volunteer-rota-october.md)

## 🟢 Waiting on someone

- **Revised quote, school roof 2** — waiting on Marcus since 17 Sept. **Next:** phone him before 9am on Mon 28 Sept (see `memory/flags.md`).
- **Village hall lease clause** — waiting on the hall committee since 22 Sept. **Next:** raise it at their meeting on Tue 6 Oct.

## Trackers

- **Co-op budget, Q3** — on track; £1,240 under on volunteer expenses. **Next check:** Wed 30 Sept.
- **Newsletter subscribers** — 1,318 (up 41 since the open day). **Next check:** Mon 12 Oct.
""")

w("TASKS-personal.md", """
# Tasks — personal

> Current state only.

## 🔴 Now

- **Oak bench** — legs cut and dry-fitted; one tenon too loose. **Next:** glue and wedge the loose tenon at Friday's class. → [`log.md`](personal-projects/001-oak-bench/log.md)

## 🟡 Soon

- **Family recipe book** — 14 recipes collected, six with photos. **Next:** ask Gran for the two missing measurements on Sunday's call. → [`log.md`](personal-projects/002-family-recipe-book/log.md)
- **Book the van MOT** — due Tue 20 Oct. **Next:** book online by Sat 10 Oct.

## Trackers

- **Running** — three runs a week, 5k in about 29 minutes. **Next check:** end of October.
""")

w("memory/recent-work.md", """
# Recent sessions — work

> Newest first. Last 21 days; older entries move to `memory/archive/`.

## 2026-09-24 — Case for support, v2

- Rewrote the case for support around the two schools' own words from the site visits, instead of the co-op's.
- Budget table left with placeholder installer costs until Marcus's revised quote arrives.
- Decision: bid for two schools, not three. The third roof needs structural work we can't cost in time. Logged in 001.

## 2026-09-22 — Survey progress and board agenda

- Member Survey at 187 responses; members under 35 still only 9% of responses. Added a reminder plan to the status board.
- Agreed the 1 Oct board agenda with Dana by phone.

## 2026-09-17 — Bid kickoff

- Created 001 Solar for Schools Bid. Brief agreed: two primary schools, £38k, deadline 9 Oct.
- Asked Marcus for a revised quote for the second school's roof.

## 2026-09-14 — Open day wrap-up

- Closed 003 Heat Pump Open Day: 64 visitors, 41 new newsletter sign-ups. Summary in its `outputs/`.
- First session with the new workspace. Moved the open-day notes from a loose document into the project log.
""")

w("memory/recent-personal.md", """
# Recent sessions — personal

> Newest first. Last 21 days.

## 2026-09-20 — Bench joinery plan

- Worked out the order for the remaining joints, so the loose tenon gets fixed before the seat goes on.
- Decided on wedged through-tenons rather than a new leg.

## 2026-09-13 — Recipe book structure

- Grouped the 14 recipes into four sections by occasion, not by course. It matched how the family actually talks about them.
""")

w("memory/projects.md", """
# Projects

> A lean index. Detail lives in each project's `index.md` and `log.md`.
>
> **Next project number (work-projects): 004**
> **Next project number (personal-projects): 003**

## Active

| # | Project | Tier | Status | Folder | Goal | Next |
|---|---|---|---|---|---|---|
| 001 | Solar for Schools Bid | Project | Active | `work-projects/001-solar-for-schools-bid/` | £38k for solar on two primary schools; deadline 9 Oct | Finish the budget once the revised quote arrives |
| 002 | Member Survey 2026 | Project | Active | `work-projects/002-member-survey-2026/` | 300+ responses and a findings paper for the AGM | Reminder email, 1 Oct |
| 001 | Oak Bench | Project | Active | `personal-projects/001-oak-bench/` | A garden bench from the woodworking course | Fix the loose tenon |
| 002 | Family Recipe Book | Project | Active | `personal-projects/002-family-recipe-book/` | A printed book of family recipes for December | Missing measurements from Gran |

## Light

| Item | File | Next |
|---|---|---|
| October volunteer rota | `working/volunteer-rota-october.md` | Fill three gaps |

## Paused or waiting

| # | Project | Why paused | Revisit |
|---|---|---|---|

## Closed

| # | Project | Closed | Outcome |
|---|---|---|---|
| 003 | Heat Pump Open Day | 2026-09-14 | 64 visitors, 41 sign-ups — `work-projects/003-heat-pump-open-day/` |
""")

w("memory/learning-log.md", """
# Learning log

> Active entries only. Graduated and discarded entries are in `memory/archive/learning-log-archive.md`.

## Active

### 2026-09-17 — Ask "who is this for?" before drafting [trying — nearing confirm]

**Observation:** Twice now (the case for support and the survey invite), Robin rewrote the first draft around a specific reader. Drafts that start from the reader need fewer rounds.
**Adjustment to test:** before any draft for an outside reader, ask one question: *who exactly is reading this, and what do they already believe?*
**Evidence so far:** 17 Sept (case for support: rewritten); 22 Sept (survey reminder: first draft accepted after asking).
**Graduates to:** `soul.md`, under "How I think and work", as a proposal.

### 2026-09-22 — Write deadlines as dates, not days [trying]

**Observation:** "Due Friday" in the tasks file was ambiguous across two sessions a week apart.
**Adjustment to test:** always write deadlines as dates, e.g. "Fri 9 Oct".
**Evidence so far:** 22 Sept.
**Graduates to:** `START-HERE.md`, if it holds.
""")

w("memory/archive/learning-log-archive.md", """
# Learning log — archive

Graduated and discarded entries, with their verdicts.

### 2026-09-14 — Flag board papers on the Wednesday before [graduated → soul.md 2026-09-19]

**Observation:** Board papers were started the day before they were due, two months running.
**Verdict:** Confirmed. Added to `soul.md` under "My rhythm".
""")

w("memory/archive/2026-08.md", """
# Archive — 2026-08

## 2026-08-27 — Open day logistics

- Confirmed the village hall for 13 Sept and two heat-pump demo units.
""")

w("memory/glossary.md", """
# Glossary

| Term | Means | Notes |
|---|---|---|
| HCE | Hollowbrook Community Energy | The co-op |
| PV | Photovoltaic (solar panels) | |
| SEG | Smart Export Guarantee | Payment for electricity exported to the grid |
| The board | HCE's volunteer board of directors | Meets the first Thursday of the month; the chair is Dana |
| Install days | Volunteer installation Saturdays | Rota in `working/volunteer-rota-october.md` |
""")

w("memory/people/dana-whitlock.md", """
# Dana Whitlock (fictional)

- **Role:** Chair of the HCE board (volunteer)
- **Relationship:** Robin reports to the board through Dana
- **Working with them:** prefers a phone call to email for anything contentious; wants board papers a full week ahead
- **Current threads:** board papers for 1 Oct; the bid's match-funding question

*Last updated: 2026-09-22*
""")

w("memory/people/marcus-ibe.md", """
# Marcus Ibe (fictional)

- **Role:** Director of the installer HCE uses for anything volunteers can't do
- **Relationship:** supplier and long-standing ally
- **Working with them:** slow on email, quick on the phone; best reached before 9am
- **Current threads:** revised quote for school roof 2 (work project 001)

*Last updated: 2026-09-17*
""")

w("memory/flags.md", """
# Flags

> Written by the morning briefing. Rungs: 1 = flag · 2 = propose one unsticking action · 3 = ask whether to park or drop. An item moves up a rung after 5 briefings in a row at its current rung.

| Item | First flagged | Last flagged | Times at this rung | Rung | Note |
|---|---|---|---|---|---|
| Revised quote, school roof 2 (001) | 2026-09-21 | 2026-09-28 | 1 | 2 | Suggested: phone Marcus before 9am rather than another email |
""")

w("memory/heartbeat.md", """
# Heartbeat

> One line per scheduled-task run. Last 60 days.

| When | Task | Result | Note |
|---|---|---|---|
| 2026-09-14 | archive-trim | skipped | nothing to trim |
| 2026-09-14 | doctor | ran | 0 errors, 1 warnings, 0 fixes |
| 2026-09-15 | morning-briefing | ran | 1 flags, top: open-day summary |
| 2026-09-18 | weekly-review | ran | 0 stuck, 1 learning-log proposals |
| 2026-09-21 | archive-trim | ran | 1 change(s) |
| 2026-09-21 | doctor | ran | 0 errors, 0 warnings, 1 fixes |
| 2026-09-21 | morning-briefing | ran | 2 flags, top: revised quote |
| 2026-09-24 | morning-briefing | ran | 2 flags, top: revised quote |
| 2026-09-25 | weekly-review | ran | 1 stuck, 1 learning-log proposals |
| 2026-09-28 | archive-trim | skipped | nothing to trim |
| 2026-09-28 | doctor | ran | 0 errors, 0 warnings, 0 fixes |
| 2026-09-28 | morning-briefing | ran | 3 flags, top: revised quote (rung 2) |
""")

w("reports/doctor-2026-09-28.md", """
# Coppice doctor — 2026-09-28

**All clear.** Nothing to fix.
""")

w("working/volunteer-rota-october.md", """
# Volunteer rota — October (Light)

**Objective:** a full install-day rota for October. **Approach:** post the gaps to the group, confirm by phone. **Done when:** no gaps.

| Date | Site | Lead | Crew | Gap? |
|---|---|---|---|---|
| Sat 3 Oct | Scout hut | Ali | 3 | — |
| Sat 10 Oct | Chapel | — | 2 | Lead needed |
| Sat 17 Oct | Allotment shed | Jess | 1 | Two crew needed |
| Sat 24 Oct | — | — | — | Site not yet chosen |
""")


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def project(root, num, name, desc, status, started, goal, nxt, brief, log, extra=None):
    base = f"{root}/{num}-{slug(name)}"
    has_board = bool(extra and "status-board.md" in extra)
    w(f"{base}/index.md", f"""
# {num} — {name}

*{desc}*

**Status:** {status} · **Tier:** Project · **Started:** {started}
**Goal:** {goal}
**Next:** {nxt}

## Key files

- `log.md` — the full history, append-only
- `brief/brief.md` — objective, approach, success criteria
""" + ("- `status-board.md` — current state at a glance\n" if has_board else "") + """
## Folders

- `brief/` · `inputs/` · `working/` · `outputs/`
""")
    w(f"{base}/brief/brief.md", f"""
# Brief — {name}

**Objective:** {brief[0]}
**Approach:** {brief[1]}
**Success looks like:** {brief[2]}
""")
    body = f"# {num} — {name}: log\n\n> Append-only. Newest at the bottom.\n"
    for d, title, items in log:
        body += f"\n## {d} — {title}\n\n" + "".join(f"- {i}\n" for i in items)
    w(f"{base}/log.md", body)
    for fn, txt in (extra or {}).items():
        w(f"{base}/{fn}", txt)
    for sub in ("inputs", "working", "outputs"):
        d = W / base / sub
        d.mkdir(parents=True, exist_ok=True)
        if not any(d.iterdir()):
            (d / ".gitkeep").write_text("")


project("work-projects", "001", "Solar for Schools Bid", "A bid to put solar panels on two local primary schools",
        "Active", "2026-09-17", "£38k from a community energy fund for solar on two primary schools; deadline Fri 9 Oct",
        "Finish the budget once Marcus sends the revised quote",
        ("Win funding for solar on two primary schools, written for a funder who backs community-led projects",
         "Build the case from the schools' own words; cost it honestly; get the board to agree match funding on 1 Oct",
         "Submitted by 9 Oct, with a budget we can defend line by line"),
        [("2026-09-17", "Project created", ["Two schools approached us after the open day; the fund's deadline is 9 Oct.",
                                            "Asked Marcus for a revised quote for the second school's roof."]),
         ("2026-09-24", "Case for support v2", ["Rewrote the case around what the head teachers said at the site visits, not what the co-op wants.",
                                                "Decided to bid for two schools, not three: the third roof needs structural work we can't cost in time. Told the third school directly.",
                                                "The budget table has placeholder installer costs until the revised quote arrives."])],
        extra={"working/case-for-support-v2.md": "# Case for support — v2 (draft)\n\n*Draft. Placeholder figures are marked [TBC].*\n\nTwo primary schools in Hollowbrook asked us to help them generate their own electricity…\n"})

project("work-projects", "002", "Member Survey 2026", "The co-op's annual survey of its members, reported at the AGM",
        "Active", "2026-09-08", "300+ responses and a short findings paper for the AGM in November",
        "Reminder email to members who haven't opened it, Thu 1 Oct",
        ("Hear from members what they want the co-op to do next, including the ones we rarely hear from",
         "A short online survey, a paper option at install days, two reminders",
         "300+ responses, at least 15% from members under 35, and a paper the board can act on"),
        [("2026-09-08", "Project created", ["Drafted from last year's survey, cut from 24 questions to 12."]),
         ("2026-09-15", "Survey live", ["Sent to 1,190 members by email; paper copies at the open day."]),
         ("2026-09-22", "Progress check", ["187 responses; members under 35 only 9% of responses so far.",
                                           "Decided: a second reminder aimed at younger members, written with two of them."])],
        extra={"status-board.md": """# 002 — Member Survey 2026: status board

> Overwritten as things change. History is in `log.md`.

| Item | State | Next | Updated |
|---|---|---|---|
| Responses | 212 of a 300 target | Reminder, Thu 1 Oct | 2026-09-24 |
| Under-35s | 9% of responses (target 15%) | Draft the second reminder with two younger members | 2026-09-24 |
| Paper copies | 23 returned | Enter them by Mon 5 Oct | 2026-09-22 |
| Findings paper | Not started | Outline once responses close, Tue 20 Oct | 2026-09-22 |
"""})

project("work-projects", "003", "Heat Pump Open Day", "A public open day about heat pumps at the village hall",
        "Closed ✅ (2026-09-14)", "2026-08-20", "A well-attended open day that grows the newsletter list", "None — closed",
        ("Show local households what a heat pump looks and sounds like, and what it costs",
         "Two demo units, three short talks, installers on hand for questions",
         "50+ visitors and 25+ new newsletter sign-ups"),
        [("2026-08-20", "Project created", ["Village hall booked for 13 Sept."]),
         ("2026-09-14", "Closed", ["64 visitors, 41 new sign-ups: both targets beaten.",
                                   "Two primary schools asked about solar afterwards, which became work project 001."])],
        extra={"outputs/open-day-summary.md": "# Heat Pump Open Day — summary\n\n64 visitors, 41 newsletter sign-ups, two follow-up enquiries from schools.\n"})

project("personal-projects", "001", "Oak Bench", "A garden bench made on the Friday woodworking course",
        "Active", "2026-09-04", "A two-seater oak garden bench, finished by the end of term",
        "Glue and wedge the loose tenon at Friday's class",
        ("Make a bench solid enough to outlast me", "Mortise and tenon joints throughout, no screws",
         "It doesn't wobble, and I'd happily sit on it"),
        [("2026-09-04", "Project created", ["Timber bought; cutting list drawn up with the tutor."]),
         ("2026-09-20", "Joinery plan", ["One tenon was cut too loose. Decided on wedged through-tenons rather than making a new leg."])])

project("personal-projects", "002", "Family Recipe Book", "A printed book of the family's recipes",
        "Active", "2026-09-06", "A printed book of about 20 family recipes, ready to give in December",
        "Ask Gran for the two missing measurements on Sunday",
        ("Keep the family recipes in one place, in the words of the people who cook them",
         "Collect by phone and photo; group by occasion; print a small run",
         "Twenty recipes, one photo each, printed by Sat 12 Dec"),
        [("2026-09-06", "Project created", ["Asked the family for recipes."]),
         ("2026-09-13", "Structure", ["14 recipes in. Grouped by occasion, not course, because that's how the family talks about them."])])

print("example written")
