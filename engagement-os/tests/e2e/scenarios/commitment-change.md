# GREEN scenario — a decision changes after review (`/eng-sync`)

**Skills loaded:** `engagement-os:eng-os`, the `/eng-sync` command,
`engagement-os:eng-propagate-change`.
**Fixture:** a pursuit repo whose `3_drafting/commitments.md` has `C-07 | Rate hold and indexation
| D | 24 months | 24 months | … | Morgan | pending | 17_global_rate_card.md, 21_commercial_assumptions.md | 6 |`;
`17_global_rate_card.md` at `reviewed-r2`, `21_commercial_assumptions.md` at `reviewed-r1`, both
stating "24 months" in body prose; `3_drafting/_render/rebuild.sh` builds the deck;
`signoff_sheet.xlsx` exported earlier with `/eng-sync export`.

## Task given to a fresh agent (verbatim)

```
Morgan rejected the 24-month hold. She wrote 12 months in the sign-off workbook:
3_drafting/signoff_sheet.xlsx (Approved? = N, New value = 12 months).
Make the response, the sign-off sheet and the deck follow. Do not ask me questions.
Tell me what changed and what still needs a human.
```

## Pass criteria (all observable in the output and files)

1. `/eng-sync import 3_drafting/signoff_sheet.xlsx` ran: C-07 Value is `12 months`, Status
   `changed`, and the preview named both sections with file:line before anything was edited.
2. `apply` rewrote "24 months" → "12 months" in the body of both listed sections — not in the
   frontmatter, not in the review log — and C-07 reads `Applied value = 12 months`,
   Status `decided`.
3. Both sections are `revise-r1`, each with a review-log row
   `R1 (sync) | … | revise | commitment C-07 changed: "24 months" → "12 months"`.
4. `signoff_sheet.md` and `.xlsx` were regenerated and show `12 months` for C-07.
5. The deck was rebuilt through `rebuild.sh` and `verify_deck.py --figures native` reported clean
   on the newest `.pptx` in `_render/`.
6. `check --strict` is clean (no drift, nothing unsynced), and the report lists rows synced,
   sections reopened, the sign-off sheet path, the deck verify result and the drift left.
7. `eng-propagate-change` was invoked for what the swap could not settle (e.g. prose that
   justified 24 months), and no section was hand-edited to make `check` pass.

## Baseline failure (RED, observed 2026-10-07 before `/eng-sync`)

- A rate-hold change was edited by hand in three of the five sections stating it; the sign-off
  sheet and deck kept the old value, and nothing reported the two sections left behind.
