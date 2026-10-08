---
description: A decision or an approval changed — make the drafting follow. Carries every changed value in 3_drafting/commitments.md (or a returned sign-off workbook) into the sections, regenerates the sign-off sheet, rebuilds and verifies the deck, and reopens what needs re-review. Also `export` (send the sign-off workbook) and `import <xlsx>` (read the approvers' answers back).
---

The engine is `${CLAUDE_PLUGIN_ROOT}/skills/eng-os/scripts/sync_commitments.py`. Run it
yourself; never hand the user a script path. The register contract (columns, statuses) is in
`${CLAUDE_PLUGIN_ROOT}/skills/eng-os/references/bid-response.md` §"Unknowns triage".

Arguments (may be empty): `$ARGUMENTS`

- `/eng-sync` — a value or an approval changed in `commitments.md`
- `/eng-sync export` — produce the sign-off workbook to send to the approvers
- `/eng-sync import <xlsx>` — read the returned workbook back, then sync

Add `--eng-id <id>` to the script call when the repo holds more than one pursuit.

**`/eng-sync` (no argument)**

1. `python3 …/sync_commitments.py <repo-root> all` — apply → signoff → rebuild → check --strict.
2. Then `Skill(engagement-os:eng-propagate-change)` for everything the deterministic sync could
   not refresh: a changed value whose surrounding argument no longer holds (a 12-month hold
   the section still justifies as "two budget cycles"), a slide that restates it in other words,
   a drift row whose old value was paraphrased rather than copied, a section reopened to
   `revise-r1` that now needs its review round. The sync swaps strings; it never rewrites an
   argument, and neither do you without that skill's review.
3. Report, in this order: rows synced (ID, old → new); sections reopened (file, status before →
   after); the sign-off sheet path (`3_drafting/signoff_sheet.md` + `.xlsx`); the deck verify
   result (clean, or each finding); deck drift: n misses (a slide states a commitment by calling `commitments.value('C-nn')` from `skills/eng-os/scripts/commitments.py` in the build script; the deck-drift check in `/eng-sync` proves every value on a slide equals the register — each
   `MISS C-nn` is a slide value typed as a literal); drift left (each `C-nn · file · reason`, and what the user
   must decide to close it). "Synced" without the drift line is not a report.

**`/eng-sync export`** — run `signoff`. Tell the user to send `3_drafting/signoff_sheet.xlsx` to
the approvers: they answer `Approved? (Y/N)`, write a `New value` where they want a different
one, and add a `Comment`; nothing else in the workbook is read back.

**`/eng-sync import <xlsx>`** — run `import-xlsx <xlsx>`. It sets `Y` → `approved`, `N` with no
new value → `rejected`, a new value → Value replaced and `changed`, and appends each comment to
Basis as `[reviewer: …]`; then it previews what `apply` would do. Show that preview, then run the
`/eng-sync` flow above. A `rejected` row with no new value cannot be synced — name it and ask the
bid lead for the new value; do not invent one.

Never edit a section by hand to make `check` pass, and never set a status to `approved` that no
approver gave.
