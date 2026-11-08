<!-- skills/panel-review/prompts/reviewer-dispatch-base.md
Shared PREFIX for every reviewer-dispatch Task call during /panel-review. -->

# Panel Review — Dispatch Context

You are being dispatched by the /panel-review orchestrator to critique a
document as your defined panel role. Your persona, tools, and Contribution
Protocol are already loaded from your agent file.

---

## Project context

```
<<<PROJECT_CONTEXT>>>
```

---

## Document under review

**Path:** `<<<DOCUMENT_PATH>>>`
**Focus:** `<<<FOCUS>>>` (one of: quality | completeness | risk | compliance | all)

**File index** (for a directory — every file in the document):

```
<<<FILE_INDEX>>>
```

**Your reading assignment:**

```
<<<READING_ASSIGNMENT>>>
```

Your files are inline below, each headed `<!-- file: <name> -->` — review
them from here; do not re-read them with tools. If more files arrive in a
second pass, return your complete block again, updated.

```
<<<DOCUMENT_CONTENT>>>
```

---

## Evidence Bundle

```
<<<EVIDENCE_BUNDLE>>>
```

---

## Red-line pre-pass results

Red-line violations already detected against this reviewer's Red Lines by the
orchestrator:

```
<<<REDLINE_VIOLATIONS>>>
```

Operating-Principle soft conflicts already detected:

```
<<<PRINCIPLE_CONFLICTS>>>
```

These are inputs — you are free to add more violations/conflicts the orchestrator
missed, but do not duplicate what's listed above. Focus your review on:

- Substantive issues from your role's priorities
- Issues the orchestrator's red-line pre-pass didn't catch (free-text judgment, not regex)
- Recommendations — concrete, actionable changes

---

## Other reviewers in this panel

`<<<OTHER_ROLES>>>`

---

## Your task

Write your reviewer block per your agent's Contribution Protocol (Dig Rule,
Grounding Rule, Output Format, Self-check), adapted to review output structure
appended below. Return the block in this reply — a partial review with its
unread files listed is a result; no block is not.
