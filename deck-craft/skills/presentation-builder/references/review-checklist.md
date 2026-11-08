# Deck review checklist

Walk every item against every slide before calling a deck client-ready — the user's own deck, a
colleague's, or one you built. Report each item as yes/no with the slide numbers of every "no" and
the quoted text. Internal decks get the same walk. Each item is a miss the user found after a
review that skipped it (281fabc6, 2026-10-13: "why you follow any best practices? this is shame").

| # | Check | A "no" looks like |
|---|---|---|
| 1 | **Action title** on every content slide — the takeaway sentence, not a topic | "Data landscape", "Next steps" |
| 2 | **Slide number** on every slide except the cover | 12 of 13 slides unnumbered |
| 3 | **Every acronym spelled out** at first use; every code (R/E/N, waves, A-0xx, risk IDs) explained on the slide or removed | "PIM, DPO, DPIA and PPU were never spelled out"; "Wave 2 (R)" with no key |
| 4 | **A key** on every RACI, heatmap and colour-coded table | RACI letters or RAG colours with no legend |
| 5 | **No white text on mid-tone fills** (terracotta, mid-blue, grey) — dark text, or a darker fill | white on terracotta, hard to read |
| 6 | **Options compared on stated criteria before the recommendation** on every decision slide: list → compare → recommend | three options listed side by side, then "we recommend B" with no criteria |
| 7 | **No cross-references or source refs**: no "see slide N", "see the last slide", transcript line refs, § refs, tracker IDs | "(see slide 3)", "[T-14:32]", "§4.2", "RISK-012" |
| 8 | **One message per slide**, and the body proves the title | two takeaways on one slide; body about something the title doesn't claim |

Report:

```
Deck checklist — <file>, <n> slides
1 Action titles        no  · 3, 7 — "Data landscape", "Next steps"
2 Slide numbers        yes
...
```

Then run `deck-verify` (file: opens, editable, fonts, fit) and `client-face-gate` (content hygiene).

Rules:
- The review is findings. A missing purpose, summary or closing slide is a finding with a one-line
  question, never a slide you add. Never restore a slide the user removed, never reorder theirs.
- A "no" without the slide number and the quoted text is not a finding.
