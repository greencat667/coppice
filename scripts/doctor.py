#!/usr/bin/env python3
"""coppice doctor: a health check for a Coppice workspace.

Checks the rules in docs/rules.md that can be checked mechanically, reports
what it finds, and (with --fix) repairs only the mechanical problems.

    python3 doctor.py                         # check the current folder
    python3 doctor.py --workspace ~/Work      # check another folder
    python3 doctor.py --fix                   # also apply safe, mechanical fixes
    python3 doctor.py --report reports/doctor-2026-09-23.md --heartbeat

Exit code 1 if any error was found, 0 otherwise. Standard library only.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import sys
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_BUDGETS = {
    "startup_tokens": 8000,
    "tasks_kb": 15,
    "recent_days": 21,
    "learning_log_kb": 12,
    "reports_days": 60,
    "stale_flag_days": 5,
}
DEFAULT_ROOT_ALLOWED = ["START-HERE.md", "AGENTS.md", "CLAUDE.md", "soul.md", "setup.md", "TASKS*.md", "README.md"]
REQUIRED_FILES = ["START-HERE.md", "soul.md", "setup.md"]
START_NAMES = ["START-HERE.md", "START HERE.md", "START_HERE.md"]   # older workspaces often use a space
PLACEHOLDER_TARGETS = {"url", "link", "href", "path", "source", "citation", "todo", "tbc", "..."}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".obsidian", ".venv", "venv", "site-packages", "dist", "build"}
# A folder with any of these is someone's code project: its links and fixtures aren't workspace notes.
CODE_MARKERS = (".git", "package.json", "pyproject.toml", "setup.py", "requirements.txt", "Cargo.toml", "go.mod",
                "CMakeLists.txt", "Makefile", "Gemfile", "pom.xml", "build.gradle")
# Captured or archived material: links in it point at the original source, so they aren't checked.
NOT_OWNED_DIRS = {"inputs", "raw", "archive", "snapshots"}
TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".csv", ".html", ".js", ".py", ".sh", ".ics"}
HEARTBEAT_NAME = "doctor"   # the name this script records in memory/heartbeat.md; matches setup.md's Scheduled tasks table
WORKING_MAX_DAYS = 7
LOG_STALE_DAYS = 30
MAX_SCAN_BYTES = 1_000_000   # text files bigger than this are logs or data dumps, not notes: not scanned line by line
LAST_UPDATED_STALE_DAYS = 180

# Credential patterns. Values are never printed in full.
SECRET_PATTERNS = [
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI-style API key", re.compile(r"\bsk-(?!ant-)(?:proj-)?[A-Za-z0-9_\-]{32,}")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b")),
    ("Private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    # The keyword may be joined to a name by "_" or "-" (TRELLO_TOKEN, db-password, api_key_v2), so the boundary is
    # "not a letter" rather than \b, which treats "_" as part of the word and missed snake_case names entirely.
    ("Credential assignment", re.compile(
        r"(?i)(?<![A-Za-z])(?:api[_ -]?key|api[_ -]?token|access[_ -]?token|auth[_ -]?token|client[_ -]?secret|secret|"
        r"password|passwd|pwd|token)(?:[_-][A-Za-z0-9_]*)?[\"'`]?\s*[:=]\s*[\"'`]?"
        r"(?P<value>[A-Za-z0-9_\-\.\/+]{16,})")),
]
PLACEHOLDER_HINT = re.compile(r"(?i)(example|placeholder|your[_-]|xxxx|<|\[|\.\.\.|changeme|redacted)")


@dataclass
class Finding:
    severity: str  # "error" | "warn" | "info"
    check: str
    message: str
    path: str = ""


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    fixes: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def add(self, severity, check, message, path=""):
        self.findings.append(Finding(severity, check, message, str(path)))

    def count(self, severity):
        return sum(1 for f in self.findings if f.severity == severity)


# ---------------------------------------------------------------- parsing helpers

def read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def est_tokens(text: str) -> int:
    # Rough and deliberately conservative: about four characters per token for English prose.
    return round(len(text) / 4)


def section(text: str, heading: str) -> str:
    """Return the body of a '## heading' section (up to the next ## heading)."""
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def first_table(text: str) -> list[list[str]]:
    """Rows of the first markdown table in text, header row first, separator dropped."""
    rows, started = [], False
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("|") and s.endswith("|"):
            started = True
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                continue
            rows.append(cells)
        elif started:
            break
    return rows



def strip_code(cell: str) -> str:
    return cell.strip().strip("`").strip()


def parse_budgets(setup_text: str):
    """Parse the ```yaml budgets block in setup.md without needing PyYAML."""
    budgets, root_allowed = dict(DEFAULT_BUDGETS), list(DEFAULT_ROOT_ALLOWED)
    m = re.search(r"```ya?ml\s*\n(.*?)```", setup_text, re.S)
    if not m:
        budgets["project_roots"], budgets["ignore"], budgets["secrets_accepted"] = ["projects"], [], []
        return budgets, root_allowed, False
    block, current = m.group(1), None
    found_allowed, found_roots, found_ignore, found_accepted = [], [], [], []
    for raw in block.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not raw.startswith((" ", "\t")):
            current = line.strip().rstrip(":")
            continue
        s = line.strip()
        if current == "budgets" and ":" in s:
            k, v = [x.strip() for x in s.split(":", 1)]
            try:
                budgets[k] = int(v)
            except ValueError:
                pass
        elif current == "root_allowed" and s.startswith("-"):
            found_allowed.append(s[1:].strip().strip("'\""))
        elif current == "project_roots" and s.startswith("-"):
            found_roots.append(s[1:].strip().strip("'\"").rstrip("/"))
        elif current == "ignore" and s.startswith("-"):
            found_ignore.append(s[1:].strip().strip("'\""))
        elif current == "secrets_accepted" and s.startswith("-"):
            found_accepted.append(s[1:].strip().strip("'\""))
    budgets["project_roots"] = found_roots or ["projects"]
    budgets["ignore"] = found_ignore
    budgets["secrets_accepted"] = found_accepted
    return budgets, (found_allowed or root_allowed), True


def parse_contexts(setup_text: str):
    rows = first_table(section(setup_text, "Contexts"))
    contexts = []
    for r in rows[1:]:
        if len(r) >= 4:
            contexts.append({"name": strip_code(r[0]), "when": r[1], "tasks": strip_code(r[2]), "recent": strip_code(r[3])})
    return contexts


def parse_schedule(setup_text: str):
    rows = first_table(section(setup_text, "Scheduled tasks"))
    tasks = []
    for r in rows[1:]:
        if len(r) >= 2:
            name = strip_code(r[0])
            if name.startswith("[") or not name:
                continue
            tasks.append({"name": name, "when": r[1]})
    return tasks


def allowed_gap_days(when: str):
    w = when.lower()
    if "hour" in w:
        return 1
    if "weekday" in w:
        return 4
    if "daily" in w or "every day" in w or "each day" in w:
        return 2
    if "fortnight" in w:
        return 16
    # Month and quarter before weekday names: "monthly" starts with "mon".
    if "quarter" in w:
        return 93
    if "month" in w:
        return 32
    if "week" in w or re.search(r"\b(mon|tue|wed|thu|fri|sat|sun)", w):
        return 8
    return None


DATE_HEADING = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\b.*$", re.M)


def split_dated_entries(text: str):
    """Split a recent-sessions file into (preamble, [(date, entry_text), ...])."""
    matches = list(DATE_HEADING.finditer(text))
    if not matches:
        return text, []
    pre = text[: matches[0].start()]
    entries = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        try:
            d = dt.date.fromisoformat(m.group(1))
        except ValueError:
            continue
        entries.append((d, text[m.start(): end]))
    return pre, entries


def is_code_dir(d: Path) -> bool:
    return any((d / m).exists() for m in CODE_MARKERS)


IGNORE: list[str] = []   # set from the budgets block in run()


def ignored(p: Path, root: Path) -> bool:
    r = rel(p, root).replace(os.sep, "/")
    return any(fnmatch.fnmatch(r, g) or fnmatch.fnmatch(r + "/", g) for g in IGNORE)


def iter_text_files(root: Path, owned_only: bool = False):
    """Yield (path, code_dir) for text files. code_dir is the enclosing code project, or None.

    owned_only skips code projects, captured sources and underscore folders entirely."""
    stack = [(root, None)]
    while stack:
        d, code = stack.pop()
        try:
            entries = sorted(d.iterdir())
        except OSError:
            continue
        for e in entries:
            if IGNORE and ignored(e, root):
                continue
            if e.is_dir():
                if e.name in SKIP_DIRS or e.name.startswith("."):
                    continue
                inner = code or (e if is_code_dir(e) else None)
                if owned_only and (inner or e.name in NOT_OWNED_DIRS or e.name.startswith("_")):
                    continue
                stack.append((e, inner))
            elif e.suffix.lower() in TEXT_SUFFIXES and not e.name.startswith(".env"):
                yield e, code


def rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------- checks

def start_file(ws):
    return next((n for n in START_NAMES if (ws / n).exists()), "START-HERE.md")


def check_required(ws, rep):
    for f in REQUIRED_FILES:
        if f == "START-HERE.md" and (ws / start_file(ws)).exists():
            continue
        if not (ws / f).exists():
            rep.add("error", "required-files", f"`{f}` is missing. The session protocol depends on it.", f)


def check_startup(ws, rep, budgets, contexts):
    base = sum(est_tokens(read(ws / f)) for f in [start_file(ws), "soul.md", "setup.md"])
    worst = None
    for c in contexts:
        tasks_t = est_tokens(read(ws / c["tasks"])) if (ws / c["tasks"]).exists() else 0
        recent_t = est_tokens(read(ws / c["recent"])) if (ws / c["recent"]).exists() else 0
        total = base + tasks_t + recent_t
        rep.stats.setdefault("startup_tokens", {})[c["name"]] = total
        if worst is None or total > worst[1]:
            worst = (c["name"], total)
        for key in ("tasks", "recent"):
            if not (ws / c[key]).exists():
                rep.add("error", "contexts", f"Context `{c['name']}` names `{c[key]}`, which doesn't exist.", c[key])
    if not contexts:
        rep.add("warn", "contexts", "No contexts found in the Contexts table in `setup.md`, so the startup read can't be measured.", "setup.md")
    if worst and worst[1] > budgets["startup_tokens"]:
        rep.add("error", "startup-budget",
                f"Startup read for context `{worst[0]}` is about {worst[1]:,} tokens, over the {budgets['startup_tokens']:,} budget. "
                "Trim the tasks and recent-sessions files first (rules 5 and 6).", "setup.md")


NARRATIVE = re.compile(r"✅\s*\(?\s*(?:\d{1,2}\s+\w{3,9}|\d{4}-\d{2}-\d{2})")


def check_tasks(ws, rep, budgets, contexts):
    seen = set()
    for c in contexts:
        p = ws / c["tasks"]
        if p in seen or not p.exists():
            continue
        seen.add(p)
        kb = p.stat().st_size / 1024
        if kb > budgets["tasks_kb"]:
            rep.add("error", "tasks-budget", f"`{c['tasks']}` is {kb:.1f} KB, over the {budgets['tasks_kb']} KB budget.", c["tasks"])
        hits = [i for i, line in enumerate(read(p).splitlines(), 1) if NARRATIVE.search(line)]
        if hits:
            lines = ", ".join(map(str, hits[:8])) + ("…" if len(hits) > 8 else "")
            rep.add("warn", "tasks-narrative",
                    f"`{c['tasks']}` has {len(hits)} dated \"✅\" history line(s) (lines {lines}). "
                    "History belongs in the project's `log.md` (rule 5).", c["tasks"])


def check_recent(ws, rep, budgets, contexts, today, fix):
    seen = set()
    cutoff = today - dt.timedelta(days=budgets["recent_days"])
    for c in contexts:
        p = ws / c["recent"]
        if p in seen or not p.exists():
            continue
        seen.add(p)
        text = read(p)
        pre, entries = split_dated_entries(text)
        old = [(d, e) for d, e in entries if d < cutoff]
        if not old:
            continue
        if not fix:
            rep.add("warn", "recent-window",
                    f"`{c['recent']}` has {len(old)} entr{'y' if len(old) == 1 else 'ies'} older than {budgets['recent_days']} days "
                    f"(oldest {min(d for d, _ in old)}). Run with --fix, or let `archive-trim` move them.", c["recent"])
            continue
        archive_dir = ws / "memory" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        by_month = {}
        for d, e in old:
            by_month.setdefault(f"{d:%Y-%m}", []).append(e.rstrip() + "\n")
        for month, items in sorted(by_month.items()):
            ap = archive_dir / f"{month}.md"
            existing = read(ap) if ap.exists() else f"# Archive — {month}\n\n"
            ap.write_text(existing.rstrip() + "\n\n" + "\n".join(items), encoding="utf-8")
        keep = [e for d, e in entries if d >= cutoff]
        p.write_text(pre + "".join(keep), encoding="utf-8")
        rep.fixes.append(f"Moved {len(old)} old entr{'y' if len(old) == 1 else 'ies'} from `{c['recent']}` to `memory/archive/` "
                         f"({', '.join(sorted(by_month))}).")


def check_learning_log(ws, rep, budgets):
    p = ws / "memory" / "learning-log.md"
    if p.exists():
        kb = p.stat().st_size / 1024
        if kb > budgets["learning_log_kb"]:
            rep.add("warn", "learning-log", f"`memory/learning-log.md` is {kb:.1f} KB, over the {budgets['learning_log_kb']} KB budget. "
                    "Move graduated and discarded entries to `memory/archive/learning-log-archive.md` (rule 24).", "memory/learning-log.md")


def check_root(ws, rep, root_allowed):
    stray = [p.name for p in sorted(ws.iterdir())
             if p.is_file() and not p.name.startswith(".") and not any(fnmatch.fnmatch(p.name, pat) for pat in root_allowed)]
    if stray:
        shown = ", ".join(f"`{n}`" for n in stray[:12]) + (f" and {len(stray) - 12} more" if len(stray) > 12 else "")
        rep.add("warn", "root-clutter", f"{len(stray)} file(s) in the workspace root that belong somewhere else: {shown}. "
                "File them in a project, `context/`, or `working/` (rule 9).", ".")


def check_working(ws, rep, today):
    w = ws / "working"
    if not w.is_dir():
        return
    old = []
    for p in w.rglob("*"):
        if p.is_file() and not p.name.startswith("."):
            age = (today - dt.date.fromtimestamp(p.stat().st_mtime)).days
            if age > WORKING_MAX_DAYS:
                old.append((age, rel(p, w)))
    if old:
        old.sort(reverse=True)
        shown = ", ".join(f"`{n}`" for _, n in old[:5]) + (f" and {len(old) - 5} more" if len(old) > 5 else "")
        rep.add("warn", "working-inbox", f"{len(old)} file(s) have been in `working/` for more than {WORKING_MAX_DAYS} days "
                f"(oldest {old[0][0]} days): {shown}. File them or flag them (rule 10).", "working/")


PROJECT_DIR = re.compile(r"^(\d{3,4})\s*-\s*.+")
# "Next project number: 012", "Next project number (work-projects): 012", or "Next client project number: 012",
# where a word before "project" names the root it belongs to ("client" → "client projects", "personal" → "personal-projects").
NEXT_NUMBER = re.compile(r"(?i)next\s+(?:([A-Za-z][\w-]*)\s+)?project number(?:\s*\(([^)]+)\))?:\s*\**\s*(\d+)")


def next_line_for(root, lines, only_root):
    for m in lines:
        prefix, paren = (m.group(1) or "").strip(), (m.group(2) or "").strip().rstrip("/")
        if paren == root or (prefix and prefix.lower() in root.lower()):
            return m
    if only_root:
        return next((m for m in lines if not m.group(1) and not m.group(2)), None)
    return None


def check_projects(ws, rep, budgets, today, fix):
    roots = budgets.get("project_roots") or ["projects"]
    index_p = ws / "memory" / "projects.md"
    text = read(index_p) if index_p.exists() else ""
    next_lines = list(NEXT_NUMBER.finditer(text))
    active_body = section(text, "Active")
    any_folders = False
    for root in roots:
        pdir = ws / root
        folders, dupes, all_dirs = {}, {}, []
        if pdir.is_dir():
            for d in sorted(pdir.iterdir()):
                if d.is_dir() and not d.name.startswith(("_", ".")):
                    m = PROJECT_DIR.match(d.name)
                    if not m:
                        rep.add("info", "projects", f"`{root}/{d.name}` doesn't follow the `NNN - Name` pattern.", f"{root}/{d.name}")
                        continue
                    num = int(m.group(1))
                    if num in folders:
                        dupes.setdefault(num, [folders[num].name]).append(d.name)
                    else:
                        folders[num] = d
                    all_dirs.append(d)
        any_folders = any_folders or bool(folders)
        for num, names in dupes.items():
            rep.add("warn", "projects", f"Project number {num:03d} is used by {len(names)} folders in `{root}/`: "
                    + ", ".join(f"`{x}`" for x in names) + ". Entries and logs can end up in the wrong one; renumber one of them.",
                    f"{root}/{names[-1]}")
        for d in all_dirs:
            if not (d / "log.md").exists():
                if fix:
                    (d / "log.md").write_text(f"# {d.name}: log\n\n> Append-only. Newest at the bottom.\n\n## {today} — Log created by coppice doctor\n\n"
                                              "- This project had no log. Earlier history, if any, wasn't recorded here.\n", encoding="utf-8")
                    rep.fixes.append(f"Created a stub `log.md` in `{root}/{d.name}/`.")
                else:
                    rep.add("error", "project-log", f"`{root}/{d.name}` has no `log.md` (rule 11).", f"{root}/{d.name}")
        if not text:
            continue
        # Index rows refer to folders as `root/NNN - Name/` in backticks.
        path_re = re.compile(r"`" + re.escape(root) + r"/(\d{3,4})\s*-\s*([^`/|]+)/?`")
        indexed = {int(m.group(1)): m.group(2).strip() for m in path_re.finditer(text)}
        active = {int(m.group(1)) for m in path_re.finditer(active_body)}
        template_rows = {n for n, name in indexed.items() if name.lower() in {"name", "[name]"}}
        missing = [folders[n].name for n in folders if n not in indexed]
        if missing:
            shown = ", ".join(f"`{x}`" for x in missing[:6]) + (f" and {len(missing) - 6} more" if len(missing) > 6 else "")
            rep.add("warn", "projects-index", f"{len(missing)} folder(s) in `{root}/` aren't listed in `memory/projects.md`: {shown} (rule 14).",
                    "memory/projects.md")
        ghosts = [f"{n:03d} ({name})" for n, name in indexed.items() if n not in folders and n not in template_rows]
        if ghosts:
            rep.add("warn", "projects-index", f"`memory/projects.md` lists {len(ghosts)} project(s) in `{root}/` with no matching folder: "
                    + ", ".join(ghosts[:6]) + ("…" if len(ghosts) > 6 else "") + ".", "memory/projects.md")
        # The next-number line: unlabelled if there's one root, labelled "(root)" if there are several.
        line = next_line_for(root, next_lines, len(roots) == 1)
        highest = max(list(folders) + [n for n in indexed if n not in template_rows], default=0)
        label = "" if len(roots) == 1 else f" ({root})"
        if line is None:
            rep.add("warn", "next-number", f"`memory/projects.md` has no \"Next project number{label}:\" line.", "memory/projects.md")
        elif int(line.group(3)) <= highest:
            width = len(line.group(3))
            want = f"{highest + 1:0{width}d}"
            if fix:
                text = text[: line.start(3)] + want + text[line.end(3):]
                index_p.write_text(text, encoding="utf-8")
                next_lines = list(NEXT_NUMBER.finditer(text))
                active_body = section(text, "Active")
                rep.fixes.append(f"Updated the next project number{label} in `memory/projects.md` from {line.group(3)} to {want}.")
            else:
                rep.add("error", "next-number", f"Next project number{label} is {line.group(3)}, but project {highest:03d} already exists. "
                        f"It should be {want}.", "memory/projects.md")
        for n in active & set(folders):
            log = folders[n] / "log.md"
            if log.exists():
                age = (today - dt.date.fromtimestamp(log.stat().st_mtime)).days
                if age > LOG_STALE_DAYS:
                    rep.add("info", "project-log", f"Active project `{folders[n].name}` hasn't had a log entry for {age} days. Still active?",
                            f"{root}/{folders[n].name}/log.md")
    if any_folders and not index_p.exists():
        rep.add("error", "projects-index", "`memory/projects.md` is missing, but project folders exist.", "memory/projects.md")


MD_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(((?:[^()\s]|\([^()\s]*\))+)(?:\s+\"[^\"]*\")?\)")


def check_links(ws, rep):
    for p, _ in iter_text_files(ws, owned_only=True):
        if p.suffix.lower() != ".md" or p.stat().st_size > MAX_SCAN_BYTES:
            continue
        broken = []
        text = read(p)
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        for m in MD_LINK.finditer(text):
            target = m.group(1)
            if re.match(r"^[a-z][a-z0-9+.\-]*:", target, re.I) or target.startswith("#"):
                continue
            path_part = urllib.parse.unquote(target.split("#", 1)[0])
            if not path_part or "NNN" in path_part or "[" in path_part or path_part.strip().lower() in PLACEHOLDER_TARGETS:
                continue
            dest = (p.parent / path_part) if not path_part.startswith("/") else (ws / path_part.lstrip("/"))
            if not dest.exists() and not (not dest.suffix and dest.with_suffix(".md").exists()):
                broken.append(target)
        if broken:
            shown = ", ".join(f"`{b}`" for b in broken[:3]) + (f" and {len(broken) - 3} more" if len(broken) > 3 else "")
            rep.add("warn", "links", f"{len(broken)} broken link(s) in `{rel(p, ws)}`: {shown}.", rel(p, ws))


def mask(value: str) -> str:
    return value[:4] + "…" + f"({len(value)} chars)" if len(value) > 8 else "…"


def check_secrets(ws, rep, accepted=()):
    in_code, in_accepted, too_big = {}, {}, []
    for p, code in iter_text_files(ws):
        if p.stat().st_size > MAX_SCAN_BYTES:
            if code is None:
                too_big.append(rel(p, ws))
            continue
        for i, line in enumerate(read(p).splitlines(), 1):
            for label, pat in SECRET_PATTERNS:
                m = pat.search(line)
                if not m:
                    continue
                value = m.groupdict().get("value") or m.group(0)
                if label == "Credential assignment":
                    if PLACEHOLDER_HINT.search(value) or not (re.search(r"\d", value) and re.search(r"[A-Za-z]", value)):
                        continue
                r = rel(p, ws).replace(os.sep, "/")
                if any(fnmatch.fnmatch(r, g) for g in accepted):
                    in_accepted[r] = in_accepted.get(r, 0) + 1
                elif code is not None:
                    in_code[code] = in_code.get(code, 0) + 1
                else:
                    rep.add("error", "secrets", f"Possible {label} in `{rel(p, ws)}` line {i} ({mask(value)}). "
                            "Move it to the keychain or an uncommitted `.env`, and rotate it if the file was ever shared (rule 15).", rel(p, ws))
                break
    if too_big:
        shown = ", ".join(f"`{f}`" for f in too_big[:5]) + (f" and {len(too_big) - 5} more" if len(too_big) > 5 else "")
        rep.add("info", "secrets", f"{len(too_big)} text file(s) over {MAX_SCAN_BYTES // 1_000_000} MB weren't scanned for secrets: {shown}. "
                "Large files are usually logs or data; if one isn't, check it by hand.", ".")
    if in_accepted:
        files = ", ".join(f"`{f}` ({n})" for f, n in sorted(in_accepted.items()))
        rep.add("info", "secrets", f"{sum(in_accepted.values())} possible secret(s) in files you've accepted the risk for in `setup.md`: {files}. "
                "Still worth moving to the keychain when there's time; anyone who can read these files can use them.", "setup.md")
    for code, n in sorted(in_code.items()):
        rep.add("info", "secrets", f"{n} possible secret(s) inside the code project `{rel(code, ws)}`. Often test fixtures or examples, "
                "but worth a look: run the doctor inside that folder for details.", rel(code, ws))


HEARTBEAT_ROW = re.compile(r"^\|\s*(\d{4}-\d{2}-\d{2})[^|]*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|")


def check_heartbeat(ws, rep, setup_text, today, running_as=None):
    schedule = parse_schedule(setup_text)
    if not schedule:
        return
    hb = ws / "memory" / "heartbeat.md"
    last, last_result = {}, {}
    if hb.exists():
        for line in read(hb).splitlines():
            m = HEARTBEAT_ROW.match(line.strip())
            if m:
                d, task, result = dt.date.fromisoformat(m.group(1)), strip_code(m.group(2)), m.group(3).strip().lower()
                if task not in last or d >= last[task]:
                    last[task], last_result[task] = d, result
    if running_as:                      # this run is about to record its own heartbeat; don't warn about ourselves
        last[running_as], last_result[running_as] = today, "ran"
    if not last:
        rep.add("info", "heartbeat", "No scheduled task has recorded a run in `memory/heartbeat.md` yet. Expected in a new workspace; "
                "if tasks have been set up for a while, check they write their heartbeat line.", "memory/heartbeat.md")
        return
    for t in schedule:
        gap = allowed_gap_days(t["when"])
        name = t["name"]
        if name not in last:
            rep.add("warn", "heartbeat", f"Scheduled task `{name}` has no heartbeat in `memory/heartbeat.md`. Has it ever run? (rule 21)",
                    "memory/heartbeat.md")
            continue
        age = (today - last[name]).days
        if gap and age > gap:
            rep.add("warn", "heartbeat", f"Scheduled task `{name}` ({t['when']}) last ran {age} days ago ({last[name]}). It may have stopped (rule 21).",
                    "memory/heartbeat.md")
        if last_result.get(name, "").startswith("fail"):
            rep.add("warn", "heartbeat", f"Scheduled task `{name}` failed on its last run ({last[name]}).", "memory/heartbeat.md")


REPORT_NAME = re.compile(r"(?i)(report|digest|briefing|scan|gaps?).*\d{4}-\d{2}-\d{2}|\d{4}-\d{2}-\d{2}.*(report|digest|briefing|scan)")


def check_reports(ws, rep, budgets, today):
    mem = ws / "memory"
    if mem.is_dir():
        strays = [p for p in mem.glob("*.md") if REPORT_NAME.search(p.stem)]
        if strays:
            names = ", ".join(f"`{p.name}`" for p in strays[:5]) + ("…" if len(strays) > 5 else "")
            rep.add("warn", "reports", f"{len(strays)} generated report(s) in `memory/` ({names}). Reports belong in `reports/` (rule 25).", "memory/")
    rdir = ws / "reports"
    if rdir.is_dir():
        old = [p for p in rdir.rglob("*") if p.is_file() and not p.name.startswith(".")
               and (today - dt.date.fromtimestamp(p.stat().st_mtime)).days > budgets["reports_days"]]
        if old:
            rep.add("info", "reports", f"{len(old)} report(s) in `reports/` are older than {budgets['reports_days']} days. `archive-trim` should delete them.", "reports/")


LAST_UPDATED = re.compile(r"(?i)last updated:?\**\s*(\d{4}-\d{2}-\d{2})")


def check_last_updated(ws, rep, today):
    for f in ["soul.md", "setup.md"]:
        m = LAST_UPDATED.search(read(ws / f))
        if m:
            age = (today - dt.date.fromisoformat(m.group(1))).days
            if age > LAST_UPDATED_STALE_DAYS:
                rep.add("info", "last-updated", f"`{f}` was last updated {age} days ago. Worth a quick review?", f)


# ---------------------------------------------------------------- output

def render(rep: Report, ws: Path, today: dt.date) -> str:
    icon = {"error": "🔴", "warn": "🟡", "info": "⚪"}
    lines = [f"# Coppice doctor — {today}", "", f"Workspace: `{ws}`", ""]
    e, w, i = rep.count("error"), rep.count("warn"), rep.count("info")
    lines.append("**All clear.** Nothing to fix." if not (e or w or i) else f"**{e} error(s), {w} warning(s), {i} note(s).**")
    if rep.stats.get("startup_tokens"):
        per = ", ".join(f"{k}: ~{v:,}" for k, v in rep.stats["startup_tokens"].items())
        lines += ["", f"Startup read (tokens, estimated): {per}."]
    if rep.fixes:
        lines += ["", "## Fixed", ""] + [f"- {f}" for f in rep.fixes]
    for sev, title in (("error", "Errors"), ("warn", "Warnings"), ("info", "Notes")):
        items = [f for f in rep.findings if f.severity == sev]
        if items:
            lines += ["", f"## {title}", ""] + [f"- {icon[sev]} **{f.check}** — {f.message}" for f in items]
    return "\n".join(lines) + "\n"


def run(ws: Path, today: dt.date, fix: bool = False, running_as: str | None = None) -> Report:
    rep = Report()
    setup_text = read(ws / "setup.md")
    budgets, root_allowed, has_block = parse_budgets(setup_text)
    if (ws / "setup.md").exists() and not has_block:
        rep.add("info", "budgets", "No `budgets` block found in `setup.md`; using the defaults.", "setup.md")
    contexts = parse_contexts(setup_text)
    IGNORE[:] = budgets.get("ignore", [])
    check_required(ws, rep)
    check_recent(ws, rep, budgets, contexts, today, fix)      # before the startup measurement, so fixes count
    check_startup(ws, rep, budgets, contexts)
    check_tasks(ws, rep, budgets, contexts)
    check_learning_log(ws, rep, budgets)
    check_root(ws, rep, root_allowed)
    check_working(ws, rep, today)
    check_projects(ws, rep, budgets, today, fix)
    check_links(ws, rep)
    check_secrets(ws, rep, budgets.get("secrets_accepted", []))
    check_heartbeat(ws, rep, setup_text, today, running_as)
    check_reports(ws, rep, budgets, today)
    check_last_updated(ws, rep, today)
    return rep


def append_heartbeat(ws: Path, today: dt.date, rep: Report):
    hb = ws / "memory" / "heartbeat.md"
    if not hb.exists():
        hb.parent.mkdir(parents=True, exist_ok=True)
        hb.write_text("# Heartbeat\n\n| When | Task | Result | Note |\n|---|---|---|---|\n", encoding="utf-8")
    note = f"{rep.count('error')} errors, {rep.count('warn')} warnings, {len(rep.fixes)} fixes"
    with hb.open("a", encoding="utf-8") as fh:
        text = read(hb)
        if not text.endswith("\n"):
            fh.write("\n")
        fh.write(f"| {today} | {HEARTBEAT_NAME} | ran | {note} |\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Health check for a Coppice workspace.")
    ap.add_argument("--workspace", "-w", default=".", help="workspace folder (default: current folder)")
    ap.add_argument("--fix", action="store_true", help="apply safe, mechanical fixes")
    ap.add_argument("--report", help="also write the report to this file (relative to the workspace)")
    ap.add_argument("--heartbeat", action="store_true", help="append a line to memory/heartbeat.md")
    ap.add_argument("--json", action="store_true", help="print findings as JSON instead of markdown")
    ap.add_argument("--today", help=argparse.SUPPRESS)  # for tests
    args = ap.parse_args(argv)
    ws = Path(args.workspace).expanduser().resolve()
    if not ws.is_dir():
        print(f"Not a folder: {ws}", file=sys.stderr)
        return 2
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    rep = run(ws, today, fix=args.fix, running_as=HEARTBEAT_NAME if args.heartbeat else None)
    out = (json.dumps({"today": str(today), "fixes": rep.fixes, "stats": rep.stats,
                       "findings": [f.__dict__ for f in rep.findings]}, indent=2, ensure_ascii=False)
           if args.json else render(rep, ws, today))
    print(out)
    if args.report:
        rp = ws / args.report
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(render(rep, ws, today), encoding="utf-8")
    if args.heartbeat:
        append_heartbeat(ws, today, rep)
    return 1 if rep.count("error") else 0


if __name__ == "__main__":
    sys.exit(main())
