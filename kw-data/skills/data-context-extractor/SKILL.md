---
name: data-context-extractor
description: >
  Use when Claude should learn a client's data estate, or when that knowledge needs extending —
  "create a data context skill", "set up data analysis for our warehouse", "help me create a skill
  for our database", "generate a data skill for <client>", "here is the data dictionary / DDL
  export / column list", "add context about <domain>", "the data skill needs more on <topic>",
  "update the data skill with <metrics/tables/terminology>". Works from a connected database or,
  with none connected, from DDL exports, data dictionaries, ALL_TAB_COLUMNS extracts, CSVs and
  Power BI model exports.
---

# Data Context Extractor

A meta-skill that extracts company-specific data knowledge from analysts and generates tailored data analysis skills.

## How It Works

This skill has two modes:

1. **Bootstrap Mode**: Create a new data analysis skill from scratch
2. **Iteration Mode**: Improve an existing skill by adding domain-specific reference files

Either mode works from a live database connection or, when none is connected, from exported files
(**Files mode**, Phase 1).

**Where the generated skill goes:** the engagement repo's `.claude/skills/<client>-data-context/`
(`<client>` = the client short-code, lowercase). Project-scoped, it loads only in that client's
repo and travels with it. Never write it to `~/.claude/skills/` — one client's data knowledge must
not load in another client's sessions. If the session is not inside the client's engagement repo,
ask which repo it belongs to before writing anything.

---

## Bootstrap Mode

Use when: User wants to create a new data context skill for their warehouse.

### Phase 1: Discovery — Database or Files

**Step 1: Identify the database type**

Ask: "What data warehouse are you using?"

Common options:
- **BigQuery**
- **Snowflake**
- **PostgreSQL/Redshift**
- **Databricks**
- **Oracle Database (e.g. 19c)**
- **Microsoft Fabric (Warehouse / Lakehouse SQL analytics endpoint)**
- **SQL Server / Azure SQL**

Use the connected database's query and schema tools. If unclear, check the available MCP tools in
the current session. **If no database tool is connected, use Files mode below** instead of asking
for access.

**Step 2: Explore the schema**

Use the database's schema tools to:
1. List available datasets/schemas
2. Identify the most important tables (ask user: "Which 3-5 tables do analysts query most often?")
3. Pull schema details for those key tables

Sample exploration queries by dialect:
```sql
-- BigQuery: List datasets
SELECT schema_name FROM INFORMATION_SCHEMA.SCHEMATA

-- BigQuery: List tables in a dataset
SELECT table_name FROM `project.dataset.INFORMATION_SCHEMA.TABLES`

-- Snowflake: List schemas
SHOW SCHEMAS IN DATABASE my_database

-- Snowflake: List tables
SHOW TABLES IN SCHEMA my_schema

-- Oracle: List tables in a schema
SELECT owner, table_name FROM all_tables WHERE owner = 'MY_SCHEMA'

-- Microsoft Fabric / SQL Server: List tables
SELECT table_schema, table_name FROM INFORMATION_SCHEMA.TABLES
```

#### Files mode — no database tool connected

Use when no database query or schema tool is available in the session — common early in an
engagement, before system access is granted — or when the client hands over exports instead of
access. The database path above is unchanged; this replaces Steps 1–2 only, and Phases 2–4 run the
same way.

**Step 1: Gather what exists.** Ask for whichever of these the client can supply:

| Input | What it gives the skill |
|---|---|
| DDL exports (`CREATE TABLE` scripts, `DBMS_METADATA.GET_DDL` output, scripted DDL from SSMS or Fabric) | Tables, columns, types, primary/foreign keys, partitioning, comments |
| Data dictionaries (xlsx / docx / pdf) | Business definitions, owners, allowed values, sensitivity |
| Table/column lists — e.g. Oracle `ALL_TAB_COLUMNS` + `ALL_COL_COMMENTS` extracts | The full column inventory with types, nullability and comments |
| CSV extracts or samples | Grain, value distributions, null rates, test/internal rows (profile them with `explore-data`) |
| Power BI model exports (`.pbit`, `model.bim` / TMDL, a DAX measure list) | Measures → metric definitions, relationships → join paths, display names → business terminology |
| An unbuilt or proposed model (DBML, Mermaid/ERD, model design docs), JSON Schemas, field maps, extraction templates | The intended tables, columns, keys and field lineage |

