# Playbook: deliverable sprint (as-is or to-be)

From "the analysis is ready" to "output shipped". The panel gate is not optional.

**Works in both the delivery and research blocks** — same chain, different paths:

| | delivery block | research block |
|---|---|---|
| The corpus validated in step 1 | `02_delivery/1_discovery/3_findings/` | `00_research/1_analysis/` |
| Mapped against | the findings backbone (`3_findings/README.md`) | the question list (`00_research/README.md` §1) |
| Built into | `02_delivery/<n>_<slot>/` | `00_research/2_output/` |
| Live-file index rev'd in step 5 | `02_delivery/DELIVERABLES.md` | `00_research/README.md` §4 |

## Chain

```
eng-validate-findings ─► panel-discuss ─► eng-build-deliverable ─► panel-review ─► eng-maintain-memory
   sweep first          lock structure      build to skeleton        red-line gate      rev index + log
```

1. **Validate the corpus** → `eng-validate-findings`.
   The deliverable may only consume validated findings. Resolve or explicitly carry
   every open `[⚠VERIFY]` that touches this deliverable's scope.
   Verify: sweep report shows no un-tagged claims in scope; conflicts arbitrated.
2. **Lock the structure** → `panel-discuss` (companion module).
   Agree the skeleton (sections, backbone mapping, what's in/out) before any content.
   Verify: skeleton approved; recorded in the deliverable framework doc.
3. **Build** → `eng-build-deliverable`.
   As-is: pull every finding tagged for this deliverable, group by backbone, add the
   deliverable's own so-what. To-be: derive from remediation cause-tags + research
   (`[T3:OWN]`-tagged), tethered to source facts. Version openly: SKELETON → v0.x → v1.0.
4. **Red-line review** → `panel-review`.
   Multi-role review; every red-line resolved or explicitly deferred with an owner.
   Verify: review record saved; no unresolved red-lines.
5. **Rev the index + memory** → `eng-maintain-memory`.
   The live-file index (see the table above) points at the new version; superseded
   versions archived (never deleted); engagement log records the sprint; memory notes
   any new recurring correction that emerged.

## Stop gates

- **No build before step 1 passes.** Building on unvalidated findings contaminates
  the deliverable with un-arbitrated conflicts.
- **No ship before step 4 passes.** A deliverable that skipped the panel gate is a
  draft, regardless of version number.
- **STOP if scope changed mid-sprint** — back to step 2 (re-lock structure), not
  silent accommodation.
