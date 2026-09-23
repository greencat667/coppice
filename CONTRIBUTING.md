# Contributing to Coppice

Thanks for your interest in improving this.

**This repo is not actively maintained.** It was published as a one-time release, not something
I'm committed to reviewing or updating on an ongoing basis. Issues and PRs may sit unanswered for
a long time, or indefinitely. If you need changes, forking is likely faster than waiting on a
response here.

## What's most useful

- A rule you've found that belongs in `docs/rules.md`, with the failure that produced it
- A check that could move a rule from "kept by memory" to "kept by `doctor.py`"
- False alarms or misses from running `doctor.py` against a real workspace, as a failing test case
- Newcomer-test findings (see `docs/testing.md`)
- Setup notes for assistants other than Claude

## How to contribute

1. Fork the repository
2. Create a branch (`git checkout -b improvement/your-change`)
3. Make your changes
4. Open a pull request with a clear description of what you changed and why

## What to avoid

- Anything from a real workspace: no real names, notes, logs or credentials, even in test fixtures. Build fake secrets at runtime, as the existing tests do.
- New dependencies for the scripts. Standard library only, Python 3.9+.
- Growing the startup read. If a change adds to what's read every session, it needs a very good reason.

## Questions?

Open an issue if you like, but see the note above — don't expect a quick reply.
