# E2E — the RESEARCH lane, run against real public material (2026-07-26)

**What we did:** scaffolded a fresh `--mode research` repo (`~/working/deloitte-ai-platform-study`)
and ran the research lane exactly as USAGE.md scenario 1 describes — `/eng-new` → question spine →
source acquisition → ingest → canonicalize → analysis → validate → build → review → v1.0 — on a
real assignment: *what does Deloitte argue an enterprise AI platform must be, what does Deloitte
itself sell, and where do the two diverge.*

**Why this matters:** every prior E2E in this pack has been on the **pursuit** side (GNI 26-002,
several waves). The research block had **never been run end to end**. It shipped on the strength of
`verify_scenarios.py` asserting the tree scaffolds and lints clean — which it does, and which
turned out to be nowhere near sufficient.

**Why this subject:** it forces the two things a bid pack never exercises — sources that are **web
pages rather than files**, and a corpus with **no T1 or T2 anywhere**, where every source is a
vendor describing itself. Both broke something.

## Bugs found by running the flow (all fixed same-day)

| # | Bug | Found by | Fix |
|---|---|---|---|
| 1 | **The research lane had no ingest path for a web page.** `convert_source.py` supported 9 file types, none of them `.html`. A desk study's most common source — a saved product page — hit `ERROR: unsupported type '.html'`. 5 of 11 real sources were blocked, including every one bearing on the "what do they sell" half of the study | trying to ingest the Zora AI product page | `convert_html()` via **defuddle** (reuse — the same tool the `defuddle` skill reads pages with), pandoc as fallback, both registered in `DISPATCH` so `--scan` picks them up automatically |
| 2 | **Cross-document image-name collision silently corrupted provenance.** Extracted images are named per-document (`p6_img1.png`) but a reference pack points *every* document at ONE `_md/images/`. With 11 documents in one bucket, **27 names were claimed by 2–5 documents each**; last writer won. The markdown still rendered, still carried a plausible caption stub, and **showed a different report's figure under our citation.** 146 extracted figures collapsed to 94 on disk. Lint caught only the 1 case where the final writer's copy was later deleted as a within-document repeat — the other 51 were invisible | `media-link-dead` fired once; chasing why one link died exposed that the other 51 had been silently overwritten instead | `ImageCollector(…, prefix=img_prefix(src))` namespaces every extracted image by source stem; `link_for()` tries both forms. Re-ran: **146 files, 0 collisions, 0 dead refs** |
| 3 | **Headings glued to the previous paragraph escaped anchor numbering.** Web markup closes blocks without a break, so the converter emitted `…scales as your needs evolve.#### Zora AI for Finance`. Not at line start = not a heading = **no `## Section N:` anchor = the section cannot be cited**, which is the entire point of ingesting it | reading the first converted product page | unglue pass before `number_headings()`, requiring a non-space before the hashes so a legitimate mid-sentence `#` is untouched |
| 4 | **A freshly scaffolded research repo linted dirty and asserted a vocabulary it did not contain.** `research-README.md.tmpl` §5 says evidence tags and T1/T2/T3 are unchanged "per `_FINDING_STANDARD.md`" — but the standard was a **delivery-only** planted file. Every research repo shipped with a dangling reference *and* no definition of the closed tag set the block claims to obey | `dangling-live-file` on the empty tree, before any work | `FINDING_STANDARD.md.tmpl` now also plants to `00_research/_FINDING_STANDARD.md`. One template, two blocks — the tag set cannot drift between them |
| 5 | **`spine-unfilled` could never go green in a research repo.** The rule scanned the **whole file** for `<placeholder>`, but the research README documents its citation format as `_sources/<bucket>/_md/<file>.md §Page N` and its versioning as `<CLIENT>_<ENG-ID>_…`. With all 8 questions filled, the rule still fired — **on the instructions rather than on the spine** | filling the question list and watching the warning survive | rule narrows to the spine section when the planted heading is found, falls back to whole-file when it isn't |
| 6 | **My own first fix for #5 introduced a worse false positive** — requiring the exact planted heading made the rule warn "section is missing" on any repo whose wording differs, including the test harness's own fixture tree. **The suite did not catch it**; a direct run against fixture-style headings did | building a throwaway tree with the fixture's headings and running lint on it | fallback-to-whole-file instead of warning; two new regression fixtures added (`spine-filled-but-later-sections-still-templated`, `spine-placeholder-inside-the-research-questions-section`) |

**Pattern worth naming, again:** none of these were findable by reading the code. #2 in particular
needs **many documents in one bucket** — the pursuit packs have a handful, so the collision never
had enough surface to show itself. The research lane's normal shape is 10–30 sources per bucket.

## Method-level gaps found (not yet fixed — proposed backlog)

