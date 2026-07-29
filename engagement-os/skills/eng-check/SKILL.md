---
name: eng-check
description: Use before shipping anything, or when the user asks "is this ready", "check the bid", "can we submit", "run the checks", "what's blocking submission", "验一下". Also answers "what companion skills am I missing / do I need to install anything" (`eng-check companions`). Runs every mechanical gate that applies — repo invariants (unmet mandatory requirements, unverified claims in a frozen response, confidentiality-bucket leaks, dangling citations) and, if the artefact is a deck, the package gates. Reports what is blocking and why, in the order a human should fix it. Never fixes silently; never overrides a gate.
---

# Checking whether it is safe to ship

The gates are scripts, not judgement — so nobody should be typing a script path to reach them.
This skill is the door: it decides *which* checks apply, runs them, and turns their output into
"here is what is blocking you, here is what each one means".

**Dependency (packaging note).** The engines are
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/eng_lint.py`, `verify_deck.py` and
`check_companions.py`. This skill is the facade; all three live with the eng-os kernel.
Pruning skills individually must keep `eng-os`.

## "companions" — am I missing anything, or can I skip the install?

Invoked as `eng-check companions` (or any "do I need to install anything / what's missing"
phrasing), run **only** this and report its output — the repo gates below do not apply:

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/check_companions.py
```

It surveys every skill this pack delegates to, says where each one resolved from, and prints
install commands **only for what is genuinely absent**. Two outcomes, and both are terminal:

- **nothing missing** → say so and stop. Do not offer the bundle; installing it on top of
  skills the user already keeps in `~/.claude/skills/` gives them a second namespaced copy
  of each. "Skip it" is the correct advice, not a fallback.
- **something missing** → relay the impact line for each, then the commands verbatim.
  A missing *recommended* companion is not a blocker: engagement-os declares no plugin
  dependencies, stays enabled, and the skill that delegates to it has a written fallback.

Run it unprompted the first time a stage actually needs a companion — not at every session
start, and never as a gate on work the user can still do.

## Workflow

```
- [ ] 0. Invoke `Skill(engagement-os:eng-propagate-change)` first. A pending manual edit,
        stale generated output, invalidated review, or modified frozen file blocks "clean".
- [ ] 1. Work out what is being checked:
        an engagement repo (a bid, a delivery)          → step 2
        an assembled deck                               → step 3
        a directory of sections about to be rendered    → hand to `eng-render --analyse`
        Check everything that applies — a bid with a deck gets both.
- [ ] 2. REPO: python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/eng_lint.py <root> --strict
        Drop --strict for a mid-flight check: warnings are then informational and only
        errors fail. Use --strict before any freeze or submission.
- [ ] 3. DECK: python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/verify_deck.py <deck.pptx> \
          --expect <slide count intended>
        See eng-os references/deck-assembly.md for what each finding means.
- [ ] 4. Report findings grouped BY WHAT THE USER MUST DO, not by which script emitted them:
          - blocks submission  (errors: unmet mandatory, [⚠VERIFY] in a frozen response,
                                bucket leak, flattened client deck)
          - fix before review  (warnings that will cost marks or trust)
          - informational
        Name the file and the fix for each. A finding nobody can act on is noise.
- [ ] 5. If nothing is blocking, say so plainly and name what was checked. "Clean" without
        a list of what ran is indistinguishable from "I didn't run anything".
```

## "I want the document anyway"

A finding is information, not a veto. When the user wants the real artefact before every gate
closes — to read it, to circulate it, to measure the page count — the answer is not to argue: hand
to `Skill(engagement-os:eng-render)` with `--force`. A forced strict-profile build is a full,
correctly stripped, correctly paginated document that **labels itself**: a first-page banner names
every gate finding it was built past, and any `[⚠VERIFY]` marker stays visible in the text. What it
must never become is a file indistinguishable from the submission — that is the whole reason the
banner exists, and it is why re-running without `--force` (once the findings close) is the build
that may actually be sent.

What this skill will not do is close a finding to make the build quiet.

## What this does NOT do

- **It does not fix.** A lint error is usually a real gap in the work (a requirement genuinely
  unmet, a claim genuinely unsourced). Silently editing the artefact to make a check pass is
  how a gate becomes decoration.
- **It does not override.** `--force` on the render, `--review-copy` on a deck: those are the
  user's calls, made with the finding in front of them, not routed around by this skill.
- **It does not judge content.** Whether the answer is *good* is `panel-review` and the human
  round. This decides only what a script can decide — which is why it is cheap enough to run
  constantly rather than once at the end.
- **It does not bless an unpropagated edit.** Complete the change-impact hand-offs and reviews,
  checkpoint the reconciled state, then run this gate again.

## Run it early and often

The gates are designed to be run mid-flight, not as a ceremony before submission. A bucket leak
found on the day it happens is a one-line fix; found the night before submission it is a
re-write of a section under time pressure. `eng_lint.py --list` prints the rule registry if you
want to know exactly what is being decided.
