# kw-legal playbook

> **DRAFT — first-pass triage aid. The firm's standard terms and its Risk & Legal / OGC function decide; confirm every position before relying on it.**

Read by `triage-nda`, `review-contract` and `compliance-check`. Lookup order: `<project>/.claude/kw-legal.local.md`,
then `~/.claude/kw-legal.local.md`. Copy this file into an engagement repo's `.claude/` to override it for one client.

**Context:** supplier side — a professional-services firm's Irish practice (data / AI consulting) contracting
with Irish and EU clients, including public-sector bodies.

**How to read a position:** *Standard* = sign as is (GREEN). *Acceptable fallback* = may be agreed after
negotiation (YELLOW). *Escalate (RED)* = route to Risk & Legal / OGC before anything is agreed.

When a position is confirmed, change its status line to `confirmed by <name>, <YYYY-MM-DD>`.

---

## Contract positions

### 1. Limitation of liability
*Status: assumption — not yet confirmed by user*
- **Standard:** Aggregate cap = fees paid or payable under the relevant SOW in the 12 months before the claim. Mutual exclusion of indirect and consequential loss, loss of profit, and loss of data. Uncapped only for fraud, wilful misconduct, and death or personal injury.
- **Acceptable fallback:** Cap up to 2× those fees; exclusions and uncapped heads unchanged.
- **Escalate (RED):** Cap above 2× fees; any other uncapped head (e.g. data protection, confidentiality, IP); loss of the indirect / consequential, loss-of-profit or data-loss exclusions; no cap at all.

### 2. Indemnities
*Status: assumption — not yet confirmed by user*
- **Standard:** Mutual IP-infringement indemnity only (supplier for its deliverables, client for materials it supplies). No indemnity for client data or for actions taken at the client's direction.
- **Acceptable fallback:** Supplier-only IP-infringement indemnity for deliverables, within the liability cap.
- **Escalate (RED):** Indemnity for breach of contract generally, data breaches, regulatory fines, client data or client-directed actions; any indemnity outside the cap.

### 3. Intellectual property
*Status: assumption — not yet confirmed by user*
- **Standard:** Supplier keeps its pre-existing IP, tools, methods and know-how. Deliverables are assigned (or licensed) to the client on payment. The client gets a licence to background IP embedded in deliverables, to use the deliverables.
- **Acceptable fallback:** Assignment of deliverables on creation rather than on payment, provided background IP stays excluded and licensed.
- **Escalate (RED):** Assignment of pre-existing IP, tools, methods or know-how; work-for-hire wording that captures background IP; any restriction on reusing general know-how.

### 4. Confidentiality
*Status: assumption — not yet confirmed by user*
- **Standard:** Mutual; 3 years; standard carve-outs (public, already known, independently developed, received from a third party without restriction, required by law); return or destroy on request, with an exception for legal hold and legally required retention.
- **Acceptable fallback:** Up to 5 years; longer only for trade secrets while they remain trade secrets.
- **Escalate (RED):** Perpetual for all information; one-way against the supplier when both sides disclose; a missing carve-out; no legal-hold / retention exception.

### 5. Data protection
*Status: assumption — not yet confirmed by user*
- **Standard:** A GDPR Article 28 DPA whenever the supplier processes personal data for the client; supplier acts as processor; sub-processors permitted with prior notice; transfers outside the EEA under the Standard Contractual Clauses.
- **Acceptable fallback:** The client's own DPA, if it meets Article 28; specific (named) sub-processor approval instead of notice.
- **Escalate (RED):** No DPA where personal data is processed; supplier cast as controller or joint controller without a reason; uncapped data-protection liability; transfer or localisation terms the delivery model cannot meet.

### 6. Payment
*Status: assumption — not yet confirmed by user*
- **Standard:** 30 days from invoice.
- **Acceptable fallback:** Up to 60 days (YELLOW).
- **Escalate (RED):** 90 days or more. 61–89 days is not yet defined — treat it as RED until a position is set.

### 7. Acceptance
*Status: assumption — not yet confirmed by user*
- **Standard:** Deliverables are deemed accepted 10 business days after delivery unless the client gives written notice of a material non-conformity with the agreed acceptance criteria.
- **Acceptable fallback:** A longer review window, provided deemed acceptance remains.
- **Escalate (RED):** No deemed acceptance; acceptance at the client's sole discretion; payment tied to outcomes rather than to delivery.

### 8. Warranties
*Status: assumption — not yet confirmed by user*
- **Standard:** Services performed with reasonable skill and care. No fitness-for-purpose, outcome or results guarantees.
- **Acceptable fallback:** Deliverables materially conform to the SOW description for a short period, with re-performance as the remedy.
- **Escalate (RED):** Fitness for purpose; guaranteed outcomes, savings or performance; warranties about the client's own compliance.

