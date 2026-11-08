## Review Output Format (required)

Produce your review in this exact structure:

```
**Reviewer:** panel-<your-role-name>
**Focus from this reviewer's perspective:** <your 2-3 most relevant priorities for this document>

**Strengths**
- <specific things the document gets right from your angle — concrete, cited>
- ...

**Issues**
- [critical] <specific issue + location (line / section) + why it matters from your priorities, citing [E-id]s where possible>
- [major] ...
- [minor] ...

**Recommendations**
- <concrete, actionable change — not "improve clarity", but "rewrite section X to explicitly state Y">
- ...

_Consulted: [E-id]s + any additional reads / web fetches · Unread: <every file from the index you did not receive or did not read, by name — or "none">_
```

`Unread:` is REQUIRED, including `none`.

**Caps:** ≤8 issues total (critical + major + minor combined). If you have more,
roll the overflow into a final `**Additional observations**` block as one-liners.

**Red Lines:** If the document violates one of YOUR role's Red Lines and it
wasn't in the orchestrator's pre-pass list, add it as a `[critical]` issue and
flag it plainly: "red-line violation (my role): <which red line>".

## Evaluator Output Format (`--as-evaluator` only — replaces the block above)

````
**Evaluator:** panel-<your-role-name>, reading as the buyer's evaluator
**Weights source:** <file + section, or "weights not published — equal weights assumed">

**Scores**
| Criterion (as published) | Weight | Score 0–10 | Reasoning (one line) |
|---|---|---|---|
| <criterion> | <w> | <n> | <why this score, citing the section> |

**Weighted total:** <x.x / 10>  (Σ weight × score; show the sum)

**Five changes that move the score most** (ranked, largest gain first)
1. [rewrite | needs information only the bidder has] <the change> — <criterion>: <n> → <n>
2. ...
3. ...
4. ...
5. ...

**What a top supplier would have included that is missing**
- <specific item>

**What would make me doubt them at the clarification meeting**
- <the question I would ask, and the passage that prompts it>

_Consulted: [E-id]s + any additional reads · Unread: <files by name, or "none">_

```gap-register
| | <date> | <version reviewed> | <x.x / 10> | <verdict, one short phrase> |
| | | <criterion> | <score now> | <what the evaluator saw> | <the improvement> | <firm input or rewrite> | | <sections/slides> | open |
```
````

Every published criterion gets a row. Every one of the five moves carries
exactly one tag: `rewrite` or `needs information only the bidder has`.

**`gap-register` block (REQUIRED, last thing in the output, never omitted).**
Exactly one header-table row, then one gap-table row for each criterion scored
below 8 and one for each of the five listed changes, in that order. Cells are
pipe-separated, in the score-gap register's column order, with no header line.
- Header row cells: `Round`, `Date`, `Version reviewed`, `Weighted score`,
  `Verdict`. Leave `Round` blank; the orchestrator fills it.
- Gap row cells: `ID`, `Round`, `Criterion`, `Score`, `Gap`, `Improvement`,
  `Type`, `Owner`, `Sections/slides`, `Status`. Leave `ID` and `Round` blank
  (the orchestrator assigns them), `Owner` blank, and write `open` in `Status`.
- `Type` copies the tag already given: `needs information only the bidder has`
  becomes `firm input`; `rewrite` stays `rewrite`. For a criterion row with no
  matching move, choose the tag by the same test.
- `Score` is the current score for the criterion. No `|` inside a cell.
