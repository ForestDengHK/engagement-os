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
6. **Deliver it in the form the recipient actually needs** → `eng-render`.
   **Ask — never assume markdown is the deliverable.** The sprint has produced reviewed
   markdown; whether that ships as markdown, a document, or a deck is a decision about the
   *recipient*, not about the content, and nobody should have to remember a command to reach it.
   Run the analyse pass first (`--analyse`), read it back, then offer the routes:

   | Recipient needs | Route | Owner |
   |---|---|---|
   | a read-through, a working copy, a repo artefact | stop at markdown — it is already the deliverable | — |
   | a document (page limit, mandated template, portal upload) | `--to docx\|pdf\|both` | `eng-render` |
   | a presentation (steering committee, defence, meeting) | `--to deck-manifest` → `presentation-builder` | `eng-render` → `presentation-builder` |
   | a workbook (cost model, register, data appendix) | **`eng-render` does not own this** — hand to the `xlsx` skill, or `eng-estimate` if it is a priced bid model | `xlsx` / `eng-estimate` |

   Verify: the analyse pass says WOULD BUILD under the right profile; for a deck, the assembled
   `.pptx` passes `verify_deck.py --expect <n>`; the live-file index row records the **shipped**
   format, not just the markdown.

## Stop gates

- **No build before `eng_lint.py` is clean of ERRORs.** Mechanical failures (untagged findings,
  dangling citations, unfilled spine) are cheaper to fix now than after they're in a deck.
- **No build before step 1 passes.** Building on unvalidated findings contaminates
  the deliverable with un-arbitrated conflicts.
- **No ship before step 4 passes.** A deliverable that skipped the panel gate is a
  draft, regardless of version number.
- **STOP if scope changed mid-sprint** — back to step 2 (re-lock structure), not
  silent accommodation.
- **Do not pick the delivered format for the user, and do not default to markdown.** Step 6 is a
  question, not a step you complete on their behalf. Reviewed markdown that nobody can open in a
  steering committee is a sprint that stopped one step early.
