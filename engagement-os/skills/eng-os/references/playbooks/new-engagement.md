# Playbook: bootstrap a new engagement

Day-1 chain. Produces a repo the other playbooks can run in.

## Chain

```
eng-scaffold ─► fill context (human) ─► /panel-init ─► first ingest batch (new-source playbook)
  skeleton      facts only a human      roles + config      loop per source doc
                 has
```

1. **Scaffold** → `eng-scaffold` (or run `scaffold_engagement.py` directly).
   Creates the folder tree and plants all templates with placeholders substituted.
   Verify: tree exists; `CLAUDE.md`, `.claude/project-context.md`, `DELIVERABLES.md`,
   `3_findings/` backbone + standard, reference-pack `_md/` skeleton all present.
2. **Fill the context a machine can't know** (human, assisted):
   - `project-context.md`: stakeholders, pre-decisions, constraints, funding, contacts.
   - Findings backbone: the engagement's gap-analysis spine (the N areas every
     finding maps to) — derive from the tender/SOW's requirement list.
   - `DELIVERABLES.md`: the deliverable list with committed dates.
   Verify: no `{{PLACEHOLDER}}` remains in these three.
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
- **Adopt-in-place variant:** if the repo already exists with its own layout, skip
  step 1; plant only the missing convention files (finding standard, reference-pack
  skeleton, DELIVERABLES index) and record the mapping in CLAUDE.md.