An unbuilt or proposed model is not a warehouse. The generated skill must label it "proposed, not
built" and mark every sample query `[⚠VERIFY vs live database]`.

If someone with read access can run one query, this Oracle extract gives the column inventory in a
single CSV:

```sql
SELECT c.owner, c.table_name, c.column_id, c.column_name, c.data_type,
       c.data_length, c.data_precision, c.data_scale, c.nullable, cc.comments
FROM all_tab_columns c
LEFT JOIN all_col_comments cc
       ON cc.owner = c.owner AND cc.table_name = c.table_name AND cc.column_name = c.column_name
WHERE c.owner IN ('MY_SCHEMA')
ORDER BY c.owner, c.table_name, c.column_id;
```

**Step 2: Read the files where they live.** In an engagement-os repo, client exports belong under
`_sources/engagement/`; read the `_md/` conversion where one exists (run `eng-ingest-source` first
for a dictionary in pdf/docx/xlsx that has not been converted). Read DDL, CSV and model files
directly. Never edit the originals.

**Check the data-handling rules first.** Before opening or profiling any data file (CSV extract,
sample, xlsx with values), read the engagement's handling rules — `CLAUDE.md`, `README`, any
handling/records notes, NDA/DPA notes. If real or client data must not be used, work from
inventories, dictionaries and schemas only (do not profile with `explore-data`), and state that rule
at the top of the generated skill.

**Step 3: Build the inventory.** From the files, list schemas, tables, columns, types, keys and
comments, then ask the same question as the database path: "Which 3-5 tables do analysts query most
often?"

**Step 4: Record provenance and gaps.** Cite `path:line` (or sheet/page) for every
table, column, metric and term in the generated files; a short-key legend is fine for long paths. Where a system extract (DDL, `ALL_TAB_COLUMNS`) and a
document (dictionary, design doc) disagree, the extract wins. Anything files cannot show — row
counts, refresh frequency, live values — becomes a Phase 2 question, or is marked
`[⚠VERIFY vs live database]` in the generated files until checked. Never copy client values (IDs,
serials, names) into the skill — field names only. When access arrives, re-run
discovery in Iteration Mode against the live database.

### Phase 2: Core Questions (Ask These)

After schema discovery, ask these questions conversationally (not all at once):

**If nobody can be asked** (non-interactive run, no analysts yet, or the user says "just do it"),
answer only from the files and put every unsettled point in the generated skill's `## Open
questions` section, with its owner. Never invent an answer.

**Entity Disambiguation (Critical)**
> "When people here say 'user' or 'customer', what exactly do they mean? Are there different types?"

Listen for:
- Multiple entity types (user vs account vs organization)
- Relationships between them (1:1, 1:many, many:many)
- Which ID fields link them together

**Primary Identifiers**
> "What's the main identifier for a [customer/user/account]? Are there multiple IDs for the same entity?"

Listen for:
- Primary keys vs business keys
- UUID vs integer IDs
- Legacy ID systems

**Key Metrics**
> "What are the 2-3 metrics people ask about most? How is each one calculated?"

Listen for:
- Exact formulas (ARR = monthly_revenue × 12)
- Which tables/columns feed each metric
- Time period conventions (trailing 7 days, calendar month, etc.)

**Data Hygiene**
> "What should ALWAYS be filtered out of queries? (test data, fraud, internal users, etc.)"

Listen for:
- Standard WHERE clauses to always include
- Flag columns that indicate exclusions (is_test, is_internal, is_fraud)
- Specific values to exclude (status = 'deleted')

**Common Gotchas**
> "What mistakes do new analysts typically make with this data?"

Listen for:
- Confusing column names
- Timezone issues
- NULL handling quirks
- Historical vs current state tables

### Phase 3: Generate the Skill

Create the skill at `.claude/skills/<client>-data-context/` in the engagement repo, with this
structure:

```
<client>-data-context/
├── SKILL.md
└── references/
    ├── entities.md          # Entity definitions and relationships
    ├── metrics.md           # KPI calculations
    ├── tables/              # One file per domain
    │   ├── [domain1].md
    │   └── [domain2].md
    └── dashboards.json      # Optional: existing dashboards catalog
