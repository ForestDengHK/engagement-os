# kw-legal

First-pass legal triage for a supplier-side consulting practice, cherry-picked from
[anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) (`legal`, commit 33d3dea)
and adapted. No bundled MCP servers. Not legal advice: the firm's standard terms and its
Risk & Legal / OGC function decide.

| Skill | Use it for |
|---|---|
| `triage-nda` | Classify an incoming NDA GREEN / YELLOW / RED and route it |
| `review-contract` | Clause-by-clause review of an MSA / SOW / contract against the playbook, with redlines and fallbacks |
| `compliance-check` | Which regulations, approvals and risk areas apply to a proposed action |

**Playbook:** the skills read `<project>/.claude/kw-legal.local.md`, then `~/.claude/kw-legal.local.md`.
`templates/kw-legal.local.md` is a DRAFT Irish-practice, supplier-side playbook; every position is
marked "assumption — not yet confirmed by user". Confirm positions there, or copy the file into an
engagement repo's `.claude/` to override it for one client.

**Install:**

```
/plugin marketplace add ForestDengHK/engagement-os
/plugin install kw-legal@engagement-os
```

**Invoke:** "triage this NDA", "review this SOW", or `/kw-legal:triage-nda <file>`,
`/kw-legal:review-contract <file>`, `/kw-legal:compliance-check <initiative>`.

**Always-on token cost:** ~251 tokens per session (skill descriptions only; bodies load on invoke, ~3.6k–4.4k each).

Licence: Apache-2.0 — see `LICENSE` and `NOTICE`.
