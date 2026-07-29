---
name: eng-bid-respond
description: Use when a validated RFP analysis + sourced research are ready and the bid response must be written, or the user says "draft the bid", "write the tender response", or "answer the RFP". Requirement-driven from the compliance matrix, matches the RFP's mandated format exactly, compliance-first with proof-backed win-themes, every claim traceable to an RFP clause or a cited research finding, through a panel red-team gate before submission — no unsupported claim, no fabricated credential. (Turning the finished sections into the submission FILE is eng-render.)
---

# Writing the bid response

Turn the validated analysis + sourced research into a compliant, persuasive, fully traceable
response. Method: `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/bid-response.md`.
Figures: the `designing-figures` skill owns them — spec before pixels, archetype from the message.

## Prerequisite
Build from a **settled** analysis and a cited research log (`bid_research_log.md`). Settled means
every requirement is extracted into `compliance_matrix.md`, and the
evidence is indexed — **not** that the rows are `met`. Rows close *because* the response answers
them; waiting for a closed matrix would mean never starting. Draft in
`01_pursuit/<ENG-ID>/3_drafting/`; freeze to `4_final/`. Start the section map from
`bid_response_outline.md.tmpl`, and each section file from `bid_section.md.tmpl` — both in
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/templates/`.

**If missing:** no matrix → `Skill(engagement-os:eng-rfp-analyze)`; no research
log → `Skill(engagement-os:eng-bid-research)`. A claim with no cited row cannot survive the traceability gate — lint errors on
a `BR-nnn` no log knows and warns on a section resting on an `open` row.

Before writing or reviewing, invoke `Skill(engagement-os:eng-propagate-change)`. Work only the
sections it identifies. A reviewed section whose content or load-bearing dependency changed is no
longer reviewed even if its frontmatter still says so; the change-impact gate returns it to the
revise state of the round it had reached.

## Workflow

**Content first, format last.** Write and review the content as per-section markdown; only when it
is approved do you render into the buyer's required output. Mixing the two costs both — you trim
an argument to fit a slide before knowing whether the argument is right.

```
Bid Response Progress:
- [ ] 1. Build the section map from the matrix (bid_response_outline.md) — every requirement row
        lands in a written section OR under a named control (a submission control sheet, the
        clarification register, commercial sign-off, contract acceptance). Process obligations and
        accepted terms are not prose questions; inventing a section for them makes the matrix lie.
        A requirement the RFT scores in two places names its primary section and its second one.
        Lint errors if a row appears nowhere at all
- [ ] 2. One MD per section, **one directory per volume** — `3_drafting/sections/v1/`, `v2/`, `v3/`
        — from bid_section.md.tmpl; frontmatter carries marks, scoring basis, page budget, reqs
        answered, figures, evidence. Each volume renders into its own file, which is how the
        buyer's mandated volume split survives into the artefact, and it is what makes a volume
        nobody has started visible. A figure reference from a volume directory is
        `../../figures/F-nn_x.png`. **Draft every volume, not only the scored one:** the pass/fail
        questionnaires (H&S, data protection, information security) are prose answers that must
        exist before the evidence arrives, and lint errors on an outline row marked drafted with
        no file behind it
- [ ] 2b. READ THE BUYER'S RESPONSE SCAFFOLDING FIRST, from the ingested RFT under
        `1_received/_md/` — it is already converted, so nothing re-parses the .docx. A tender
        nearly always supplies its own: numbered questions with Yes / No / N-A options, a
        "TENDERER'S RESPONSE (identify document attached)" box, appendix forms to fill.
        Each section declares which one applies in `response_form`:
          buyer-form: <their file>  the answer IS their form, filled — Appendix 3 reference data
                                    sheet, Appendix 4 CV sheet, the pricing workbook. Fill it with
                                    `Skill(docx)` / `Skill(xlsx)` — or `Skill(document-skills:docx)`
                                    etc. if they are installed as a plugin rather than as personal
                                    skills; `eng-check companions` prints this machine's names —
                                    NEVER re-typeset it in our layout
          buyer-structure           they numbered the questions and gave the answer options —
                                    reproduce their numbering and their wording exactly
          prose                     they gave a response box and a page limit; the answer is our
                                    document, identified in that box
        Inventing a structure where the buyer supplied one is a format non-compliance, and
        format non-compliance is a common auto-reject: the content never gets read.
