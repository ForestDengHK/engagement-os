# Playbook: the scope grows — add a block to an existing repo

A research assignment turns into a bid. A bid is won. A delivery client asks for a study first.
The repo doesn't get rebuilt and it doesn't get a sibling — you **add the block** and keep one
audit trail. Blocks are additive by design; the scaffolder never clobbers.

The mechanical part takes one command. The part that matters is what does **not** carry over.

## Chain

```
re-run eng-scaffold --mode <old>,<new> ─► top up CLAUDE.md ─► draft the handoff ─► re-baseline sources
       adds only the new block              you edit it         what we promised     the sharp gate
```

1. **Re-run the scaffolder with the old blocks AND the new one.**
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/scaffold_engagement.py \
     --root <same root> --client <CLIENT> --eng-id <ENG-ID> --name "<name>" \
     --mode <old>,<new> --phase <new phase label>
   ```
   Always name the **old blocks too** — the mode is the repo's full block list, not a delta.
   Verify: the new work tree + its source bucket exist; every pre-existing file printed `skip`.
2. **Top up `CLAUDE.md` — you do it, not the user.** The *script* never rewrites an existing
   `CLAUDE.md` (it never clobbers) and prints a warning. Read the file, add the new block's
   pointer-table rows and its pipeline-skills line, update the "Scaffolded blocks" line and
   `**Phase:**`, then show the diff for confirmation.
   Verify: every path in the pointer table resolves.
3. **Draft the handoff before doing any new work** — the block-specific artefact below. Write a
   complete first version from the old block's own output (for a won bid: the compliance matrix,
   the submitted response in `4_final/`, the RFP's stated dates and deliverables) and present it
   for confirmation. Do not hand the user a blank briefing template. This is what stops the new
   phase from quietly redefining what was agreed in the old one.
4. **Re-baseline the sources** — see the gate. Then resume the normal loops
   (`new-source-arrived`, `rfp-arrived`, `post-workshop`, `deliverable-sprint`).

## Per-transition specifics

| Transition | New block/bucket | The handoff artefact | What must NOT carry |
|---|---|---|---|
| **pursuit → +delivery** (we won) | `02_delivery/` + `engagement/` | `01_pursuit/<ENG-ID>/7_briefing/` — what we won and what we promised: scope, deliverables, dates, binding commitments, assumptions we priced. Delivery scope is read from here, not from memory of the bid. | Bid facts. `pre_award/` claims stay `[T3]`; `engagement/` starts **empty** and gets filled from what the client hands over post-award. |
| **research → +pursuit** (client tenders) | `01_pursuit/` + `pre_award/` | A short scope note in `01_pursuit/<ENG-ID>/2_analysis/` stating which research conclusions are usable and on what basis. | **Anything in `engagement/`.** If the research was done under the client's confidentiality terms, that material — and any conclusion resting on it — cannot enter the bid. Re-source it publicly or drop it. |
| **research → +delivery** (study becomes the engagement) | `02_delivery/` | `00_research/2_output/` — the issued report is the delivery baseline; log it as the starting position in `_pm/engagement_log.md`. | Nothing structurally — same `engagement/` bucket, same constraint. But re-check anything marked `[⚠VERIFY]` before it feeds a deliverable. |
| **delivery → +pursuit** (follow-on tender) | `01_pursuit/` + `pre_award/` | Fresh RFP analysis; treat as a new bid. | **Everything in `engagement/`.** The strongest version of the rule: the material you know best is the material you may not use. Source independently. |

## Stop gates

- **STOP before citing a pre-award claim as an established fact.** Winning does not verify
  anything. A `pre_award/` fact stays `[T3]` until re-established from an `engagement/` source or
  measured from the system. Re-verify, don't re-label. Log the re-baseline in the precedence
  register so the upgrade is auditable.
- **STOP if any `engagement/` material is about to enter a bid** — this bid or a later one, this
  client or another. There is no "we already know it" exception; that is exactly the leak the
  buckets exist to prevent. If a bid needs the fact, it must be sourced independently and filed
  in `pre_award/` or `public/`.
- **STOP if the handoff artefact isn't written.** Starting delivery without the "what we
  promised" briefing is how delivery scope drifts from the sold scope — the single most expensive
  failure mode of a won bid.
- **Do NOT delete or rewrite the old block.** A won bid's `01_pursuit/` is frozen evidence of what
  was committed, not clutter. Same for a research report once delivery starts.

## Anti-goals

Don't fork a second repo per phase (breaks the one audit trail and duplicates `project-context.md`
and `_pm/`). Don't rename the old block's folders to "make room". Don't migrate files between
`_sources/` buckets to save re-verification — moving a file does not change how it was obtained.
