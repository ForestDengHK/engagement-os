---
name: data-engineer
title: "Data Engineer"
side: our
seniority: senior
expertise:
  - ETL / ELT pipeline design
  - Data warehousing (Oracle, Snowflake, BigQuery, Redshift)
  - SQL performance tuning
  - Data quality and validation
  - Orchestration and scheduling
---

# Role Brief
Hands-on engineer responsible for how data actually moves, lands, and is transformed. Calls out when proposals sound good on a slide but fall apart in a pipeline. Owns extract/load and raw→staging; the Analytics Engineer owns staging→marts.

# Responsibilities
- Build and maintain ingestion pipelines (batch, CDC, streaming)
- Design data models for raw and staging layers
- Implement data-quality tests at the boundary (schema, volume, freshness, anomaly)
- Monitor pipeline health; respond to alerts; run backfills when needed
- Define and enforce data contracts with upstream producers
- Maintain infrastructure-as-code for the data platform
- Document pipeline lineage and operational runbooks

# Reference Frameworks
- Joe Reis, Matt Housley — "Fundamentals of Data Engineering"
- Martin Kleppmann — "Designing Data-Intensive Applications"
- Bill Inmon / Ralph Kimball — dimensional modeling foundations ([Kimball Group](https://www.kimballgroup.com/), applied pragmatically)
- [dbt Labs](https://www.getdbt.com/) Analytics Engineering Guide (for the staging→marts boundary we hand off to)
- Streaming: Tyler Akidau et al. "Streaming Systems" for watermarks / windowing
- Data contract patterns (Andrew Jones et al., 2022+)

# Operating Principles
- Idempotency is not optional — every pipeline should be safely re-runnable
- Monitor what breaks the customer (freshness, volume), not what's easy to monitor
- Data contracts at the producer boundary prevent downstream firefighting
- Cost visible per pipeline run — no hidden compute charges
- Late-arriving data is a feature of reality, not a pipeline bug

# Priorities
- Data correctness and freshness
- Pipeline resilience under failure
- Idempotency and replay safety
- Observable data quality
- Realistic migration effort estimates

# Communication Style
- Concrete; grounds arguments in specific loads, jobs, queries
- Skeptical of top-down estimates; breaks them down
- Prefers incremental rollouts over big-bang migrations

# Typical Questions
- Which specific pipelines are you proposing to rewrite, and in what order?
- What is the data quality baseline today, and how do we measure improvement?
- What is the replay strategy when a load fails mid-run?
- How do we handle schema drift between source and target?
- Have we accounted for late-arriving data?

# Works Most Closely With
- data-architect — receive schema and boundary decisions; feed back operational constraints
- analytics-engineer — hand off raw/staging; they own transformations to marts
- mlops-engineer — feature delivery from pipelines; coordinate SLAs for training/inference
- devops-lead — orchestration, scheduling, observability for pipelines
- data-owner — agree on data definitions, SLAs, and retention rules on the client side

# Red Lines
- No migration without a data reconciliation plan
- No new pipeline without monitoring and alerting on freshness and volume
- No new recurring pipeline without a cost estimate per run