- [ ] 2c. FILL THE BUYER'S OWN DOCUMENT — for every `buyer-form` **and every `buyer-structure`**
        section, put a working copy in
        `3_drafting/forms/` and fill it there with `Skill(xlsx)` / `Skill(docx)`. A form is often
        **a table inside their RFT** rather than a separate file (a reference data sheet, a CV
        sheet): extract that table into a working copy with `Skill(docx)` and fill it in their
        field order — the labels and the row order are the format they are checking against.
        **Never edit `1_received/`**: that is what they sent, and it is the evidence of what was issued.
        **`buyer-structure` is the same obligation.** Where their document carries the answer
        structure — their headings, their question numbering, their Yes / No / N-A boxes, their
        tables — copy that range out of their file and fill it. Re-drawing it as markdown tables
        looks close and is not: on the worked example the buyer's incident table is 12 rows x 8
        columns (incident type x five years) and the re-drawn one was 5 x 4, so the evaluator
        would have been marking a form we had redesigned.
        The section itself becomes the cover note — what was filled, what is owed, who signs —
        not a prose restatement of the form. On the pack's worked example the entire price
        response was two cells in the buyer's workbook (tenderer name, lump sum) and the first
        draft answered it with 565 words of prose instead. Lint warns while drafting and errors
        once a package is frozen (`buyer-form-not-filled`), and it checks content, not just
        presence: a working copy byte-identical to the original, unresolved `[TBD]` markers,
        and cells still holding the buyer's bare currency placeholder all fire
        (`buyer-form-unfilled-copy` / `buyer-form-tbd-open` / `buyer-form-placeholder-cell`).
        **The cover note must never outrun the form.** "Filled" means every mandatory cell holds
        an answer and the boxes are ticked; anything less is "structure carried, answers owed",
        and the note must say which. On the worked example a transmittal claimed answers were
        written while the form held 119 `[TBD]` markers and zero ticked boxes.
        **One price, transcribed once, in one edit.** When the partner commits the number, the
        same figure lands in the workbook's Decision, the buyer's pricing form, and any Form of
        Tender — in a single edit, and the forms check above verifies no placeholder survives.
        A price that lives in three places without a check will eventually disagree with itself.
- [ ] 2d. VISUAL OPPORTUNITY PASS — before drafting a high-weight section, mark the relationships
        that an evaluator must understand at a glance: three-or-more mappings, a dependent
        sequence, option trade-offs, ownership, architecture or a roadmap. Use a figure when it
        materially reduces evaluator search time; otherwise record why a table or prose is
        clearer. This is a scoring decision, not decoration. A 100+-mark section with a strong
        visual relationship must not silently default to walls of text
- [ ] 3. Draft each section: answer in the buyer's own order; compliance first, exceptions plain;
        build its figures alongside it with the `designing-figures` skill — archetype from the
        message, never a default row of boxes. Three artefacts per figure from ONE html source:
        .html (edit here) + .png (2x, goes in the document) + .pptx (one slide, native shapes,
        so a reviewer can correct it). A figure bound for an A4 *document* keeps the skill's
        canvas and grid but drops slide furniture that the document already provides — the
        section heading and the markdown caption. The editable-master pointer goes on the
        `**Figure source.**` line, never in the caption: the strip removes that line, and a
        caption naming `F-01_x.html` ships our internal filenames to the evaluator
- [ ] 4. Weave the 3–5 win-themes at the high-weight criteria, each backed by a cited log row or
        an indexed firm asset (A-nnn)
- [ ] 4b. EVIDENCE UTILISATION — reverse-check every A-nnn / BR-nnn declared in a section's
        `evidence` or `depends_on`. Record what it contributes and the visible paragraph, table or
        figure where that contribution lands. A method source is not “used” because its id appears
        in frontmatter or Traceability: the reader must be able to see its structure, how it was
        adapted to this buyer, and what it changes in the proposed work. Incorporate it materially
        or remove it from the section; bibliography-only references are false differentiation
- [ ] 5. Traceability: every claim → [RFP §x] / A-nnn / a `closed` research-log row (`BR-nnn`);
        kill any [⚠VERIFY]. Lint reports a section resting on an `open` row and counts every
        unresolved marker while you draft — not for the first time at the freeze. Reconcile the
        matrix after drafting: an honest caveat is not fulfilment. If the buyer asks for an
        outcome, KPI/SLA, credential, signature or referee and the source does not hold it, keep
        `Gap type = proof` and status `partial`/`gap`; never mark it `met` merely because the
        section admits the evidence is absent
- [ ] 6. REVIEW ROUNDS per section, logged in the section's own table:
        R1 panel red-team (does it score?) → R2 experienced human (what only experience sees)
        → R3 final read (cross-section consistency, format, no [⚠VERIFY] left)
- [ ] 7. Run the strict mechanical gate → `Skill(engagement-os:eng-check)` in strict mode.
- [ ] 8. ONLY AFTER IT PASSES, render → `Skill(engagement-os:eng-render)` with the bid profile.
        It strips internal scaffolding and re-checks page counts. Do not assemble by hand here.
- [ ] 9. Verify the actual rendered artefact, then freeze that exact verified submission package
        to 4_final/ + record date; matrix fully closed
- [ ] 10. After all affected sections pass review and the new artefact is verified, checkpoint
         through `Skill(engagement-os:eng-propagate-change)`. A later edit is measured against
         this exact reconciled state.
