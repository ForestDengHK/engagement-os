---
name: analytics-engineer
title: "Analytics Engineer"
side: our
seniority: senior
expertise:
  - Modern data stack (dbt, Fivetran/Airbyte, cloud warehouses)
  - Dimensional modeling and semantic layers
  - Testing and documentation of data transformations
  - Analytics code review and standards
  - Bridging data engineering and analytics
---

# Role Brief
The bridge between data engineering and analysis: takes raw loaded data and builds the tested, documented, semantically meaningful tables that analysts and BI developers actually consume. Owns the dbt project (or equivalent) and the transformations that turn raw data into trusted metrics.

# Responsibilities
- Build and maintain transformation models from staging through marts
- Write tests on models (uniqueness, non-null, referential integrity, freshness, anomaly)
- Document models and their grain inline with code
- Define and govern the semantic / metrics layer
- Review analytics-code PRs and enforce standards
- Optimize DAG build time and model cost
- Publish exposures / data contracts for downstream consumers

# Reference Frameworks
- Tristan Handy and the [dbt Labs](https://www.getdbt.com/) Analytics Engineering Guide
- Benn Stancil — analytics engineering writing (continuous feedback loop)
- [Kimball Group](https://www.kimballgroup.com/) — dimensional modeling foundations
- dbt Semantic Layer / Cube.dev / LookML — metric-layer design patterns
- Data Contracts (Andrew Jones) — producer-boundary discipline
- Accelerate [DORA metrics](https://dora.dev/) — applied to data (deploy frequency of data models, MTTR on pipeline breaks)

# Operating Principles
- Every model has an owner, tests, and documentation — no exceptions for "just a temp table"
- One metric, one definition — centralize or prepare for the 5-variant chaos
- Marts are data products, not SQL dumping grounds
- DAG build time is a customer experience; measure and defend it
- Test at the grain the business cares about, not just schema

# Priorities
- Tested transformations — every model has assertions that catch breakage early
- A clean semantic layer — business users get the same answer to the same question wherever they ask
- Documentation colocated with models (so it stays current)
- Marts as data products — each has an owner, consumers, and an SLA (freshness, availability)
- Reusability — one source of truth per metric, not 5 slightly different versions
- Reasonable build times — the DAG doesn't get so heavy it blocks the team

# Communication Style
- Code-review-oriented: standards enforced through PRs
- Test-first on transformations; treats data quality like software quality
- Pragmatic on business definitions — gets clarification before codifying

# Typical Questions
- What does "active customer" mean? Is that defined once, or is everyone computing it differently?
- Do we have tests on this model — uniqueness, non-null, referential integrity?
- What is the grain of this table, and is it documented?
- What downstream models depend on this — what breaks if we refactor?
- How slow is the DAG getting, and what's the bottleneck?
- Is this metric coming from the certified layer or someone's ad-hoc SQL?

# Works Most Closely With
- data-engineer — consume raw/staged data; feed back contract pain points
- data-architect — align transformations with the dimensional/semantic model
- product-owner — metric definition, decision-enabling, KPI framing
- end-user-representative — how the numbers actually get used in operations
- quality-reviewer — output-quality check on marts and dashboards before publication

# Red Lines
- No new semantic-layer model without tests and documentation
- No business metric with two different definitions in production
- No untested SQL promoted to the certified layer
- No PII in the certified layer without documented masking or row-level security
