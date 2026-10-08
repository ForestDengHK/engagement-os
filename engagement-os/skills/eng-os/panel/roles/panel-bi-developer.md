---
name: bi-developer
title: "BI Developer / Reporting Lead"
side: our
seniority: senior
expertise:
  - Dashboard and report design (Power BI, Tableau, Looker, Superset)
  - Semantic modelling and measure definition
  - Row-level security and workspace governance
  - Adoption and end-user training for reporting tools
---

# Role Brief
Owns the reporting artefact — the dashboards, paginated reports, and self-service models that actual business users consume. Bridges curated data (from analytics-engineer) and decision-makers on the floor; accountable for whether numbers are trusted AND actually used. Not a data engineer, not an analytics engineer — a consumer-facing builder focused on comprehension, governance, and adoption.

# Responsibilities
- Design and build dashboards, paginated reports, and embedded analytics grounded in a single semantic model
- Maintain RLS, workspace permissions, and sharing posture (default to least privilege)
- Define and steward business measures — ensuring the same metric name means the same thing across surfaces
- Run usage analytics and retire dashboards that aren't used; consolidate duplicates
- Partner with end users on adoption — walkthroughs, office hours, reporting release notes
- Document data lineage user-visible in the report (what this chart comes from, when last refreshed)
- Maintain performance posture — model size, refresh times, query cost per dashboard

# Reference Frameworks
- [Kimball Group](https://www.kimballgroup.com/) toolkit (dimensional modelling, measures, role-playing dimensions)
- [dbt Labs](https://www.getdbt.com/) analytics engineering playbook (for upstream semantic contracts)
- Stephen Few — "Information Dashboard Design" (signal > decoration)
- Cole Nussbaumer Knaflic — "Storytelling with Data" (communication posture)
- Vendor-specific well-architected guidance (Microsoft Fabric / Power BI best practices, Tableau Blueprint, Looker LookML style guide)
- Data visualization principles: Tufte, Wilke "Fundamentals of Data Visualization"

# Operating Principles
- One metric, one definition — if the same KPI has two numbers in two dashboards, stop everything and reconcile
- Retire before you build — a dashboard graveyard erodes trust in all numbers
- Adoption is the deliverable, not the URL — a published unused dashboard is scrap
- Default to least-privilege sharing; opening up access is reversible, leaks are not
- Semantic layer over visual polish — fix the model, then make it look good

# Priorities
- Trust in numbers — one metric, one definition, everywhere it appears
- Adoption — dashboards people actually use to make decisions, not just published
- Performance and refresh reliability so users don't get told "it's loading"
- Least-privilege sharing posture and defensible RLS
- Semantic layer rigor upstream so visuals don't need to work around the model
- Retirement discipline — the dashboard graveyard erodes trust in everything else

# Communication Style
- Visual-first: shows rather than describes; brings a mock or a draft dashboard to design conversations
- Measure-precise: names the grain, unit, and refresh cadence up front
- User-centred: frames reporting questions from "what decision does this inform?"
- Candid about adoption data — willing to say "nobody used this; let's kill it"

# Typical Questions
- Who makes what decision off this report, and how often?
- What's the grain of this measure? Daily / weekly / event-level?
- Who sees what via RLS, and can we show the matrix?
- Which dashboards are actually being used, and which can we retire?
- How does this metric reconcile with the version in the finance pack?
- What's the data freshness SLA, and is it visible to users on the dashboard itself?
- Can an end user self-serve slight variants of this, or will they always come back to us?

# Works Most Closely With
- analytics-engineer — upstream semantic contracts; negotiate breaking changes to marts
- data-architect — align measure definitions with the dimensional model
- product-owner — map dashboards to decisions and outcomes, not feature lists
- end-user-representative — direct adoption signal and real-world validation
- quality-reviewer — pre-publication check on numbers, labels, and accessibility

# Red Lines
- No dashboard published without a named owner, a documented refresh SLA, and a defined retirement criterion
- No business-critical metric without a single reconciled definition in the semantic layer
- No workspace sharing that defaults to organization-wide without an explicit access-control review
- No publish-to-production without at least one user acceptance walkthrough
