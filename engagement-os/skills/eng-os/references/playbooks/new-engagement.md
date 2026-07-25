# Playbook: bootstrap a new engagement

Day-1 chain. Produces a repo the other playbooks can run in.

## Chain

```
pick mode ─► eng-scaffold ─► fill context (human) ─► /panel-init ─► first ingest batch
 which        skeleton for    facts only a human      roles + config    (new-source playbook)
 blocks?      those blocks     has
```

0. **Pick the blocks — the one irreversible-ish choice on day 1.**
   `pursuit` (bidding only) · `delivery` (we already have the work) · `research` (understand
   the client's materials, no bid, no delivery) · `full` (both, default). Combine with commas.
   Build only what the work needs — an empty `02_delivery/` in a bid repo sends every later
   skill hunting through folders that will never hold anything. Blocks are additive, so
   under-building is cheap to fix and over-building is not.
1. **Scaffold** → `eng-scaffold` (or run `scaffold_engagement.py --mode <blocks>` directly).
   Creates the tree for the selected blocks and plants their templates.
   Verify: `CLAUDE.md` + `.claude/project-context.md` + `_sources/README.md` + `_pm/` exist;
   per block, `01_pursuit/<ENG-ID>/2_analysis/` spine *(pursuit)* and `DELIVERABLES.md` +
   `3_findings/` backbone + standard *(delivery)*; **no folders for unselected blocks**.
2. **Fill the context a machine can't know** (human, assisted):
   - `project-context.md`: stakeholders, pre-decisions, constraints, funding, contacts.
   - *[delivery]* Findings backbone: the engagement's gap-analysis spine (the N areas every
     finding maps to) — derive from the tender/SOW's requirement list.
   - *[delivery]* `DELIVERABLES.md`: the deliverable list with committed dates.
   - *[pursuit]* `compliance_matrix.md`: one row per RFP requirement (via `eng-rfp-analyze`).
   Verify: no `{{PLACEHOLDER}}` remains in the files the mode planted.
3. **Panel setup** → `/panel-init` (companion module).
   Reads the same `project-context.md` (one SSOT, two consumers); creates roles.
4. **First ingest batch** → run the **new-source-arrived playbook** over the
   tender documents + any client-shared baseline materials.
   Verify: every received doc is in the reference pack with a manifest row;
   canonical summary has its first real content.
5. **Memory start** → `eng-maintain-memory`: first engagement-log entry
   (mobilisation baseline); cross-session memory records the engagement exists
   and where its canonical files live.

## Stop gates

- **Do not ingest before step 2 is done** — the backbone and context determine
  where facts land; ingesting into an empty skeleton produces canonical debt.
- **Do not scaffold a block "just in case."** Add it later with another `--mode` run;
  the only manual top-up is `CLAUDE.md`'s pointer table (the scaffolder warns).
- **Adopt-in-place variant:** if the repo already exists with its own layout, skip
  step 1; plant only the missing convention files (finding standard, source-bucket
  skeleton, DELIVERABLES index) and record the mapping in CLAUDE.md.
