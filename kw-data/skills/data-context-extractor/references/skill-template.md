# Generated Skill Template

Use this template when generating a new data analysis skill. Replace all `[PLACEHOLDER]` values.

---

```markdown
---
name: [company]-data-context
description: "Use when querying or analysing [COMPANY] data in [WAREHOUSE_TYPE] — (1) [PRIMARY_USE_CASE_1], (2) [PRIMARY_USE_CASE_2], (3) [PRIMARY_USE_CASE_3] — or any data question that needs [COMPANY]-specific tables, metrics or terminology."
---

# [COMPANY] Data Analysis

## SQL Dialect: [WAREHOUSE_TYPE]

[INSERT APPROPRIATE DIALECT SECTION FROM sql-dialects.md]

---

## Entity Disambiguation

When users mention these terms, clarify which entity they mean:

[EXAMPLE FORMAT - customize based on discovery:]

**"User" can mean:**
- **Account**: An individual login/profile ([PRIMARY_TABLE]: [ID_FIELD])
- **Organization**: A billing entity that can have multiple accounts ([ORG_TABLE]: [ORG_ID])
- **[OTHER_TYPE]**: [DEFINITION] ([TABLE]: [ID])

**Relationships:**
- [ENTITY_1] → [ENTITY_2]: [RELATIONSHIP_TYPE] (join on [JOIN_KEY])

---

## Business Terminology

| Term | Definition | Notes | Source |
|------|------------|-------|--------|
| [TERM_1] | [DEFINITION] | [CONTEXT/GOTCHA] | [path:line] |
| [TERM_2] | [DEFINITION] | [CONTEXT/GOTCHA] | [path:line] |
| [ACRONYM] | [FULL_NAME] - [EXPLANATION] | | [path:line] |

---

## Standard Filters

Always apply these filters unless explicitly told otherwise:

```sql
-- Exclude test/internal data
WHERE [TEST_FLAG_COLUMN] = FALSE
  AND [INTERNAL_FLAG_COLUMN] = FALSE

-- Exclude invalid/fraud
  AND [STATUS_COLUMN] != '[EXCLUDED_STATUS]'

-- [OTHER STANDARD EXCLUSIONS]
```

**When to override:**
- [SCENARIO_1]: Include [NORMALLY_EXCLUDED] when [CONDITION]

---

## Key Metrics

### [METRIC_1_NAME]
- **Definition**: [PLAIN_ENGLISH_EXPLANATION]
- **Formula**: `[EXACT_CALCULATION]`
- **Source**: `[TABLE_NAME].[COLUMN_NAME]`
- **source:** [path:line]
- **Time grain**: [DAILY/WEEKLY/MONTHLY]
- **Caveats**: [EDGE_CASES_OR_GOTCHAS]

### [METRIC_2_NAME]
[REPEAT FORMAT]

---

## Data Freshness

| Table | Update Frequency | Typical Lag |
|-------|------------------|-------------|
| [TABLE_1] | [FREQUENCY or `unknown — see Open questions`] | [LAG] |
| [TABLE_2] | [FREQUENCY or `unknown — see Open questions`] | [LAG] |

To check data freshness:
```sql
SELECT MAX([DATE_COLUMN]) as latest_data FROM [TABLE]
```

---

## Knowledge Base Navigation

Use these reference files for detailed table documentation:

| Domain | Reference File | Use For |
|--------|----------------|---------|
| [DOMAIN_1] | `references/[domain1].md` | [BRIEF_DESCRIPTION] |
| [DOMAIN_2] | `references/[domain2].md` | [BRIEF_DESCRIPTION] |
| Entities | `references/entities.md` | Entity definitions and relationships |
| Metrics | `references/metrics.md` | KPI calculations and formulas |

---

## Common Query Patterns

### [PATTERN_1_NAME]
```sql
[SAMPLE_QUERY]
```

### [PATTERN_2_NAME]
```sql
[SAMPLE_QUERY]
```

---

## Open questions

Points the files could not settle. Never fill these with guesses.

| # | Question | Owner | Source |
|---|----------|-------|--------|
| 1 | [UNSETTLED_POINT] | [OWNER] | [path:line] |

Source key (optional, for long paths): `[KEY]` = `[LONG_PATH]`

---

## Troubleshooting

### Common Mistakes
- **[MISTAKE_1]**: [EXPLANATION] → [CORRECT_APPROACH]
- **[MISTAKE_2]**: [EXPLANATION] → [CORRECT_APPROACH]

### Access Issues
- If you encounter permission errors on `[TABLE]`: [WORKAROUND]
- For PII-restricted columns: [ALTERNATIVE_APPROACH]

### Performance Tips
- Filter by `[PARTITION_COLUMN]` first to reduce data scanned
- For large tables, use `LIMIT` during exploration
- Prefer `[AGGREGATED_TABLE]` over `[RAW_TABLE]` when possible
```

---

## Customization Notes

When generating a skill:

1. **Fill all placeholders** - Don't leave any `[PLACEHOLDER]` text; use `unknown — see Open questions` for what can't be settled
   - If the data-handling rules bar real/client data, state that rule at the top of the generated skill
   - If the model is proposed, not built, label it so and mark sample queries `[⚠VERIFY vs live database]`
2. **Remove unused sections** - If they don't have dashboards, remove that section
3. **Add specificity** - Generic advice is less useful than specific column names and values
4. **Include real examples** - Sample queries should use actual table/column names
5. **Keep it scannable** - Use tables and code blocks liberally
