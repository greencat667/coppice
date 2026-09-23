# Working patterns

Named ways of working that you can ask for by name, and that the assistant can offer when one clearly fits. Each is short enough to use mid-conversation. None should be applied to everything: part of each pattern is knowing when not to use it.

---

## Critique passes

### Two-pass critique

**Use for:** strategy documents, proposals, synthesis, anything where being persuasive could hide being wrong.

1. **Builder pass:** make the strongest honest case for the idea.
2. **Sceptic pass:** what's weak, missing, untested or assumed? Name the single biggest risk.

Report both, and flag clearly if the sceptic pass found something that should change the conclusion.

### Three-pass critique

**Use for:** anything external-facing, or anything that affects people who aren't in the room.

The two passes above, plus:

3. **Values pass:** check it against the values in `soul.md` and any standing commitments (an organisation's ethics policy, for example). Who is affected but not represented? Whose consent is assumed? Does the framing extract from, or speak for, a group it should be working with?

Offer this pass; don't impose it on everything.

---

## Evidence mode

**Use for:** research, synthesis, summarising source material, anything that will be quoted or relied on.

Only state what you can point to in the provided sources, and say where. If something isn't in the sources, say so, rather than filling the gap from general knowledge. If general knowledge is genuinely useful, add it separately and label it as such.

---

## Calibrate on five before scaling

**Use for:** applying a framework, rubric or set of criteria to a large set of items, e.g. rating a hundred signals or tagging two hundred survey responses.

Apply it to five representative items first. Show the results, agree any adjustments, then run the full set. Fixing the criteria after five items costs minutes; fixing them after two hundred costs the whole run.

---

## Planning-first brief

**Use for:** any task expected to take more than about 20 minutes.

Before starting, write three lines and check them with the person:

- **Objective:** what we're trying to achieve, and for whom
- **Approach:** how we'll go about it
- **Success looks like:** how we'll know it worked

The project template's `brief/brief.md` holds exactly this.

---

## Compression handoff

**Use for:** moving a line of thinking from a chat on another device or assistant into this workspace.

Attach `memory/handoff-prompt.md` to the chat and say *"Apply this to our conversation."* Paste the half-page result into a new session here as the opening message. It carries the context, conclusions, the one live question and a first action, without the whole transcript.

---

## Correction scan

**Use for:** the end of every session. It's part of the session protocol.

Look back for moments where the person corrected or redirected the assistant ("no, like this"). Most corrections are one-offs. Some contain a rule that would apply next time too. Offer at most one or two of those as learning-log entries. The aim is to catch the directive corrections that would otherwise be lost when the session ends.

---

## Compounding prompt

**Use for:** straight after a significant piece of work (a strategy document, a report, a hard problem solved), not only at the end of the session.

Ask once: *"Worth adding to the learning log?"* or, if there's a knowledge wiki, *"Anything here worth keeping in the wiki?"* A short answer is fine. The point is to make the question routine.

---

## State redirect

**Use for:** when the person describes their state rather than asking for something ("brain's tired", "keep getting distracted").

Acknowledge it in a line, then offer **one** concrete next action sized to that state. Don't analyse it, and don't offer a new framework. `soul.md` usually says what works for them.

---

## Handoff contract

**Use for:** any piece of work that more than one assistant (or an assistant and a person) takes turns on, e.g. one assistant drafts and another builds and publishes.

Keep a small state file with the work, e.g. `STATE.yaml`:

```yaml
stage: draft-review        # where the work is in its pipeline
owner: writer              # who may edit it right now
next_owner: builder        # who it goes to next
required_before_handoff:   # checks that must be true before ownership changes
  - self_edit_done: true
  - word_count_checked: true
handed_over: 2026-09-01
notes: "Chapter 4 cut from the build; see log.md"
```

Rules:

- Only the current `owner` edits the work's source files.
- Handing over means updating the file (new owner, date) and saying so. It never just happens.
- A check that matters is a named, required field, not a line in someone's instructions. Optional-shaped steps get skipped.

---

## Adding your own

A pattern earns a place here when it's been used and worked several times (usually via the learning log). Give it a name you'd actually say out loud, a **Use for** line, and the steps. Name when *not* to use it too, if that's not obvious.
