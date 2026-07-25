---
name: eng-scaffold
description: Use when starting a new consulting / advisory engagement, onboarding an advisory project, or when the user says "set up a new engagement / project repo", "scaffold the consulting project", or names a new client + tender to begin work on. Also use when the repo should cover only part of the lifecycle — bid/RFP only, delivery only, or just a client-materials research base — or when adding a phase to an existing engagement repo.
---

# Scaffolding engagements

Create a new engagement repo that follows the Engagement OS conventions, so every later stage
(ingest → canonicalize → findings → build) has the folders and index files it expects.

## Inputs (ask only if missing)
- **client** — short code (e.g. `ACME`)
- **eng-id** — engagement / tender id (e.g. `27-010`)
- **name** — engagement name (e.g. "Data Platform Strategic Assessment")
- **root** — destination directory (default: `./<client-lower>-<eng-id>`)
- **mode** — which blocks to build (default: `full`) — see below
- **phase** — starting phase label (default: `Mobilisation`)

## Pick the mode first

Not every engagement has both phases. Build only the blocks the work needs — a half-empty
delivery skeleton in a bid repo is noise that rots into wrong navigation.

| The work is… | `--mode` | Work tree | Source buckets |
|---|---|---|---|
| Bid only — respond to an RFP | `pursuit` | `01_pursuit/<ENG-ID>/…` + RFP-analysis / compliance-matrix spine | `public` + `pre_award` |
| Delivery only — we already have the work | `delivery` | `02_delivery/…` + `DELIVERABLES.md` + findings spine | `public` + `engagement` |
| A standalone research assignment — client materials in, a report out | `research` | `00_research/` (questions + `1_analysis/` + `2_output/`) | `public` + `engagement` |
| Bid then deliver (the usual) | `full` *(default)* | both phase trees | all three |

Combine with commas (`--mode pursuit,delivery` ≡ `full`; `--mode research,pursuit` = pre-bid
intelligence feeding a tender). Every mode also gets core: `_pm/`, `CLAUDE.md`,
`project-context.md`, `_sources/README.md`, `archived/`, `references/`, `panel/`.

**Blocks are additive** — when a research repo turns into a bid, or a bid is won, re-run with the
extra block; nothing existing is touched. Ask the user which mode only if the request doesn't
make it obvious.

**Research and delivery share the `engagement` bucket** — in both, the client handed us material
under an engagement's confidentiality terms. Buckets are named for the constraint on the material,
not for the work tree that consumes it, so the same filing rule holds in every mode.

## Workflow

```
Scaffold Progress:
- [ ] 1. Confirm client / eng-id / name / root / MODE
- [ ] 2. Run scaffold_engagement.py (creates tree + plants templates)
- [ ] 3. Fill project-context.md from what's known
- [ ] 4. [research] Write the questions + scope in 00_research/README.md
- [ ] 5. [pursuit]  Ingest the tender pack → eng-rfp-analyze
- [ ] 6. [delivery] Set the backbone in 3_findings/README.md
- [ ] 7. [delivery] Align deliverable slots (prune/rename folders + DELIVERABLES rows)
- [ ] 8. Stand up the panel if installed (/panel-init), else plan a manual review
- [ ] 9. git init + first commit (if not already a repo)
```

**Step 2 — run the scaffolder (deterministic; never clobbers existing files):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/scaffold_engagement.py \
  --root <root> --client <CLIENT> --eng-id <ENG-ID> --name "<name>" \
  --mode <full|research|pursuit|delivery> --phase <phase>
