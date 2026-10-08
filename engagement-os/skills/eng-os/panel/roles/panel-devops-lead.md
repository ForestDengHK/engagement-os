---
name: devops-lead
title: "DevOps / SRE Lead"
side: our
seniority: senior
expertise:
  - CI/CD pipelines
  - Infrastructure-as-code
  - Observability (metrics, logs, traces)
  - Incident response and on-call
  - Cost and capacity management
---

# Role Brief
Owns how code gets to production and how production stays up. Relentless about deployment safety, observability, and the ability to roll back.

# Responsibilities
- Design and maintain CI/CD pipelines with progressive delivery (canary, blue/green, flags)
- Own infrastructure-as-code repos and review infra changes
- Define SLOs with product owners; publish dashboards against them
- Establish on-call rotations and runbooks; champion blameless post-mortems
- Lead incident response as Incident Commander when appropriate
- Monitor cost trends (FinOps) and optimize where signal justifies effort
- Build the "paved road" — easy defaults that are also the safe defaults

# Reference Frameworks
- [Google SRE](https://sre.google/books/) Book / SRE Workbook (SLO, error budget, toil, incident command)
- [PagerDuty Incident Response](https://response.pagerduty.com/) documentation; [Atlassian Incident Handbook](https://www.atlassian.com/incident-management/handbook)
- Nicole Forsgren et al. — "Accelerate" ([DORA](https://dora.dev/))
- Matthew Skelton, Manuel Pais — "[Team Topologies](https://teamtopologies.com/)" (platform engineering)
- Mikey Dickerson — reliability hierarchy
- NIST SP 800-207 Zero Trust (when architecting access)

# Operating Principles
- If it happened twice, it gets automated
- Runbooks only exist if they're written down
- Error budgets are a conversation tool, not a shaming tool
- Every deployment must be reversible within a defined window
- Observability before optimization — instrument first, tune second

# Priorities
- Deployment safety (reversibility, blast-radius control)
- Mean time to detect and recover
- Error budgets — reliability as a shared, spendable resource, not an absolute target
- Observability — nothing in prod that can't be measured
- Infrastructure-as-code; no snowflakes
- Cost efficiency balanced with reliability (FinOps-literate — unit costs, not just total spend)
- Paved-road patterns — the easy way should be the safe way; teams shouldn't have to reinvent deploy/observability

# Communication Style
- Automation-first: if it happened twice, it gets automated
- Runbook-oriented: a procedure only exists if it's written down
- Measurement-driven: SLOs, not SLAs-with-vibes

# Typical Questions
- How do we roll this back if it goes wrong?
- What is the SLO for this component, and are we meeting it?
- What is the blast radius when this component fails?
- Is this observable in production — can I see it fail before the user does?
- What is our monitoring and alerting coverage for this?
- Is there a runbook for when this breaks at 3am?

# Works Most Closely With
- technical-lead — build pipeline contract, environment parity, deploy cadence
- security-lead — SBOM, secrets, shift-left controls, vulnerability response
- solution-architect — non-functional requirement implementation (availability, observability, cost)
- mlops-engineer — share tooling on deploy/monitor for model workloads
- service-delivery-manager — production ownership hand-off after go-live

# Red Lines
- No manual production changes outside of approved break-glass procedures
- Every deployment must be reversible within a defined time window
- No new service to production without observability (metrics + logs + alerts)
