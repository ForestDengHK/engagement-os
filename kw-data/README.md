# kw-data

Data analysis skills for consulting engagements, cherry-picked from
[anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) (`data`, commit 33d3dea)
and adapted. No bundled MCP servers: connect your own database tool, or work from files.

| Skill | Use it for |
|---|---|
| `explore-data` | Profile a new table or file — shape, nulls, distributions, quality flags |
| `validate-data` | QA an analysis before it is shared — methodology, calculations, bias |
| `sql-queries` | Write, tune or port SQL; includes Oracle 19c, Microsoft Fabric and Oracle-to-Fabric gotchas (sources in `skills/sql-queries/references/dialect-sources.md`). Model-invoked only |
| `data-context-extractor` | Build or extend a client data-context skill, from a live database or — with none connected — from DDL exports, data dictionaries, column lists, CSVs and Power BI model exports. Writes to the engagement repo's `.claude/skills/<client>-data-context/`, never `~/.claude/skills/` |

**Install:**

```
/plugin marketplace add ForestDengHK/engagement-os
/plugin install kw-data@engagement-os
```

**Invoke:** ask in plain language ("profile this table", "check this analysis before I send it",
"build a data context skill from these DDL exports"), or `/kw-data:explore-data <table or file>`,
`/kw-data:validate-data`, `/kw-data:data-context-extractor`.

**Always-on token cost:** ~392 tokens per session (skill descriptions only; bodies load on invoke, ~2.7k–6.2k each).

Licence: Apache-2.0 — see `LICENSE` and `NOTICE`.
