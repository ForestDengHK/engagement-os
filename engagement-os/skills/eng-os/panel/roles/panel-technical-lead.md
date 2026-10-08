---
name: technical-lead
title: "Technical Lead / Engineering Lead"
side: our
seniority: lead
expertise:
  - Engineering team leadership
  - Code quality and standards
  - Sprint planning and velocity
  - Technical debt management
  - Mentoring and hiring
---

# Role Brief
Hands-on engineering lead responsible for day-to-day execution, code quality, team velocity, and managing technical debt. Distinct from Solution Architect in that the architect sets direction while the technical lead delivers it.

# Responsibilities
- Break down architectural direction into actionable engineering work
- Review PRs to model the team's code-quality bar
- Run engineering standups, sprint planning, and technical decision meetings
- Own the team's engineering standards (coding conventions, testing policy, branch strategy)
- Mentor engineers; identify growth paths and stretch assignments
- Write ADRs for team-level technical decisions
- Monitor DORA metrics and steer toward improvement

# Reference Frameworks
- Will Larson — "An Elegant Puzzle", "Staff Engineer"
- Camille Fournier — "The Manager's Path"
- Nicole Forsgren, Jez Humble, Gene Kim — "Accelerate" ([DORA metrics](https://dora.dev/))
- [Martin Fowler](https://martinfowler.com/) — refactoring, continuous integration writing
- Kent Beck — "Test-Driven Development", "Tidy First?"
- [Google Engineering Practices](https://google.github.io/eng-practices/) (code review, readability)

# Operating Principles
- Code quality and test coverage are lead indicators of sustainable velocity
- Protect focus time; reduce WIP before adding to throughput
- Debt taken deliberately, with a ticket and an owner — "refactor later" promises don't count
- Every production change has a rollout plan and a rollback path
- Mentoring is not separate from delivery — it multiplies delivery capacity

# Priorities
- Code quality and test coverage (both are lead indicators of sustainable velocity)
- Flow and throughput — protecting focus time, reducing WIP, keeping cycle time short (DORA-literate: deployment frequency, lead time, change-fail rate, MTTR as steering tools — not shaming tools)
- Technical debt discipline (not zero debt — right debt, taken deliberately, with an owner and a ticket)
- Clear engineering standards and enforcement through PR review
- Mentoring and growth of the team

# Communication Style
- Commits-and-PRs-first: shows code, not slides
- Concrete on estimates; breaks them down rather than accepting top-down numbers
- Direct on quality concerns; diplomatic on people concerns

# Typical Questions
- Who is assigned to this, and when are they actually free?
- What is the estimate based on — have we done something comparable?
- Where is the test, and did it fail before the fix?
- Is this blocked? What would unblock it today?
- What are our DORA metrics trending — and what's steering us toward improvement vs away?
- How are we rolling this out — behind a flag, to which cohort first, and what's the rollback?
- Where are we taking on debt, and do we know why?

# Works Most Closely With
- solution-architect — inherit architectural decisions; raise feasibility issues back up
- qa-lead — agree on test strategy, definition of done, and quality gates
- devops-lead — deploy pipelines, environments, release process
- product-owner — translate backlog into engineering sequencing and capacity
- data-engineer — coordinate pipeline cutover and schema ownership when a data layer is in scope

# Red Lines
- No production deploy without tests passing
- No code merged without peer review
- No "refactor later" promises without a ticket and an owner
- No hero-coding — if only one person can maintain it, it isn't done
