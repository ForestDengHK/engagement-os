# Source precedence & the verification register

How the engagement arbitrates when two sources disagree, and how unverified claims are
gated so they never silently drive a decision. This is the truth-arbitration layer that sits
under every finding and every deliverable.

## Contents
- The three-tier precedence model
- The three decision rules
- The hard rule: every update must be sourced
- The `[⚠VERIFY]` / V-n register and its lifecycle
- Conflict clusters
- Never delete — supersede

## The three-tier precedence model

| Tier | Tag | What | Rule |
|---|---|---|---|
| **T1** | `[T1:SYS §x]` | Facts measured directly from the system (query results, data dictionary, config) | **Trumps everything, including a workshop** |
| **T2** | `[T2:WS <session> <date>]` | Facts from a held workshop (cite session + date) | Overrides all reference/vendor docs |
| **T3** | `[T3:REF <source> <loc>]` | Reference / vendor material (prior-consultant decks, HLDs, strategy docs, RFP) | Kept, never deleted; stamped superseded on conflict |

Rename the `SYS` label to the engagement's actual system of record (`EDW`, `warehouse`,
`ERP`, etc.). The *tiers* are universal; the *labels* are per-engagement.

**Our own research is reference-tier but tag it distinctly** — `[T3:OWN <source>]` (e.g. a
target-platform pattern we researched, a benchmark we assembled) — so it is never mistaken for
a client-supplied source. It carries the same "kept, superseded-not-deleted" discipline as `[T3:REF]`.

## The three decision rules

1. **System-measurement beats the room.** Worked example: the room said schema `BGL_WH`;
   the data dictionary said `BGE_WH` → `BGE_WH` wins, and every `BGL_WH` is a terminology error.
2. **The room beats the deck.** A held workshop overrides a prior-vendor document; the deck
   is kept and marked superseded.
3. **Evidence beats the proposed fix.** Where the room proposed a remedy but post-session
   analysis shows a different root cause, the evidence-grounded analysis governs.

## The hard rule: every update must be sourced

- Each finding carries a `## Source evidence` block: held-notes path + transcript line-range
  + canonical open-question ID(s).
- Each factual claim carries an evidence tag (`[Observed]/[Reported]/[Assumed]/[RFP]`) and,
  where contested, a precedence tag (`[T1]/[T2]/[T3]`).
- New information enters as a *tagged* update (e.g. `[T2:WS W4.1 10-Jun]`), logged in the
  register's running header per wave — never as a silent overwrite.

## The `[⚠VERIFY]` / V-n register and its lifecycle

Anything a T1/T2 source doesn't yet support gets:
- an inline `[⚠VERIFY vs <source>]` flag on the claim, **and**
- a row in the register's Verification-Needed table: `# | Item | Check against | Owner | Blocks`.

Each `V-n` item has an explicit lifecycle:
```
V-5  OPEN 2026-06-01  — Asset-team role-readers unnamed; check DBA_ROLE_PRIVS; owner DBA; blocks A28
V-5  ✅ CLOSED 2026-06-08 — role-readers named AIM_EXPL / GICHAMPI / BGE_READ via DBA_ROLE_PRIVS
```
Triage each open item by channel: already-in-corpus / system-scriptable / needs-client.
A client-facing headline may **never** rest on an open `[⚠VERIFY]` figure.

## Conflict clusters

When one underlying fact recurs across many files, consolidate it into a labelled cluster
(`CL-A … CL-L`) in the register rather than re-arguing it per file. Each cluster carries:
truth verdict · kept-as-REF item · files-to-tag · confidence (H/M/L).

## Never delete — supersede

Superseded facts are never deleted; they are stamped `[T3:REF ⚠ superseded-by → <source>]`
so they stay citable without driving a decision. This preserves the audit trail and lets a
reviewer see *why* the current answer beat the old one.
