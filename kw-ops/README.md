# kw-ops

Operations skills cherry-picked from
[anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) (`operations`, commit 33d3dea)
and adapted to engagement-os conventions. No bundled MCP servers.

| Skill | Use it for |
|---|---|
| `change-request` | A change request with impact analysis and rollback plan |
| `process-doc` | A process as RACI + SOP + flowchart, as-is or to-be |
| `risk-assessment` | Likelihood × impact scoring into a prioritised risk register |
| `vendor-review` | Vendor cost (TCO), risk and a recommendation; side-by-side comparisons |

**In an engagement-os repo** the skills write into the established locations, update the existing
`_pm/raid_and_decisions.md` (risks `R<n>`, decisions `DEC-<n>`, change requests `CR-<n>`) instead
of starting parallel registers, cite sources with the engagement's `[T1]/[T2]/[T3]` tags and
`[⚠VERIFY]`, and hand off to the owning `eng-*` skill — e.g. artefact edits to
`eng-propagate-change`, sizing to `eng-estimate`, bid risks to `eng-rfp-analyze`. Elsewhere they
answer in the reply.

**Install:**

```
/plugin marketplace add ForestDengHK/engagement-os
/plugin install kw-ops@engagement-os
```

**Invoke:** "what are the risks", "write a CR for this", "document this process", "compare these
vendors", or `/kw-ops:change-request`, `/kw-ops:process-doc`, `/kw-ops:vendor-review`.

**Always-on token cost:** ~302 tokens per session (skill descriptions only; bodies load on invoke, ~0.8k–1.5k each).

Licence: Apache-2.0 — see `LICENSE` and `NOTICE`.