```

**SKILL.md Template**: See `references/skill-template.md`

**SQL Dialect Section**: See `references/sql-dialects.md` and include the appropriate dialect notes.

**Reference File Template**: See `references/domain-template.md`

### Phase 4: Write and Deliver

1. Write all files under `.claude/skills/<client>-data-context/` in the engagement repo
2. Run the Quality Checklist below
3. Verify nothing else changed: `git status` when the repo is git; otherwise `touch` a marker file
   before writing and run `find <repo> -newer <marker>` after
4. Give the user a summary of what was captured, with the file paths, and list the open
   `[⚠VERIFY]` items and Open questions

Only if the user wants a portable copy to share outside the repo, package it with
`scripts/package_data_skill.py <skill-folder> [output-dir]` (a `.skill` zip).

---

## Iteration Mode

Use when: User has an existing skill but needs to add more context.

### Step 1: Load Existing Skill

Locate the existing skill at `.claude/skills/<client>-data-context/` in the engagement repo, or ask the user for its folder.

Read the current SKILL.md and reference files to understand what's already documented.

### Step 2: Identify the Gap

Ask: "What domain or topic needs more context? What queries are failing or producing wrong results?"

Common gaps:
- A new data domain (marketing, finance, product, etc.)
- Missing metric definitions
- Undocumented table relationships
- New terminology

### Step 3: Targeted Discovery

For the identified domain:

1. **Explore relevant tables**: Use the database's schema tools to find tables in that domain — or, in Files mode, the newly supplied exports
2. **Ask domain-specific questions**:
   - "What tables are used for [domain] analysis?"
   - "What are the key metrics for [domain]?"
   - "Any special filters or gotchas for [domain] data?"

3. **Generate new reference file**: Create `references/[domain].md` using the domain template

### Step 4: Update

1. Add the new reference file
2. Update SKILL.md's "Knowledge Base Navigation" section to include the new domain
3. Close any `[⚠VERIFY]` items the new evidence settles
4. Summarise the change for the user, with file paths

---

## Reference File Standards

Each reference file should include:

### For Table Documentation
- **Location**: Full table path
- **Description**: What this table contains, when to use it
- **Primary Key**: How to uniquely identify rows
- **Update Frequency**: How often data refreshes (or `unknown — see Open questions`)
- **Key Columns**: Table with column name, type, description, notes
- **Relationships**: How this table joins to others
- **Sample Queries**: 2-3 common query patterns

### For Metrics Documentation
- **Metric Name**: Human-readable name
- **Definition**: Plain English explanation
- **Formula**: Exact calculation with column references
- **Source Table(s)**: Where the data comes from
- **Caveats**: Edge cases, exclusions, gotchas

### For Entity Documentation
- **Entity Name**: What it's called
- **Definition**: What it represents in the business
- **Primary Table**: Where to find this entity
- **ID Field(s)**: How to identify it
- **Relationships**: How it relates to other entities
- **Common Filters**: Standard exclusions (internal, test, etc.)

---

## Quality Checklist

Before delivering a generated skill, verify:

- [ ] SKILL.md has complete frontmatter: `name` = the directory name (`<client>-data-context`), description starting with when to use it
- [ ] Entity disambiguation section is clear
- [ ] Key terminology is defined
- [ ] Standard filters/exclusions are documented
- [ ] At least 2-3 sample queries per domain
- [ ] SQL uses correct dialect syntax
- [ ] Reference files are linked from SKILL.md navigation section
- [ ] Written under the engagement repo's `.claude/skills/`, not `~/.claude/skills/`
- [ ] Every fact cites `path:line` (or its short key)
- [ ] No leftover `[placeholder]`s
- [ ] Open questions are listed
- [ ] No client values copied (IDs, serials, names) — field names only