### 9. Non-solicitation
*Status: assumption — not yet confirmed by user*
- **Standard:** Mutual, 12 months, limited to personnel directly involved in the engagement; general advertising excluded.
- **Acceptable fallback:** No non-solicitation clause at all.
- **Escalate (RED):** One-way against the supplier; longer than 12 months; covering staff not involved in the engagement; penalties.

### 10. Non-compete and exclusivity
*Status: assumption — not yet confirmed by user*
- **Standard:** None.
- **Acceptable fallback:** None — there is no fallback.
- **Escalate (RED):** Any restriction on working for other clients (including the client's competitors); any exclusivity.

### 11. Termination for convenience
*Status: assumption — not yet confirmed by user*
- **Standard:** Either party on 30 days' written notice; the client pays for work done up to termination.
- **Acceptable fallback:** Client-only termination for convenience on 30 days' notice, still paying for work done.
- **Escalate (RED):** Immediate termination without paying for work done; termination fees payable by the supplier.

### 12. Governing law and courts
*Status: assumption — not yet confirmed by user*
- **Standard:** Laws of Ireland; courts of Ireland.
- **Acceptable fallback:** Another EU member state's law, or England and Wales.
- **Escalate (RED):** Non-European governing law; mandatory arbitration seated outside Ireland.

### 13. Insurance
*Status: assumption — not yet confirmed by user*
- **Standard:** Reference professional indemnity (and other customary) cover; state no amounts.
- **Acceptable fallback:** Confirm cover on request, with amounts provided by Risk & Legal, not in the contract.
- **Escalate (RED):** Specific minimum amounts in the contract; naming the client as an additional insured.

### 14. AI use
*Status: assumption — not yet confirmed by user*
- **Standard:** Supplier may use AI tools in delivery, under the confidentiality and data-protection terms. Client data is not used to train third-party models.
- **Acceptable fallback:** Notify the client of the AI tools used, or use a client-approved tool list.
- **Escalate (RED):** A ban on all AI tools; warranties about AI outputs beyond reasonable skill and care.

### 15. Audit
*Status: assumption — not yet confirmed by user*
- **Standard:** On reasonable notice, at most once a year, at the auditor's own cost, limited to records of the engagement and subject to confidentiality.
- **Acceptable fallback:** An extra audit after a material breach or when a regulator requires it.
- **Escalate (RED):** Unlimited or unannounced audits; supplier pays; access to systems or information about other clients.

### 16. Public sector
*Status: assumption — not yet confirmed by user*
- **Standard:** The Freedom of Information Act 2014 applies to most Irish public bodies: mark commercially sensitive content in bids and contracts, and list it, so it can be considered before any release.
- **Acceptable fallback:** Irish public procurement terms are often non-negotiable. Flag each deviation from these positions, don't redline it; raise it as a clarification question in the tender's query window.
- **Escalate (RED):** A non-negotiable public-sector term that hits a RED position above (e.g. uncapped liability) — escalate before the bid goes in, not after award.

---

## NDA triage criteria

*Status: assumption — not yet confirmed by user*

**GREEN — sign under standard delegation**
- Mutual, or one-way protecting the client's information where only the client discloses
- Confidentiality obligations up to 5 years (trade secrets may be longer)
- All five standard carve-outs present (position 4)
- Return or destroy with a legal-hold / legally required retention exception
- Disclosure permitted to employees, affiliates, professional advisers and subcontractors under equivalent confidentiality
- Laws and courts of Ireland
- No non-solicitation, non-compete, exclusivity, IP licence or assignment, liquidated damages or indemnity

**YELLOW — Risk & Legal review, likely one pass of minor redlines**
- Obligations over 5 and up to 7 years, or perpetual only for trade secrets
- Mutual non-solicitation within position 9 (12 months, involved staff only)
- Another EU member state's law, or England and Wales
- Definition broader than preferred but not capturing public or independently developed information
- One carve-out missing that is easy to add (other than independent development or legal compulsion)
- Workable marking requirements; narrow residuals clause limited to unaided memory
- Minor asymmetry in a mutual NDA

**RED — do not sign; Risk & Legal / OGC full review**
- One-way against the firm when the firm also discloses
- Independent-development or legal-compulsion carve-out missing
- Non-compete, exclusivity or standstill (position 10); non-solicitation beyond position 9
- Perpetual for all information, or more than 7 years
- IP assignment or licence, liquidated damages, or an indemnity
- Audit rights without notice or limits
- Non-European governing law, or mandatory arbitration outside Ireland
- Commercial terms beyond confidentiality — it is not really an NDA
- A public body's standard NDA that cannot be negotiated and conflicts with these criteria — flag it, don't redline

## Routing

*Status: assumption — not yet confirmed by user*
- **GREEN:** sign under the firm's delegation of authority, if the firm's policy allows it for this document type.
- **YELLOW / RED:** send to the firm's Risk & Legal / OGC function with the triage report.
- **Before any contract work:** if the client is (or may become) an audit client of the firm, independence clearance comes first.
