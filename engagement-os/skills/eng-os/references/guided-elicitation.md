# Guided elicitation — draft first, ask second, never send the user to an editor

Every artefact in this pack is a **template with a shape**. That shape exists so the *agent* can
fill it, not so a human can be handed a blank form. A step that ends "now open `X.md` and write
the questions" has moved work onto the user that the agent was better placed to do.

## The contract

1. **Draft from what you already have.** The user's invocation text, `project-context.md`, the
   RFP or SOW if one is ingested, the source manifest, the engagement log. Produce a *complete*
   first version — not a skeleton with `<placeholder>` left in.
2. **Show it in the conversation.** Inline, compact enough to read in one screen. The user should
   never have to open a file to see what you propose.
3. **Ask only what you genuinely cannot infer**, and ask it as a small number of concrete
   questions with your recommended answer already stated. "I've assumed X — correct?" beats
   "What should X be?".
4. **Apply their corrections and write the file.** The user's edits happen in conversation; the
   file write is yours.
5. **Say what you assumed.** Anything you inferred rather than were told gets flagged so it can
   be challenged later — and if it's load-bearing and unverifiable, it gets `[⚠VERIFY]`.

## What this does NOT mean

- **It is not "decide for them."** The judgment calls stay the user's — go/no-go, the shape of the
  spine, whether a claim is defensible. What changes is that they *review a proposal* instead of
  *producing one from nothing*.
- **It is not "skip the gate."** A stop gate still stops. Drafting the handoff briefing doesn't
  mean the user isn't asked to confirm it.
- **It is not "guess silently."** An inference you can't support is stated as an inference.

## The three artefacts this most changes

| Artefact | Was | Now |
|---|---|---|
| `.claude/project-context.md` | blank template, user fills 9 sections | drafted from the invocation text + any ingested tender/SOW; user corrects the 2-3 fields that were guessed |
| The spine — `00_research/README.md` §1 questions *(research)* / `3_findings/README.md` backbone *(delivery)* | blank table, user writes 5-8 items | **proposed** from the engagement's scope: RFP requirement clusters, SOW objectives, or the stated research goal. User reshapes; agent writes |
| Held-notes *(post-workshop)* | blank template, user fills in | drafted from whatever raw material exists — transcript, bullet dump, recording notes. User adds what's missing |

## Where the raw material comes from

Before asking the user for anything, look for it:

- **The invocation text itself** — usually carries client, id, name, sector, and the shape of the work.
- **`.claude/project-context.md`** — if a prior command already filled it.
- **An ingested RFP / SOW** — `01_pursuit/<ENG-ID>/1_received/_md/` is the richest source for a
  backbone: the requirement list, the stated limitations, the evaluation criteria.
- **The source manifests** — `_sources/<bucket>/_md/README.md` says what's already in the corpus.
- **`_pm/engagement_log.md`** — what has happened so far.

If the material genuinely isn't there (day 1, nothing ingested), say so and ask — but ask with a
proposal: "No SOW is ingested yet, so I've drafted a backbone from the sector-standard shape for
a data-strategy assessment. Here it is — what's wrong with it?"

## Applies to every eng-* skill

If a skill's workflow contains a step whose instruction to the user is "write", "fill in", or
"set" a file, that step is mis-designed. Rewrite it as: draft → show → ask the residual → write.

The only legitimate exceptions are **judgment gates**, where the deliverable of the step is a
*decision* rather than a document: go/no-go, accepting a red-line, confirming a handoff. Even
there, the agent lays out the options and its recommendation first.
