# Engagement OS — command cheat sheet

Every scenario, start to finish, as commands. Full reasoning lives in `README.md`; this page is
just the sequence.

**6 commands total.** Each one runs a whole chain, gates included.

| | |
|---|---|
| `/eng-new` | start a repo |
| `/eng-source` | a document arrived |
| `/eng-workshop` | a session ended |
| `/eng-sprint` | ship an output |
| `/eng-rfp` | bid a tender |
| `/eng-upgrade` | the scope grew |

---

## 1. Research only

```
/eng-new       ACME 27-010 "Market & Capability Study" mode=research
               → scaffolds 00_research/ + public/ + engagement/ buckets
               → then write the questions in 00_research/README.md   ← do this before ingesting

/eng-source    ~/Downloads/acme-pack/          (repeat per batch)
/eng-sprint    the research report
```

**3 commands.** Output lands in `00_research/2_output/`, live version recorded in
`00_research/README.md` §4.

---

## 2. Pursuit only (bid an RFP)

```
/eng-new       ACME 27-010 "DWH Strategic Assessment" mode=pursuit
/eng-rfp       ~/Downloads/26-002-tender/
```

**2 commands.** `/eng-rfp` runs the whole bid loop — ingest → compliance matrix → **go/no-go stop**
→ gap research → response → red-team → freeze to `4_final/`.

Optional: `/eng-source` for extra background you gather mid-bid.

---

## 3. Delivery only

```
/eng-new       ACME 27-010 "DWH Strategic Assessment" mode=delivery
               → then set the backbone in 3_findings/README.md      ← do this before ingesting

/eng-source    ~/client-docs/                  (repeat per batch)
/eng-workshop  week_1/session_2                (repeat per session)
/eng-sprint    D1                              (repeat per deliverable)
```

**4 commands**, the middle two on repeat.

---

## 4. Bid then deliver (the usual)

```
/eng-new       ACME 27-010 "DWH Strategic Assessment" mode=full
/eng-rfp       ~/Downloads/26-002-tender/
        ── win ──
/eng-source    ~/client-docs/
/eng-workshop  week_1/session_2
/eng-sprint    D1
```

Same as running scenario 2 then scenario 3 — `mode=full` just builds both trees up front.

---

## 5. Upgrading — the scope grew

One command, whichever direction:

```
/eng-upgrade   bid won, add delivery
/eng-upgrade   research became the engagement, add delivery
/eng-upgrade   client is tendering, add pursuit
```

It re-scaffolds with the added block (nothing existing is touched), tops up `CLAUDE.md`, writes
the handoff, and re-baselines the sources. Then carry on with the new lane's loop above.

**The one thing it will stop you on:** winning verifies nothing. `pre_award/` facts stay `[T3]`
and `engagement/` starts empty. And `engagement/` material can never enter a bid — including a
follow-on tender for the same client.

---

## When you want one stage, not a chain

| | |
|---|---|
| `/eng-os` | the map — which stage owns what |
| `/eng-scaffold` | just create/extend the tree |
| `/eng-ingest-source` | convert **one** document |
| `/eng-update-canonical` | fold a batch into a bucket's summary |
| `/eng-write-findings` | evidence → findings |
| `/eng-validate-findings` | the precedence + `[⚠VERIFY]` sweep |
| `/eng-build-deliverable` | assemble from validated findings |
| `/eng-maintain-memory` | re-index CLAUDE.md / DELIVERABLES |
| `/eng-rfp-analyze` · `/eng-bid-research` · `/eng-bid-respond` | the three bid stages |

Default to the chain commands — they carry the ordering and the stop gates, which is the part
that's easy to skip.

---

## The two things a command won't do for you

1. **Set the spine.** `00_research/README.md` questions *(research)* · `3_findings/README.md`
   backbone *(delivery)*. Settle it before ingesting, or sourced facts land nowhere.
2. **Bucket ambiguous sources.** `/eng-source` asks rather than guessing when it can't tell how a
   document was obtained. Answer it — don't wave it through into `public/`.
