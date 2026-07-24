---
name: eng-write-findings
description: Use when writing up current-state findings from discovery evidence (workshop notes, transcripts, system-query results, canonical source markdown), when the user says "write this up as a finding", "capture the current-state finding", or "turn these notes into findings".
---

# Writing findings

Produce a **fact baseline** — a finding records what *is*, so every downstream deliverable can
cite the same fact with its own so-what. A finding is NOT a recommendation.

## Read the project's own standard first
Follow `02_delivery/1_discovery/3_findings/_FINDING_STANDARD.md` (planted per engagement — it
may carry engagement-specific areas and backbone). The method rationale is in `eng-os` →
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/finding-standard.md`. A blank file to copy: `3_findings/_TEMPLATE_finding.md`.

## Workflow

```
Finding Progress:
- [ ] 1. One coherent topic → pick the area folder → new file
- [ ] 2. Header block: Area · Backbone item(s) · Severity · Priority · Status · Feeds
- [ ] 3. Source-evidence block (held-notes path + transcript lines + question IDs)
- [ ] 4. Body: tag every claim; quantify; keep observation vs inference separate
- [ ] 5. Rate Severity (evidence-only) THEN Priority (engagement pull) — don't collapse them
- [ ] 6. Precedence tags on contested claims; [⚠VERIFY] + register row for unsupported ones
- [ ] 7. Close with Remediation direction / Cross-references / Gaps still owed
- [ ] 8. Set Status to match the canonical open-question backlog; update the backbone matrix
```

**Step 1 — scope + map.** One topic per file, in the right `<area>/` folder. Map to ≥1 backbone
item; if it maps to none, either extend the backbone deliberately or it's out of scope — don't invent one.
**If the backbone isn't set yet** (fresh engagement, `3_findings/README.md` still placeholders):
seed it first from the engagement's known problem areas / RFP limitations / audit objectives, or
map the finding `#provisional` and flag it in "Gaps still owed" — never skip the mapping.

**Step 3 — source evidence** must carry ≥1 concrete locator matched to the source type: a workshop
(held-notes + transcript lines + question ID), a **document** (`Source-md …§Page/Slide N`, tag
`[T3:REF]`/`[T3:OWN]`), or a **query** (result file, tag `[T1:SYS]`). A finding from a PDF is as
valid as one from a workshop — it just cites the source-md, not a transcript.

**Step 4 — tag every factual claim:** `[Observed]` (verified directly, assertive language) ·
`[Reported]` (a person said it — attribute speaker + session + line; corroborate before treating
as established) · `[Assumed]` (our inference — hedged, `⚐` marker) · `[RFP]` (from the brief).
Quantify (counts / % / dates / object names).

**Step 5 — two axes, never collapsed.** Severity = intrinsic badness (Likelihood × Impact) on
evidence alone, set first. Priority = engagement relevance, set after. A Critical item can be Low
priority and vice-versa. If severity maps straight to priority, stop.

**Step 6 — precedence + verification.** Add `[T1]/[T2]/[T3]` on contested claims (system-measured
> workshop > reference). Anything a higher tier doesn't support gets `[⚠VERIFY vs <source>]` +
a row in `_pm/source_precedence_and_conflict_register.md`.

**The signature move:** separate what the client *said* from what the *evidence* shows; record
the contradiction rather than smoothing it; re-point the remediation at the real cause.

## Guardrails
Never fabricate a rating, source, or fact. Assertive language only for `[Observed]`. A finding is
a fact baseline, not a recommendation. Every Status line matches the canonical backlog.

## Hand-off
Once written, findings are swept for provenance by `eng-validate-findings` and assembled by
`eng-build-deliverable`.
