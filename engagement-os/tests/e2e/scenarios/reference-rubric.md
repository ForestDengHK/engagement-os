# GREEN scenario — reference rubric + network sweep (eng-bid-research → eng-bid-respond)

**Skills loaded:** `engagement-os:eng-bid-research`, then `engagement-os:eng-bid-respond`.
**Fixture:** a pursuit repo for an automotive buyer whose scoring criterion reads "relevance of
references to automotive/manufacturing"; `firm_assets.md` holds a GenAI proof of concept (2025),
an undated data-warehouse migration, and a utility data assessment (2023). Web access available.

## Task given to a fresh agent (verbatim)

```
The tender asks for three client references, scored on "relevance to automotive/manufacturing,
scale, and demonstrated outcomes" [RFP §5.3].
Research what we can cite for this, then choose the three references for section 5.3.
Our indexed assets are in 01_pursuit/_shared/firm_assets.md.
The buyer is an automotive supplier; check what they are planning for the next year too.
Record your reference choice so the bid lead can challenge it.
Do not draft section 5.3 itself yet.
Do not ask me questions.
Log everything you find where the plugin expects it.
When done, list the three references and why.
```

## Pass criteria (all observable in the files)

1. `bid_research_log.md` has ≥ 3 `[T3:OWN]` rows from the network client-story sweep, each with
   client as named publicly, member firm, year, scope, platform, measurable outcome (or "none
   stated") and a URL, with source tier noted.
2. `bid_research_log.md` has ≥ 1 row from the buyer's next-12-months agenda sweep (filing,
   separation/spin-off, segment change, CEO letter or job ad), with URL.
3. `bid_response_outline.md` has a `## Reference selection` table scoring **every** candidate
   (all three indexed assets plus every network story) 0–2 on sector, delivery, recency, outcome,
   nameable, with a total.
4. The chosen three are the top three totals; any tie is broken by naming the buyer's scoring words.
5. The PoC and the undated migration are not chosen unless they out-score every network story.
6. Any network credential chosen is worded "Deloitte network client story, published with the
   client's agreement", and `signoff_sheet.md` names its delivering member firm.

## Baseline failure (RED, observed 2026-10-07 under the previous skill)

- References were picked from what was on disk — a GenAI proof of concept, an undated warehouse
  migration, a utility assessment — for an automotive buyer whose scoring says
  "automotive/manufacturing relevance". Bid lead: "do you think all chosen references are good
  and relevant? I may not think so."
- A public sweep then found Deloitte network client stories (three automotive and
  manufacturing clients) in one hour.
