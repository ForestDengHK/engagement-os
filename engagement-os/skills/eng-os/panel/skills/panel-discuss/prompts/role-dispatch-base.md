<!-- skills/panel-discuss/prompts/role-dispatch-base.md
Shared PREFIX included in every role-dispatch Task call during /panel-discuss.
Keeping this identical across sibling dispatches maximizes prompt-cache efficiency. -->

# Panel Discussion — Dispatch Context

You are being dispatched by the /panel-discuss orchestrator skill to speak as
your defined panel role. Your persona, tools, and contribution protocol are
already loaded (they come from your agent file at `agents/panel-<role>.md`).

This message provides the shared context for your contribution: the project,
the evidence the orchestrator gathered, the topic, and the goal type. A
role-specific suffix follows this base prefix.

---

## Project context

The following is the user-maintained summary of this engagement. It is the
ground truth for the project, its stakeholders, technology landscape, timeline,
and compliance posture. All contributions must be consistent with this context
unless they explicitly flag disagreement.

```
<<<PROJECT_CONTEXT>>>
```

---

## Evidence Bundle

The orchestrator ran Recon + Bundle before dispatching you. The bundle below
contains excerpts from files the orchestrator identified as relevant to the
topic, with `[E-id]` references you can cite in your contribution. Files are
ranked by relevance. Each excerpt is labeled with its source path and line
range.

```
<<<EVIDENCE_BUNDLE>>>
```

---

## Topic and goal

**Topic:** `<<<TOPIC>>>`

**Goal type:** `<<<GOAL_TYPE>>>`

**Other roles in this panel:** `<<<OTHER_ROLES>>>`

The goal type shapes what is expected of your contribution. See your agent's
Contribution Protocol for Output Format; see the goal-type-specific
instructions appended below.

---

## Prior rounds (if continuing a thread)

```
<<<PRIOR_ROUNDS>>>
```

If this section contains "(none — new thread)", you are contributing to round 1
of a fresh discussion.

---

## Your task

Write your contribution per your agent's Contribution Protocol (Dig Rule,
Grounding Rule, Output Format, Self-check).

The goal-type-specific instructions, appended below this base prefix, tell
you what shape the contribution should take for this discussion's purpose.
