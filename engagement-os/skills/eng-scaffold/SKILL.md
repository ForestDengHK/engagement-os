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

| The work is… | `--mode` | You get |
|---|---|---|
| Bid only — respond to an RFP | `pursuit` | core + `01_pursuit/<ENG-ID>/…` + `_sources/pursuit/` + the RFP-analysis / compliance-matrix spine |
| Delivery only — we already have the work | `delivery` | core + `02_delivery/…` + `_sources/delivery/` + `DELIVERABLES.md` + the findings spine |
| Just understand a client's materials | `research` | core only — `_sources/_shared/` + `_pm/` + `CLAUDE.md` + `project-context.md` |
| Bid then deliver (the usual) | `full` *(default)* | both phase blocks |

Combine with commas (`--mode pursuit,delivery` ≡ `full`). **Blocks are additive** — when a
research repo turns into a bid, or a bid is won, re-run with the extra block; nothing existing
is touched. Ask the user which mode only if the request doesn't make it obvious.

## Workflow

```
Scaffold Progress:
- [ ] 1. Confirm client / eng-id / name / root / MODE
- [ ] 2. Run scaffold_engagement.py (creates tree + plants templates)
- [ ] 3. Fill project-context.md from what's known
- [ ] 4. [pursuit] Ingest the tender pack → eng-rfp-analyze
- [ ] 5. [delivery] Set the backbone in 3_findings/README.md
- [ ] 6. [delivery] Align deliverable slots (prune/rename folders + DELIVERABLES rows)
- [ ] 7. Stand up the panel if installed (/panel-init), else plan a manual review
- [ ] 8. git init + first commit (if not already a repo)
```

**Step 2 — run the scaffolder (deterministic; never clobbers existing files):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/scaffold_engagement.py \
  --root <root> --client <CLIENT> --eng-id <ENG-ID> --name "<name>" \
  --mode <full|research|pursuit|delivery> --phase <phase>
```
Always plants (core): `CLAUDE.md` (pointer table built for the selected blocks),
`.claude/project-context.md`, `_sources/README.md` + the `_shared/` bucket trio
(README + SUMMARY + INSIGHTS), `_pm/` (engagement log + RAID/decisions + source-precedence
register), and the cross-session `MEMORY.md` index. Adds per block: `_sources/pursuit/` +
`rfp_analysis.md` + `compliance_matrix.md` *(pursuit)*; `_sources/delivery/` +
`DELIVERABLES.md` + the findings `_FINDING_STANDARD.md` / `README.md` / `_TEMPLATE_finding.md`
+ the discovery-question backlog *(delivery)*. Placeholders are substituted from the args.

**On an additive re-run**, the scaffolder cannot extend the existing `CLAUDE.md` (it never
clobbers). It prints a warning — add the new block's pointer-table rows and skill list by hand.

**Step 3 — fill `project-context.md`** with whatever is already known (client sector +
regulatory posture, scope / out-of-scope, deliverables, tech stack, stakeholders, pre-decisions).
Leave unknowns under "Open Questions". This file is the shared SSOT that `/panel-init` reuses.

**Step 4 — [pursuit only] get the tender in.** Convert the RFP pack to anchored markdown into
`01_pursuit/<ENG-ID>/1_received/_md/` via `eng-ingest-source`, then run `eng-rfp-analyze` to fill
the planted `rfp_analysis.md` + `compliance_matrix.md`. Pre-award *background* research (published
strategy, annual reports, market info) goes to `_sources/pursuit/`, not `1_received/`.

**Step 5 — [delivery only] set the backbone** in `02_delivery/1_discovery/3_findings/README.md`:
the fixed, defining problem list for this engagement (RFP limitations / audit objectives /
hypothesis tree / capability gaps). Every finding will map to ≥1 backbone item. This is the one
structural choice that must be made deliberately up front.

**Step 6 — [delivery only] align deliverable slots.** The scaffolder plants the generic
`2_assessment … 6_executive_summary` folders + a D1–D5 `DELIVERABLES.md`. **Prune/rename** these
to *this* engagement's actual deliverables (a small engagement may have one; a big one may add
D6+). Keep the numeric-prefix + fixed D-number map, and update the `DELIVERABLES.md` rows to
match — don't leave half-empty folders and index rows for deliverables that don't exist.

**Step 7 — stand up the review panel (if the Panel Framework is installed).** Do NOT rebuild it —
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
- **Never pool source material across buckets.** Pre-award and post-award corpora stay apart —
  see the boundary + flow rules in `_sources/README.md` (planted) and directory-conventions.
- Don't hardcode client facts into the templates; they belong in `project-context.md`.
- If the repo already follows these conventions, you don't need this skill — the in-engagement
  skills read the project's own planted files directly.