```
Always plants (core): `CLAUDE.md` (pointer table built for the selected blocks),
`.claude/project-context.md`, `_sources/README.md` + the `public/` bucket trio
(SOURCES_GO_HERE + manifest README + SUMMARY + INSIGHTS), `_pm/` (engagement log +
RAID/decisions + source-precedence register), and the cross-session `MEMORY.md` index. Adds per
block: `00_research/README.md` *(research)*; `rfp_analysis.md` + `compliance_matrix.md`
*(pursuit)*; `DELIVERABLES.md` + the findings `_FINDING_STANDARD.md` / `README.md` /
`_TEMPLATE_finding.md` + the discovery-question backlog *(delivery)*. Source buckets follow the
blocks — `pre_award/` for pursuit, `engagement/` for research **or** delivery, planted once even
when both are selected. Placeholders are substituted from the args.

**On an additive re-run**, the scaffolder cannot extend the existing `CLAUDE.md` (it never
clobbers). It prints a warning — add the new block's pointer-table rows and skill list by hand.

**Step 3 — fill `project-context.md`** with whatever is already known (client sector +
regulatory posture, scope / out-of-scope, deliverables, tech stack, stakeholders, pre-decisions).
Leave unknowns under "Open Questions". This file is the shared SSOT that `/panel-init` reuses.

**Step 4 — [research only] settle the questions** in `00_research/README.md`: the bounded,
answerable question list this assignment exists to answer, plus what's explicitly out of scope.
This is the research block's equivalent of the findings backbone — settle it **before** ingesting,
or sourced facts land nowhere and the pack becomes unstructured reading. Our own analysis goes in
`00_research/1_analysis/`, never in `_sources/`.

**Step 5 — [pursuit only] get the tender in.** Convert the RFP pack to anchored markdown into
`01_pursuit/<ENG-ID>/1_received/_md/` via `eng-ingest-source`, then run `eng-rfp-analyze` to fill
the planted `rfp_analysis.md` + `compliance_matrix.md`. Pre-award *background* research (published
strategy, annual reports, market info) goes to `_sources/pre_award/`, not `1_received/`.

**Step 6 — [delivery only] set the backbone** in `02_delivery/1_discovery/3_findings/README.md`:
the fixed, defining problem list for this engagement (RFP limitations / audit objectives /
hypothesis tree / capability gaps). Every finding will map to ≥1 backbone item. This is the one
structural choice that must be made deliberately up front.

**Step 7 — [delivery only] align deliverable slots.** The scaffolder plants the generic
`2_assessment … 6_executive_summary` folders + a D1–D5 `DELIVERABLES.md`. **Prune/rename** these
to *this* engagement's actual deliverables (a small engagement may have one; a big one may add
D6+). Keep the numeric-prefix + fixed D-number map, and update the `DELIVERABLES.md` rows to
match — don't leave half-empty folders and index rows for deliverables that don't exist.

**Step 8 — stand up the review panel (if the Panel Framework is installed).** Do NOT rebuild it —
Engagement OS uses the Panel Framework as a companion. If the `panel-*` skills are present, run
`/panel-init`: `project-context.md` already exists, so it reuses that (one SSOT, two consumers)
and scaffolds `panel-config.yaml` + the roster proposal. **If the panel skills are NOT installed**,
skip this and do a manual multi-lens review before shipping any deliverable (the review gate in
`eng-build-deliverable` still applies).

## Conventions
The full directory tree, the block map, the `_sources/` bucket boundary, naming rules, and the
dual-index discipline live in the `eng-os` skill:
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/directory-conventions.md`. Adjust the deliverable
folder names to this engagement's actual deliverable slots, but keep the numeric-prefix + fixed
D-number map.

## Guardrails
- Idempotent + additive: re-running skips files that already exist — safe on a partial repo, and
  the way to add a block later. Only `CLAUDE.md` needs a manual top-up after an added block.
- **Don't build a block "just in case."** An empty `02_delivery/` in a bid repo sends every later
  skill hunting through folders that will never hold anything.
- **Never pool source material across buckets.** Material under different confidentiality constraints stays apart —
  see the boundary + flow rules in `_sources/README.md` (planted) and directory-conventions.
- Don't hardcode client facts into the templates; they belong in `project-context.md`.
- If the repo already follows these conventions, you don't need this skill — the in-engagement
  skills read the project's own planted files directly.
