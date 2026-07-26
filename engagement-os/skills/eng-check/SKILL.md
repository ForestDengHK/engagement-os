---
name: eng-check
description: Use before shipping anything, or when the user asks "is this ready", "check the bid", "can we submit", "run the checks", "what's blocking submission", "验一下". Runs every mechanical gate that applies — repo invariants (unmet mandatory requirements, unverified claims in a frozen response, confidentiality-bucket leaks, dangling citations) and, if the artefact is a deck, the package gates. Reports what is blocking and why, in the order a human should fix it. Never fixes silently; never overrides a gate.
---

# Checking whether it is safe to ship

The gates are scripts, not judgement — so nobody should be typing a script path to reach them.
This skill is the door: it decides *which* checks apply, runs them, and turns their output into
"here is what is blocking you, here is what each one means".

**Dependency (packaging note).** The engines are
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/eng_lint.py` and `verify_deck.py`. This skill is
the facade; both live with the eng-os kernel. Pruning skills individually must keep `eng-os`.

## Workflow

```
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

## What this does NOT do

- **It does not fix.** A lint error is usually a real gap in the work (a requirement genuinely
  unmet, a claim genuinely unsourced). Silently editing the artefact to make a check pass is
  how a gate becomes decoration.
- **It does not override.** `--force` on the render, `--review-copy` on a deck: those are the
  user's calls, made with the finding in front of them, not routed around by this skill.
- **It does not judge content.** Whether the answer is *good* is `panel-review` and the human
  round. This decides only what a script can decide — which is why it is cheap enough to run
  constantly rather than once at the end.

## Run it early and often

The gates are designed to be run mid-flight, not as a ceremony before submission. A bucket leak
found on the day it happens is a one-line fix; found the night before submission it is a
re-write of a section under time pressure. `eng_lint.py --list` prints the rule registry if you
want to know exactly what is being decided.
