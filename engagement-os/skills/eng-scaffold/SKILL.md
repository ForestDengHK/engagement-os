---
name: eng-scaffold
description: Use when starting a new consulting / advisory engagement, onboarding an advisory project, or when the user says "set up a new engagement / project repo", "scaffold the consulting project", or names a new client + tender to begin delivery for.
---

# Scaffolding engagements

Create a new engagement repo that follows the Engagement OS conventions, so every later stage
(ingest → canonicalize → findings → build) has the folders and index files it expects.

## Inputs (ask only if missing)
- **client** — short code (e.g. `ACME`)
- **eng-id** — engagement / tender id (e.g. `27-010`)
- **name** — engagement name (e.g. "Data Platform Strategic Assessment")
- **root** — destination directory (default: `./<client-lower>-<eng-id>`)
- **phase** — starting phase label (default: `Mobilisation`)

## Workflow

```
Scaffold Progress:
- [ ] 1. Confirm client / eng-id / name / root
- [ ] 2. Run scaffold_engagement.py (creates tree + plants templates)
- [ ] 3. Fill project-context.md from what's known
- [ ] 4. Set the backbone in 3_findings/README.md
- [ ] 5. Align deliverable slots (prune/rename folders + DELIVERABLES rows)
- [ ] 6. Stand up the panel if installed (/panel-init), else plan a manual review
- [ ] 7. git init + first commit (if not already a repo)
```

**Step 2 — run the scaffolder (deterministic; never clobbers existing files):**
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/scaffold_engagement.py \
  --root <root> --client <CLIENT> --eng-id <ENG-ID> --name "<name>" --phase <phase>
```
This creates the phased folder tree and plants: `CLAUDE.md`, `.claude/project-context.md`,
`02_delivery/DELIVERABLES.md`, the findings `_FINDING_STANDARD.md` + `README.md` +
`_TEMPLATE_finding.md`, the `_md/` reference-pack trio (README + SUMMARY + INSIGHTS), the
engagement log, the source-precedence register, the discovery-question backlog, and the
cross-session `MEMORY.md` index. Placeholders are substituted from the args.

**Step 3 — fill `project-context.md`** with whatever is already known (client sector +
regulatory posture, scope / out-of-scope, deliverables, tech stack, stakeholders, pre-decisions).
Leave unknowns under "Open Questions". This file is the shared SSOT that `/panel-init` reuses.

**Step 4 — set the backbone** in `02_delivery/1_discovery/3_findings/README.md`: the fixed,
defining problem list for this engagement (RFP limitations / audit objectives / hypothesis
tree / capability gaps). Every finding will map to ≥1 backbone item. This is the one structural
choice that must be made deliberately up front.

**Step 5 — align deliverable slots.** The scaffolder plants the generic `2_assessment …
6_executive_summary` folders + a D1–D5 `DELIVERABLES.md`. **Prune/rename** these to *this*
engagement's actual deliverables (a small engagement may have one; a big one may add D6+). Keep
the numeric-prefix + fixed D-number map, and update the `DELIVERABLES.md` rows to match — don't
leave half-empty folders and index rows for deliverables that don't exist.

**Step 6 — stand up the review panel (if the Panel Framework is installed).** Do NOT rebuild it —
Engagement OS uses the Panel Framework as a companion. If the `panel-*` skills are present, run
`/panel-init`: `project-context.md` already exists, so it reuses that (one SSOT, two consumers)
and scaffolds `panel-config.yaml` + the roster proposal. **If the panel skills are NOT installed**,
skip this and do a manual multi-lens review before shipping any deliverable (the review gate in
`eng-build-deliverable` still applies).

## Conventions
The full directory tree, naming rules, and the dual-index discipline live in the `eng-os`
skill: `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/directory-conventions.md`. Adjust the deliverable folder names to this
engagement's actual deliverable slots, but keep the numeric-prefix + fixed D-number map.

## Guardrails
- Idempotent: re-running the scaffolder skips files that already exist — safe on a partial repo.
- Don't hardcode client facts into the templates; they belong in `project-context.md`.
- If the repo already follows these conventions, you don't need this skill — the in-engagement
  skills read the project's own planted files directly.