1. **`project-context.md` is the only shared artefact between `eng-scaffold` and `/panel-init`, and
   they use different schemas.** eng-os plants Project Name / Client / Timeline / Scope / Current-State
   Technology / Stakeholder Map / Strategic Pre-Decisions / Compliance / Open Questions. panel-init's
   template and self-check want Key Technology / Known Pain Points / **Project Type** / Reference Pack /
   Inherited Context and a Stakeholder Map with `### Our Side` / `### Client Side` / `### External`.
   **`Project Type` is in panel-init's self-check and eng-os never plants it**, so panel-init either
   fails its own check or overwrites the eng-os file. The eng-os SKILL claims "one SSOT, two consumers";
   the SSOT has no agreed schema. → Reconcile the two templates, or have eng-scaffold plant panel's
   superset.
2. **Only `CLAUDE.md.tmpl` is mode-aware.** 26 of 27 templates have zero `IF:` fences, so
   `project-context.md` in a research repo asks for "Current-State Technology" and a client
   stakeholder map that a desk study does not have. → Extend the `<!--IF:block-->` mechanism to at
   least `project-context.md.tmpl`.
3. **`eng-validate-findings` is delivery-shaped in its own steps.** Step 5 points at
   `0_mobilisation/discovery_questions.md` and step 6 says "backbone coverage" — neither exists in a
   research repo. The *playbook* (`deliverable-sprint.md`) has the delivery↔research mapping table;
   the skill does not, so running the stage directly leaves the operator to improvise. → Put the
   mapping table in the skill, or point the skill at the playbook's table.
4. **`references/delivery/` is a CORE directory**, so a research-only repo gets a delivery-named
   folder for a block it does not have. Minor, but it contradicts the playbook's own "no folders for
   unselected blocks" verification step.
5. **`--mode research` always plants an `engagement/` bucket** that a desk study of published
   material will never fill, and nothing in the pack says what to do with a permanently-empty
   bucket. We annotated it by hand. → Either make the bucket conditional, or have the template say
   "empty is a valid terminal state, record it".
6. **No provenance field for an origin URL existed.** A downloaded PDF's filename does not carry
   where it came from, and a research claim must cite something retrievable. Fixed in passing
   (`--source-url` → `> **Origin URL:**` in the header, all formats), but it was absent by design,
   not by oversight — the pack assumed sources arrive from a client, not from the web.

## What the lane got right

- **The question spine did its job.** Locking 8 questions before ingesting meant every one of 11
  sources landed against a row, and the coverage table in the register wrote itself. Q4 came back
  **`partial` and stayed partial** — no build/buy framework exists in Deloitte's public material,
  and the method reported the absence instead of reconstructing one. That is the behaviour the
  spine exists to produce.
- **The precedence discipline earned its keep on a single-tier corpus.** With no T1 and no T2
  anywhere, the T1>T2>T3 rules are inert — so the register grew three engagement-specific rules
  (*method beats assertion* · *tense is evidence* · *self-publication is not corroboration*). The
  second one caught the run's best finding: all three Zora outcome figures are **targets**
  ("intends", "target", "anticipates"), and trade press had already reported them as achieved.
- **`[⚠VERIFY]` gating worked as designed.** V-2 (the seven Trustworthy AI dimensions are not
  stated verbatim in either ingested primary) kept a list out of the report that every secondary
  source would have supplied. The output says so instead of reproducing it.
- **The apparent 23%-vs-11% contradiction between two Deloitte reports resolved into a
  construct/population mismatch**, both retained, neither superseded — exactly what the conflict
  cluster is for.

## Honest limitations of this run

- **The review gate was a manual multi-lens pass, not a dispatched `panel-review`** (session
  constraint on subagents). Recorded in the review file rather than papered over. 5 red lines were
  still raised and resolved, but one author's lens diversity is not six agents'.
- **12 lint warnings carried, not cleared** — 146 extracted figures untriaged. No claim in the
  output derives from a figure, and the register records the carry as a decision. A vision triage
  of 146 images was judged disproportionate; a real engagement might disagree.
- **Scope shortfall found by the review, not by the method:** the assignment scoped 2023-01→2026-07
  and the earliest source located is April 2024. Nothing in the pipeline compares the *scope
  statement* against the *dates actually ingested*. → candidate lint rule.

## Artefacts

- E2E repo: `~/working/deloitte-ai-platform-study` (kept — rerun target)
- Output: `00_research/2_output/INTERNAL_26-R01_Deloitte-AI-Platform-POV-and-Asset-Study_v1.0.md`
  (3,746 words, 13 sections, every claim cited to a page/section anchor with an origin URL)
- Review record: `panel/reviews/2026-07-26_R1_review_26-R01_v0.1.md`
- Register: `_pm/source_precedence_and_conflict_register.md` (CL-A + V-1…V-6)
- Final gate: `eng_lint.py` **0 errors**, 12 carried warnings; `tests/run_tests.py` and
  `verify_scenarios.py` both green after every fix
