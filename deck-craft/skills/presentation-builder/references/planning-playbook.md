# Planning Playbook — structure the deck BEFORE any slide

Planning is the other half of "Deloitte-looking" output (the first half is `designing-figures`). A deck fails at the storyboard, not the styling. Do this before building (SKILL.md workflow step 5).

## 1. Two logics every deck must pass

- **Vertical logic** (within a slide): the action title is a claim; everything on the slide is evidence *for that claim* — nothing else.
- **Horizontal logic** (across slides): read the titles top to bottom — they alone must tell the whole story and flow. If the title string doesn't argue the case, the structure is wrong.

## 2. Open with SCQA, structure the body as a Pyramid

- **SCQA** frames the opening: **S**ituation (what the audience already accepts) → **C**omplication (what changed / what's at stake) → **Q**uestion (the question that raises) → **A**nswer (your governing thought).
- **Pyramid (Minto):** you *think* bottom-up (findings → groups → answer) but *present* top-down — **lead with the answer**, then the MECE supporting pillars, then evidence. Executives get the point first; detail is earned, not front-loaded.
- **MECE** the pillars: mutually exclusive, collectively exhaustive (e.g. an assessment's findings grouped Secure / Mature / Leverage).
- **Action titles:** every title is a conclusion, never a topic ("Demand is outrunning governance", not "Power BI usage").

## 3. Adapt the spine to the content type

| Deck type | Spine (in presenting order) |
|---|---|
| **Assessment / current-state** | SCQA → governing message → one-page picture → findings grouped MECE by pillar (each: claim + evidence + severity) → maturity/baseline → recommendation direction → the ask |
| **Recommendation / proposal** | Answer (the recommendation) → 3 MECE reasons → evidence per reason → risks/mitigations → plan & ask |
| **Strategy / roadmap** | Situation → options considered → recommended path (why) → phased roadmap → cost/value → decision asked |
| **Status / update** | Headline status → progress vs plan → risks/issues → decisions/asks → next steps |
| **Technical design** | Context/requirements → target architecture → key decisions & trade-offs → NFRs/risks → roadmap |

## 4. Adapt the depth to the audience

- **Executive / board:** answer-first, one governing message, a one-page picture, ≤1 number per point; push detail to an appendix. Shorter is stronger.
- **Technical / working team:** name the technologies, show the traces and the evidence, keep the decisions explicit.
- **Mixed read-out (common in consulting):** a board-defensible executive layer on top, a named-technology technical layer beneath — same deck, layered.

## 5. Storyboard before building (the "ghost deck")

1. Write the **governing message** (one sentence) and the **audience + decision**.
2. Write every **slide title as an action title**; order them; read them straight through as the horizontal logic. Fix the argument here — in text, where it's cheap.
3. Mark each slide **text/table vs figure**; for figures, note the archetype (hand to `designing-figures`).
4. **Get the title outline agreed (gate 1)** before drafting figure specs.
5. Draft figure specs, **review them together (gate 2)**, then build.

## 6. Standard deck skeleton (trim to the content type)

Cover → **Executive summary (the answer)** → one-page picture → [SCQA situation/complication] → MECE body sections (each: section divider + claim slides) → synthesis / maturity / baseline → recommendation → **the ask / next steps** → appendix (evidence, registers, detail).

> Front-load the executive summary: a busy reader who stops after slide 2 should still have your whole answer.
