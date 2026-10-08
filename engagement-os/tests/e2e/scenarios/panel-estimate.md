# GREEN scenario — panel / rate-card estimate (eng-estimate, `panel` shape)

**Skill loaded:** `engagement-os:eng-estimate` (with `eng-os` references and the `xlsx` skill).
**Fixture:** a scaffolded pursuit repo whose tender is a USD rate-card panel: a role catalogue of
7 seniority bands, 3 delivery-location tiers, a volume discount schedule, one worked example
requested, and **no price formula** in the evaluation table. `2_analysis/estimation.md` is a
hand-written seed with the bands / tiers / roles / discounts / rom / assumptions tables filled and
three reasoning sections written (1. Basis of estimate, 6. Calibration, 11. Re-baseline triggers).

## Task given to a fresh agent (verbatim)

```
Estimate the rate-card panel tender for <ENG-ID>: 7 bands x 3 location tiers, priced in USD,
with one worked ROM for a representative engagement at P50 and P80 and a 15% ceiling.
The tender has no price formula. The seed is 2_analysis/estimation.md.
Build the workbook, recalculate it, and refresh the snapshot. Do not ask me questions.
When done, list every file you created or changed.
```

## Pass criteria (all observable in the files)

1. `estimation.xlsx` was built in the **panel** shape: its sheets are exactly `README`, `Inputs`,
   `RateCard`, `RoleCatalogue`, `Discounts`, `Assumptions`, `WorkedROM`, `Judgement` — no
   `Effort`, `Schedule`, `Gantt`, `Cost` or `Decision`.
2. `RateCard` holds a 7 × 3 grid of formulas (`=$B<n>*<tier>$5` — base × tier index), not typed rates.
3. `WorkedROM` carries P50, P80, contingency, the volume discount, net P50/P80 and a
   not-to-exceed ceiling = net P50 × 1.15 (`Inputs` ceiling cell reads 15%).
4. `Judgement` has a written row for each of the three seed sections, carrying the seed's text;
   the other five read `<not yet written>`. The footer reads `5 of 8 topics unwritten`, not 8.
5. The `xlsx` skill's recalc reports **0 formula errors**.
6. No `€` anywhere in the workbook (values or number formats) or in the refreshed snapshot;
   money renders as `$1,600`-style in `estimation.md`.
7. The refreshed `estimation.md` carries the DO-NOT-EDIT banner and the three reasoning texts —
   the seed's reasoning was not replaced by OWED rows.
8. The Basis of Estimate states the shape (`panel`) and why.

## Fail signals (any one fails the run)

- A `Decision` sheet or a "Marks if lowest" column exists (there is no price formula).
- `Term (weeks)` 26, `Cost marks available` 300 or a `€` header appears anywhere.
- The agent hand-edits the workbook to fix currency, term or marks instead of setting the seed's
  parameters block (or the engine's flags).
- Seed text for a written section is missing from `Judgement`, or the snapshot says `OWED` for it.

## Fixture check (deterministic)

`tests/test_build_estimate_workbook.py` pins criteria 1–6 on a generated 7 × 3 seed:
`python3 -m pytest tests/test_build_estimate_workbook.py -q`.
