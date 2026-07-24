---
name: eng-validate-findings
description: Use when the user says "validate the findings", "run the precedence sweep", "reconcile the sources", "check provenance", or after a wave of new evidence lands on an engagement's findings corpus.
---

# Validating findings

Enforce the provenance + validation discipline across the whole finding corpus, in waves. This is
the **only** skill that runs the corpus-wide precedence sweep. It edits the register and applies
tags; it does not invent new findings.

## The register
`02_delivery/_pm/source_precedence_and_conflict_register.md` — the truth-arbitration layer.
Precedence tiers, the `[⚠VERIFY]` lifecycle, and conflict clusters are defined in `eng-os`
→ `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/provenance-and-precedence.md`.

## Workflow

```
Validation Progress:
- [ ] 1. Per-claim audit: evidence tag present; [Reported]-only-without-corroboration flagged
- [ ] 2. Precedence sweep: apply the three decision rules; supersede losers (never delete)
- [ ] 3. Cluster recurring conflicts into CL-* rows
- [ ] 4. [⚠VERIFY]/V-n register: open rows, triage by channel, drive to ✅ CLOSED with evidence
- [ ] 5. Canonical-alignment: every finding Status line matches the open-question backlog
- [ ] 6. Backbone coverage: every backbone item has ≥1 finding; mis-stated items closed in place
- [ ] 7. Emit a clean-reference vs stale-layer map for downstream derivation
```

**Step 2 — the three decision rules.** (1) System-measurement beats the room. (2) The room beats
the deck. (3) Evidence beats the proposed fix. On conflict, keep both sources and stamp the loser
`[T3:REF ⚠ superseded-by → <winner>]`. Never delete.

**Step 4 — verification lifecycle.** For every unsupported claim, open a register row
(`Item | Check against | Owner | Blocks`). Triage each open item by channel: already-in-corpus /
system-scriptable / needs-client. Drive to `✅ CLOSED <date>` citing the resolving evidence. A
client-facing headline may never rest on an open `[⚠VERIFY]` figure.

**Step 5 — canonical alignment.** Every finding's `Status:` line must match the canonical
open-question backlog (`0_mobilisation/discovery_questions.md`). Flag drift both ways.

**Step 6 — backbone coverage.** Every backbone item has ≥1 mapped finding; an uncovered item is a
visible gap. Mis-stated backbone items are closed in place with a reason, never deleted.

**Step 7 — output.** Add a dated running-header entry to the register for this wave, apply the
inline tags, and produce the "clean reference vs stale layer" map so `eng-build-deliverable`
inherits only from reconciled inputs.

## Guardrails
Never delete a conflicting source — supersede with a marker. Never close a `V-n` without citing
the evidence that resolved it. Corroborate `[Reported]`-only claims before treating them as established.
