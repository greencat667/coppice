# How Coppice was tested

Two kinds of testing: automated tests for the scripts, and a newcomer test for everything else.

## Automated

`python3 -m unittest discover tests` runs on every push, on Python 3.9 and 3.12. The tests:

- build fresh copies of the starter workspace, break each one in a specific way, and check that `doctor.py` catches the problem and `--fix` repairs only what it should
- check that the starter workspace and the example workspace both come back clean
- check that `trim.py` moves and deletes exactly what it says it will, that `--dry-run` changes nothing, and that a second run finds nothing to do
- include a regression case for each false alarm found when the doctor was run against a real workspace in daily use for eight months, and for each bug found in the newcomer test below

To make sure the tests aren't passing by accident, each main check was switched off in turn and the suite confirmed to fail.

## The newcomer test

A fresh assistant session with no prior context was given only the repository and a fictional newcomer to play. It was asked to find where someone new would get stuck, and to report rather than fix. The newcomer, "Alex", a freelancer with a mixed week, threw three curveballs:

1. **Pasted an API key during setup.** The pass condition: the key ends up in no file.
2. **Wasn't sure whether part of their week was a separate context.**
3. **Declined the morning briefing,** wanting only the trim and health check.

The session then compressed a week of use:

- created a project, and something that should stay a plain task
- ran the end-of-session routine
- faked the passage of time with stale entries, a stray root file and a project with no log
- ran the trim and the doctor
- ran the briefing on consecutive days to check that flags escalate
- ran the weekly review

Finally it built a deliberately messy existing setup and ran adopt mode against it.

### What it found

- **Level 0 alone: yes.** Level 2 worked mechanically too. The pasted key was never written to a file, the trim and doctor behaved exactly as documented, and flags escalated on schedule.
- **One blocker:** the doctor's secret scanner missed credentials named in snake_case (`trello_token = …`), because a word boundary in its pattern treated the underscore as part of the word. That's one of the most common ways secrets are written down. **Fixed**, with six regression cases.
- **Three confusing points, all fixed:**
  - no default for someone unsure about contexts (now: use one; it's cheaper to split than to merge)
  - a two-part interview question (now split, with "not sure" explicitly fine)
  - a declined scheduled task could still run (every template now starts with a check that it's listed in `setup.md`)
- **Eight minor points, all fixed:**
  - the doctor warned about its own missing heartbeat on its first run
  - an unused status board was left in every new project
  - interview questions that assumed an employer, or asked people to write a policy from scratch (it now proposes a default)
  - no "nothing to flag" case in the briefing
  - escalation wording that said "days" where it meant "consecutive briefings"
  - the weekly review couldn't see unindexed projects
  - two gaps in adopt mode: a setup with no start-here file, and a tasks file that's entirely history

## Dogfooding

Coppice was then used to adopt the long-lived workspace it grew out of. Adopt mode's read-only survey and a doctor run against about 900 project and note files found real problems the workspace's own conventions had missed:

- a prompt-driven archive task that had reported success for three weeks while archiving nothing
- a next-project-number line that had fallen five projects behind

The run also found five things to improve in the doctor itself, now fixed and tested:

- **Accepted risks.** Files where someone has knowingly left a credential for now can be listed under `secrets_accepted`. They're reported as one reminder instead of errors every week.
- **Large files.** Log and data files over 1 MB are skipped by the line-by-line scans (with a note), after a 7 MB file made the check crawl.
- **Start file name.** `START HERE.md` (with a space) is accepted as the start file.
- **Placeholder links.** Link targets such as `(URL)` or `(link)` in drafts are ignored.
- **Next-number lines named with a word.** A line like "Next client project number: 012" is matched to the root whose name contains that word.

### What to re-test after changes

After changes to a skill or scheduled task, re-run the newcomer test with a different newcomer and fresh curveballs. A test that's passed once starts to shape the thing it tests.
