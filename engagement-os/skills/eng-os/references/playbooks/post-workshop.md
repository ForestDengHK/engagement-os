# Playbook: after a workshop / discovery session

Turns raw session output (notes, transcript, query results) into validated-trajectory
knowledge within the same day, while memory is fresh.

## Chain

```
held-notes ─► eng-write-findings ─► eng-update-canonical ─► backlog + eng-maintain-memory
 (human)        per topic             deltas only              per session
```

1. **Held-notes** (human or agent-assisted): fill the session's held-notes file —
   what was asked, what was answered, direct quotes, what was NOT covered.
   Verify: every agenda item is marked covered / deferred / not-run.
2. **Findings — one per coherent topic** → `eng-write-findings`.
   New findings for new topics; extend existing findings where the session added
   evidence. Every claim carries an evidence tag (`[Observed]`/`[Reported]`/…)
   and a precedence tag; new unverifiable claims get `[⚠VERIFY]` + a V-n register row.
   Verify: each finding maps to the backbone; quotes are attributed.
3. **Canonical deltas** → `eng-update-canonical`.
   Only the session's *deltas* — corrected facts, new systems/people/dates —
   not a re-summary of the whole session (the held-notes + findings hold that).
4. **Backlog sweep** (part of `eng-update-canonical`'s remit):
   flip answered discovery questions to their answer status with the source;
   add newly-surfaced questions. List what the session was supposed to cover but
   didn't — that becomes the "owed" list for the next session.
5. **Log + memory** → `eng-maintain-memory`: session write-up in the engagement log;
   milestone line in CLAUDE.md only if a phase/week closed.

## Stop gates

- **Do NOT canonicalize from the transcript directly** — canonical facts come from
  the held-notes/findings, which are the checked layer. Transcripts are T2 evidence,
  cited not mined.
- **STOP and flag** if the session contradicts the current findings backbone
  (e.g. reveals a whole missing area) — backbone changes are a human decision.