```

**Watch the `scoring` line.** A section marked **per item** needs self-contained answers per item —
six deliverables scored out of 30 each means six complete answers, and a flowing narrative that
blurs them loses marks six times over.

**Page budgets: per-question or shared?** "Max 5 A4 for 3 questions" is a shared budget; "max 3 A4
per question response" is not. Confusing them always errs toward writing too much.

**Measure the budget in pages, mid-flight, before anything is approved.** The only build that
measures the *submission* page count is the one the gate refuses until every section is approved —
so measure a single section on its own, with the strip applied:

```
python3 .../render_document.py --sections <a dir holding just that section> \
    --out /tmp/pb --name s513 --to pdf --profile bid --force
```

`--force` here is legitimate and it reports everything it overrides (open `[⚠VERIFY]`, unapproved
status) as advisories. The internal review copy is rendered with `--profile plain`, which keeps the
scaffolding — its page count is NOT the buyer's page count.

**Under-use costs marks too.** "The level of detail provided" is an explicit scoring dimension, so
half an unused page budget on a 100+-mark criterion is marks left on the table. Lint warns in both
directions (`section-overlength` / `section-underlength`); the call is yours, but make it a call.

**Requirement-driven, not narrative-driven.** The response is assembled from the compliance
matrix; when every row is `met` and every mandatory satisfied, it's complete. The matrix is the
fact base; the response adds the persuasion.

**Any format they mandate, not just Word.** The response format is theirs to choose, and the pack
routes each kind to the skill that owns it rather than re-implementing it:

| They mandate | The answer is | Owned by |
|---|---|---|
| A document (Word / searchable PDF) | our sections, rendered | `eng-render` → `docx` |
| A workbook (pricing, questionnaire) | **their workbook, filled** in `3_drafting/forms/` | `xlsx` |
| Their Word form (data sheet, declaration) | **their form, filled** in `3_drafting/forms/` | `docx` |
| A deck | a re-cut argument, not a paginated document | `eng-render --to deck-manifest` → `presentation-builder` |
| A web portal with per-question boxes | a transcription pack: one plain-text answer per question id, inside their character limits, plus the attachments | sections stay the source; **you** produce the pack by hand |

The first four are wired. The **portal** case is NOT: no mode, no generator, no character-limit
check exists for it today. If a tender is portal-submission, say so in the outline and treat the
transcription pack as a manual work item with an owner — do not let a rendered `.docx` stand in
for an answer that is never submitted as a file. (Claiming this was wired, before it was, is
exactly the label-with-nothing-behind-it failure this pack exists to catch.)

**Match the buyer's format exactly** — volume split, page/word limits, mandated forms. Format
non-compliance is a common auto-reject; don't impose our own structure. The mandated format is a
**fact from the RFT**, so record it in the outline's `## Submission format (machine-checked)` table
(volumes · accepted file formats · paper · minimum font · separator pages · buyer document label).
The label matters: citation shorthand renders as `(RFP §…)` by default, and a tender whose buyer
calls their document an RFT or an ITT must say so there rather than ship the wrong word.
`eng_lint.py` reads the table: an artefact built in a format the buyer does not accept is an error
under `4_final/`, and a declared volume with no sections is reported. Otherwise the required format
reaches the build only through whatever someone types on the command line — a tender that demands
Word would accept a deck without a word of protest.

## Review rounds (not one gate)
A section is finished when the rounds stop producing changes, not when it is written. Each section
carries its own log, because sections finish at different times.

- **R1 — panel red-team** (`panel-review` if installed, else a manual multi-lens pass): does it
  score? **evaluator's eye** · **legal** (exceptions clean, exposure?) · **finance**
  (priceable/deliverable at margin?) · **architect/delivery** (deliverable as staffed?) ·
  **visual argument** (does the selected form reveal a scoring relationship at A4 size, or is it
  decorative, duplicated prose, or an unreadable mini-slide?) ·
  **evidence utilisation** (does every declared method/case/standard visibly change the answer,
  or is it only named in the bibliography/traceability?).
- **R2 — experienced human.** What only experience sees: a claim that won't survive a client
  conversation, a promise delivery cannot staff, a tone wrong for this buyer.
- **R3 — final read.** Cross-section consistency, format compliance, nothing left `[⚠VERIFY]`.

**Do not collapse R1 and R2** — they fail differently. R1 is structural and can be reasoned about
from the RFT; R2 is judgement and cannot.

## Guardrails
- No unsupported claim, no fabricated credential — ever. Anything `[⚠VERIFY]` is cut or closed first.
- Every mandatory requirement is `met`; exceptions stated openly with rationale.
- Never edit a submitted volume in place — a post-submission change is a new dated version.
- **Never ship a figure as only a flat image.** Review rounds produce figure corrections; a
  reviewer who cannot edit sends the change back as prose. Every figure gets its editable
  one-slide PPTX alongside the PNG, both generated from the same HTML.
- **Look at both outputs.** Round-trip the PPTX back to an image and check the shape count — a
  one-slide export with 1-2 shapes is a screenshot in a wrapper, not an editable figure. Text that
  fits in HTML can clip as a PowerPoint shape.
- **A figure passes only in the final medium.** Inspect the PNG inside the rendered A4 document,
  not only at 1920×1080. If labels require zooming, redesign or use a table/prose. If the figure
  merely repeats the paragraph without making a relationship visible, remove it.
