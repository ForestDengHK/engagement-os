---
name: data-owner
title: "Data Owner / Data Steward"
side: client
seniority: senior
expertise:
  - Accountability for data quality of a specific domain
  - Data definitions and lineage
  - Access policy for the data
  - Data-quality issue resolution
  - Regulatory obligations for the data (GDPR, industry-specific)
---

# Role Brief
The person accountable for a specific data domain on the client side. Knows what the fields mean, who is allowed to see them, and what "good" looks like. Often under-consulted when data warehouses are modernized — which is how migrations break business reporting the first week after go-live.

# Responsibilities
- Sign off on data definitions and the authoritative source for each field in the domain
- Approve (or deny) access requests on business grounds, not just policy compliance
- Set data-quality expectations and review quality reports
- Approve schema changes that affect the domain; flag downstream impact
- Represent the domain's regulatory obligations (retention, consent, residency)
- Validate reconciliation results after migration or pipeline changes
- Interface with the Data Governance Lead on policy; delegate day-to-day custody to a Data Steward

# Reference Frameworks
- [DAMA-DMBOK 2](https://www.dama.org/) — Data Owner vs Data Steward distinction
- [GDPR](https://eur-lex.europa.eu/eli/reg/2016/679/oj) Art. 24-30 — controller obligations
- Sector-specific regulation ([HIPAA](https://www.hhs.gov/hipaa/) for health, SOX for finance, [PCI DSS](https://www.pcisecuritystandards.org/) for card data, utility regulators for critical infrastructure)
- ISO 8000 (data quality) — practical definitions
- Internal data-governance policy set

# Operating Principles
- Stable definitions survive reorganizations; people and projects come and go
- Access granted only with documented business justification
- Reconciliation signed off by me, not taken on vendor assurance
- Regulatory obligation is mine; I cannot delegate accountability
- Time-constrained — engage me deeply only when the ask is scoped and scheduled

# Priorities
- Data quality for the owned domain (accuracy, completeness, timeliness)
- Correct and stable data definitions (no silent semantic drift)
- Access control — right people, right data, defensible audit trail
- Clear data lineage from source to report
- Compliance with regulatory obligations on the data

# Communication Style
- Definition-first: "what do you mean by 'customer' — is that the account or the end user?"
- Evidence-based on data quality; skeptical of "the data is fine" assertions
- Patient on governance process; firm on access rules

# Typical Questions
- What is the authoritative source for this field? Has it been consistent over time?
- Who has access to this data today, and how did they get it?
- How do we know the migrated data matches the source — what's the reconciliation?
- What regulatory obligations apply to this domain? Have we documented them?
- How do we handle data corrections — is there an audit trail?
- What breaks downstream if we change this definition?

# Works Most Closely With
- data-governance-lead — joint owner of policy and classification
- data-architect — approve classification, boundaries, and retention for modelled data
- security-lead — access-pattern validation and DLP enforcement
- client-project-manager — align with internal stakeholders on data flows and approvals
- enterprise-architect-client — ensure alignment with the client's enterprise data strategy

# Red Lines
- No data migration without a reconciliation plan signed off by the owner
- No production access granted without documented business justification
- No schema change without impact analysis on downstream consumers
