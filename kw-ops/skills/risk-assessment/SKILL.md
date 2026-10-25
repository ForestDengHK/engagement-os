---
name: risk-assessment
description: Use when the user asks "what are the risks", "risk assessment", "risk register", "update the RAID", "what could go wrong", or is weighing the risks of a project, migration, vendor, process or decision.
---

# Risk Assessment

Systematically identify, assess, and plan mitigations for operational risks.

## Risk Assessment Matrix

| | Low Impact | Medium Impact | High Impact |
|---|-----------|---------------|-------------|
| **High Likelihood** | Medium | High | Critical |
| **Medium Likelihood** | Low | Medium | High |
| **Low Likelihood** | Low | Low | Medium |

## Risk Categories

- **Operational**: Process failures, staffing gaps, system outages
- **Financial**: Budget overruns, vendor cost increases, revenue impact
- **Compliance**: Regulatory violations, audit findings, policy breaches
- **Strategic**: Market changes, competitive threats, technology shifts
- **Reputational**: Customer impact, public perception, partner relationships
- **Security**: Data breaches, access control failures, third-party vulnerabilities

## Risk Register Format

For each risk, document:
- **Description**: What could happen
- **Likelihood**: High / Medium / Low
- **Impact**: High / Medium / Low
- **Risk Level**: Critical / High / Medium / Low
- **Mitigation**: What we're doing to reduce likelihood or impact
- **Owner**: Who is responsible for managing this risk
- **Status**: Open / Mitigated / Accepted / Closed
- **Source**: Where the risk was raised or evidenced

## Where it goes in an engagement repo

An engagement-os repo has `_pm/raid_and_decisions.md` — its Risks table **is** the risk register.
Update it in place; never start a separate register.

1. **Read the Risks table first.** A risk already there gets its row updated (likelihood, impact, mitigation, status), not a duplicate.
2. **New risks take the next free ID** in the file's own scheme (`R<n>` in the planted template; follow whatever the file uses).
3. **Keep the file's columns** (`ID | Risk | Likelihood | Impact | Owner | Mitigation | Status`). Don't add columns: start the Risk text with the category (`Compliance: …`) and end it with the citation; write Impact with the matrix level, e.g. `H · Critical`. Likelihood and Impact are `H`/`M`/`L`; status uses the file's lowercase vocabulary (`open` · `mitigated` · `accepted` · `closed`).
4. **Cite the source** in the engagement's style: `[T1:SYS §x]`, `[T2:WS <session> <date>]`, `[T3:REF <source> <loc>]`, `[T3:OWN <source>]`, `[RFP §x]`. A risk whose likelihood rests on an unconfirmed figure gets `[⚠VERIFY vs <source>]`.
5. **An accepted risk is a decision** — add a Decision Log row (`DEC-<n>`) and reference it in the risk's Status.
6. **Log it** with a dated entry at the top of `_pm/engagement_log.md`, following its entry template.

Hand off when the risk belongs elsewhere:
- Risks to **winning or bidding a tender** (deal-breakers, red flags, clarification candidates) → the risks section of the RFP analysis, owned by `eng-rfp-analyze`.
- **Contract** risk (liability, IP, data protection terms) → `review-contract` (kw-legal).
- A risk that changes a current-state **finding** → `eng-write-findings`.

Outside an engagement repo, give the register in the reply and ask where to save it.

## Output

Produce a prioritized risk register with specific, actionable mitigations. Focus on risks that are controllable and material. In an engagement repo, the reply lists what was added or changed, by ID, ordered by level.
