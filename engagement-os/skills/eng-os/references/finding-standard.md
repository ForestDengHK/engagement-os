# Finding standard

The single authority for what a finding file looks like. This is the *master* copy;
`eng-scaffold` plants a project-local copy at `1_discovery/3_findings/_FINDING_STANDARD.md`.
In an active engagement, follow the project's planted copy (it may carry engagement-specific
areas and backbone) and treat this as the reference for the *why*.

## Contents
- What a finding is (and is not)
- The fixed header block
- The two orthogonal rating axes
- Evidence tags on every claim
- Body shapes
- The three fixed closing sections
- The signature move: record contradictions, don't smooth them
- Backbone mapping

## What a finding is (and is not)

A finding is a **current-state fact baseline**: it records what *is*, so every downstream
deliverable can cite the *same fact* with its *own* so-what, without re-pasting evidence.

- A finding is **NOT** a recommendation. The remediation *direction* is a forward-looking
  cause-tag, not a solution. The solution is built downstream in `eng-build-deliverable`.
- One coherent topic per file. Cross-reference other findings rather than duplicate.
- Observation and interpretation stay visibly separate: assertive language for what was
  observed, hedged language for what was inferred.

## The fixed header block (exact order)

```markdown
# Finding — <one-line topic>
**Area:** <Data · Platform · Reporting/BI · Compliance · Governance · Operations · Integration>
**Backbone item(s) mapped:** #<n> (<label>) · #<n> (<label>)
**Severity:** <Critical|High|Medium|Low|N/A> — <one-line rationale>
**Priority:** <High|Medium|Low> — <one-line rationale>
**Status:** <confirmed-vs-open in ONE line, with open-question IDs>
**Feeds:** <applicable D-items only, ·-separated, canonical D1–D6 numbering>
```

`Backbone item(s)` = the engagement's fixed problem list (RFP limitations, audit objectives,
hypothesis tree, capability gaps). Every finding maps to ≥1. See "Backbone mapping" below.

## The two orthogonal rating axes (never collapse them)

- **Severity** = *intrinsic problem badness* (Likelihood × Impact), assessed on evidence
  alone, **before** priority, independent of scope. Stable.
- **Priority** = *engagement relevance* (in scope? central to the contracted assessment?
  client-flagged?). A judgment set **after** severity.

A Critical-severity item can be Low priority; a Medium-severity item can be High priority.
**If you find yourself mapping severity straight to priority, you have collapsed the axes — stop.**

## Evidence tags on every claim

Every factual claim carries exactly one evidence tag:

- `[Observed]` — directly verified (ran the query, saw the config, read the doc). Assertive language.
- `[Reported]` — a person asserted it (workshop/interview). Attribute speaker + session + transcript line. **Inquiry alone is never sufficient — corroborate with a second source before treating as established.**
- `[Assumed]` — our inference/hypothesis. Hedged language ("suggests", "likely"). Keep hypothesis blocks visibly distinct with a `⚐` marker.
- `[RFP]` — from the RFP / briefing text.

Anything a higher-tier source doesn't yet support gets an inline `[⚠VERIFY vs <source>]` flag
and a row in the verification register. See `provenance-and-precedence.md` for the tier tags
(`[T1]/[T2]/[T3]`) that arbitrate conflicts between sources.

**Evidence tags and precedence tags are orthogonal, not the same axis.** An evidence tag says
*how you know* a claim (observed / reported / assumed / from-brief); a precedence tag says
*which source wins* when two disagree (system > workshop > reference). A single claim can carry
both — e.g. `[Observed][T1:SYS]` (you ran the query) or `[Reported][T2:WS]` (someone said it in
a workshop). Don't collapse them.

## Source-evidence block (every finding has one)

A finding cites where its evidence came from — the form depends on the source:
- **Workshop/interview:** `Held-notes: <path> · transcript lines <n–m> · question ID(s)`.
- **Document/canonical:** `Source-md: <pack>/_md/<topic>/<slug>.md §Page/Slide N` (tag the claim `[T3:REF]`/`[T3:OWN]`).
- **System query:** `Query: <script/pack> → <result file>` (tag the claim `[T1:SYS]`).

No finding ships without at least one concrete locator — that is the whole point of a fact baseline.

## Body shapes

Two valid shapes:
- **Multi-finding** (preferred): per-item severity within the file, so a reader can triage
  within one topic. Use when a topic contains several distinct sub-findings.
- **Single-finding**: one overall severity + a dedicated rationale section.

Quantify wherever possible (counts / % / dates / object names). Vague findings don't drive decisions.

## The three fixed closing sections

Every finding file ends with, in order:
1. **Remediation direction** — a forward-looking cause-tag, **not** a solution.
2. **Cross-references** — links to related findings (don't duplicate their content).
3. **Gaps still owed** — what's unverified or not yet elicited, matched to open-question IDs.

## The signature move: record contradictions, don't smooth them

Separate what the client *said* in the room from what the *evidence* shows, and refuse to
smooth a contradiction. Worked example: the client framed "single schema = the problem";
the evidence showed the root cause was an over-broad `SELECT ANY TABLE` privilege. The finding
records **both** and re-points the remediation at the real cause. Findings record contradictions
rather than resolving them prematurely — that is what keeps the corpus trustworthy.

## Backbone mapping

Declare the backbone once (the engagement's fixed, defining problem list). Then:
- Force every finding to map onto ≥1 backbone item (reject a "finding" that maps to none —
  either extend the backbone deliberately, or it's out of scope).
- Maintain a **backbone → file(s) matrix** in `3_findings/README.md` (bidirectional coverage:
  "which findings cover item #9?" and "which items does this finding serve?").
- **Close mis-stated backbone items in place** with a reason, never delete them
  (e.g. #6 "hardware failure" → "Closed as mis-stated, see `oracle_dwh_infrastructure.md §3`").
- An area folder with no file against its mapped backbone item is a visible gap.
