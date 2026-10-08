# GREEN scenario — buyer-evaluator scoring gate (rfp-arrived playbook, R1b)

**Skills loaded:** `engagement-os:eng-os` (playbook `references/playbooks/rfp-arrived.md`) and
`engagement-os:eng-bid-respond`; panel-framework installed with `/panel-review --as-evaluator`.
**Fixture:** a pursuit repo with all sections at `reviewed-r1`, a published evaluation table of
five weighted criteria in `rfp_analysis.md`, and `signoff_sheet.md` with two priority-1 items open.

## Task given to a fresh agent (verbatim)

```
All sections for <ENG-ID> passed R1. Take the response to submission-ready.
The evaluation criteria and weights are in 2_analysis/rfp_analysis.md.
Do whatever review the playbook requires before R2 and before shipping.
Apply what you can yourself; list what needs the firm.
Record each review pass where the playbook expects it.
Do not render the final artefact if anything blocks it — say what blocks it.
Do not ask me questions.
The partner reviews tomorrow morning.
When done, report the score before and after.
Keep every change in 3_drafting/.
```

## Pass criteria (all observable in the output and files)

1. `/panel-review <sections dir> --as-evaluator` ran over the
   whole response, not per section.
2. The scoring output has one 0–10 score with one line per published criterion, and a weighted total.
3. It lists exactly five changes ranked by score impact, each marked `needs firm input` or `rewrite`.
4. Every `rewrite` item is applied in the sections, and a **second** scoring run is recorded
   showing each applied; the before/after totals are reported.
5. The agent does not render for submission while either priority-1 sign-off item is unconfirmed,
   and names those items as the blocker.

## Baseline failure (RED, observed 2026-10-07 under the previous playbook)

- The most useful review was an ad-hoc "read this as the buyer's evaluator and score it" pass
  (39% → 62% after fixes). It was not in the playbook, so a run following the playbook skips it.
