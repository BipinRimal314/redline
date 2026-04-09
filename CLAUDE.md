# Redline — Compliance Documentation Linter

Deterministic compliance documentation linter. 95 rules across 17 regulations. Every flag traces to a specific rule, which traces to a specific regulation paragraph. Zero LLM cost at runtime.

## Critical Rules

### Compliance Verification Gate
Every regulation rule must satisfy ALL of these before shipping:
1. `regulation_paragraph` citing the exact section (e.g., "§164.312(a)", "Article 6")
2. Description must match what the cited paragraph actually says — no paraphrasing that injects terms not in the regulation
3. If a concept comes from implementation guidance (NIST 800-88, PCAOB AS 2201) rather than the cited statute, cite the guidance source, not the statute
4. Vale rules must have tokens that catch real compliance issues, not common legal language

**Background:** Spot-check audit (2026-04-07, 10 of 85 rules) found 1 fabricated rule, 6 imprecise rules. Details below.

### Audit Findings (Fixed 2026-04-07)

| Rule | Issue | Resolution |
|------|-------|-----------|
| GDPR-02 | Cited Article 7 but consent definition is Article 4(11) | Now cites both Article 4(11) and Article 7 |
| GDPR-05 | Said "30-day timeline" — GDPR says "one month" | Fixed to "one-month timeline" with Article 12(3) citation |
| GDPR-08 | Presented 72-hour deadline as absolute | Added "where feasible" qualifier per Article 33(1) |
| HIPAA-01 | Bundled Required + Addressable equally | Distinguishes Required (unique user ID, emergency access) from Addressable (auto logoff) |
| HIPAA-07 | Injected "role-based access criteria" | Rewritten to §164.514(d)(2) language: persons/classes + PHI categories |
| HIPAA-09 | **Was fabricated** — attributed NIST 800-88 to HIPAA | Rewritten to actual §164.310(d)(2)(i-ii): disposal + media re-use |
| SOX 404-05 | Attributed PCAOB AS 2201 concepts to statute | Now cites both 15 USC 7262(a) and PCAOB AS 2201 separately |

### Full Audit: GDPR + HIPAA (2026-04-08)

All 10 GDPR and 10 HIPAA rules audited against primary sources (Regulation EU 2016/679 and 45 CFR Part 164).

**GDPR (10 rules): All verified correct.** No changes needed beyond the 3 fixes from the spot-check.

**HIPAA (10 rules): 3 additional fixes.**

| Rule | Issue | Resolution |
|------|-------|-----------|
| HIPAA-05 | "with defined timelines" injected — §164.308(a)(6) does not mandate specific timelines | Rewritten to match regulation language: identify, respond, mitigate, document |
| HIPAA-06 | "delivery frequency, and completion tracking" injected — not in §164.308(a)(5) | Rewritten to cite the Standard (Required) and four Addressable implementation specs |
| HIPAA-10 | "backup schedules", "recovery time objectives", "testing frequencies" injected | RTOs are not a HIPAA term. Rewritten to cite Required (backup, recovery, emergency mode) vs Addressable (testing, criticality analysis) |

### Full Audit: SOX + BSA-AML (2026-04-08)

All 11 SOX rules (section-302, section-404, pcaob-standards) and 15 BSA-AML rules (aml-program, cdd, ctr, sar) audited against primary sources.

**SOX (11 rules): All 11 fixed.** Every rule was missing `regulation_paragraph`. Additional issues:

| Rule | Issue | Resolution |
|------|-------|-----------|
| 302-01/02/03 | `authority` was "PCAOB" — Section 302 is a statutory requirement, SEC implements it | Changed authority to "SEC"; added `regulation_paragraph` citing 15 USC 7241(a) subsections |
| 302-01 | Description was generic ("precise and legally compliant") | Rewritten to reference the specific certification statements required by 15 USC 7241(a)(1)-(6) |
| 404-01/02/03/04 | `authority` was "PCAOB" — Section 404 management assessment is SEC's domain | Changed authority to "SEC"; added `regulation_paragraph` for each |
| 404-03 | Said "must not contain indicators of material weakness" — misleading | Rewritten: the issue is detecting language suggesting undisclosed weaknesses, not prohibiting disclosure |
| 404-04 | No source citation for test procedure requirements | Now cites PCAOB AS 2201.42-61 and notes it's an auditor standard that management follows |
| PCAOB-03 | Cited AS 2201 but the "experienced auditor" standard is from AS 1215.04 | Fixed cfr_reference to include AS 1215; regulation_paragraph now cites AS 1215.04 |

**BSA-AML (15 rules, not 13 as originally counted): All 15 fixed.** Every rule was missing `regulation_paragraph`. Additional issues:

| Rule | Issue | Resolution |
|------|-------|-----------|
| AML-01 | Called CIP a BSA/AML "pillar" under 31 CFR 1020.210 — CIP is a separate regulation (31 CFR 1020.220) | Now distinguishes four pillars (1020.210) from CIP (1020.220, USA PATRIOT Act Section 326) |
| AML-03 | Presented risk assessment as a regulatory requirement — it's FFIEC/FinCEN guidance, not statute | Description now clarifies this is a regulatory expectation, not a statutory requirement |
| AML-04 | Same guidance-vs-statute conflation as AML-03 | Now cites FFIEC BSA/AML Examination Manual and FinCEN advisories |
| CDD-01 | Conflated CDD and CTR concepts ("thresholds, structuring") under 31 CFR 1010.230 | Rewritten to CDD-specific elements: beneficial ownership, nature/purpose of relationships, ongoing monitoring |
| CTR-01 | Labeled as "CDD/CTR elements" — these are CTR-specific requirements | Rewritten as CTR-specific: $10,000 threshold (1010.311), aggregation (1010.313), structuring (31 USC 5324), exemptions (1020.315) |
| SAR-07 | Missing citation for confidentiality provision | Now cites 31 USC 5318(g)(2) and 31 CFR 1020.320(e) |

### Full Audit: FINRA + SEC (2026-04-08)

All 10 FINRA rules (rule-2111, rule-2210, rule-3110) and 9 SEC rules (adv-filing, marketing-rule) audited against primary sources (FINRA Rules 2111/2210/3110, 17 CFR 275.206(4)-1, 17 CFR 279.1, Investment Advisers Act of 1940).

**FINRA (10 rules): All 10 fixed.** Every rule was missing `regulation_paragraph`. Additional issues:

| Rule | Issue | Resolution |
|------|-------|-----------|
| 2111-01 | Description said "must not suggest universal suitability" -- too vague, did not mention Reg BI carve-out | Rewritten to cite Rule 2111(a) investment profile requirement; notes Reg BI (Rule 15l-1) applies to retail customers |
| 2111-02 | Description was generic "reasonable-basis suitability analysis" | Now specifies all three suitability obligations: reasonable-basis, customer-specific, quantitative |
| 2210-01 | Description was generic "exaggerated, misleading, or prohibited claims" | Rewritten to use Rule 2210(d)(1)(B) exact language: "false, exaggerated, unwarranted, promissory or misleading" |
| 2210-03 | Said "predictions of specific future performance are prohibited" -- missed the three exceptions | Now notes exceptions for mathematical illustrations, investment analysis tools, and research report price targets |
| 2210-04 | Said "include appropriate disclaimers" -- vague | Rewritten to cite Rule 2210(d)(1)(F) no-recurrence implication + Rule 2210(d)(2) past recommendations list requirements |
| 2210-05 | Said "approved by a principal" -- generic | Now specifies "registered principal before the earlier of use or filing" per Rule 2210(b)(1)(A) |
| 3110-01 | Said "must not contain prohibited claims" -- conflated content standards (Rule 2210) with supervision (Rule 3110) | Clarified: this lints supervisory procedures documents for precision, grounded in Rule 3110(a)-(b) |
| 3110-02 | Was vague "describe supervisory system including designation of supervisory personnel" | Now specifies OSJ designation, registered person assignment, and supervisory controls per Rule 3110(a)(1)-(5) and (b)(1)-(2) |
| 3110-03 | Was vague "address review of correspondence and communications" | Now specifies registered principal review with evidence requirements (reviewer, date, actions) per Rule 3110(b)(4)-(5) |

**SEC (9 rules): All 9 fixed.** Every rule was missing `regulation_paragraph`. Critical issue found and fixed:

| Rule | Issue | Resolution |
|------|-------|-----------|
| **All MKT rules** | **`cfr_reference` cited 17 CFR 275.206(4)-7 (Compliance Procedures) instead of 17 CFR 275.206(4)-1 (Marketing Rule)** | Fixed to correct CFR. Also fixed references in PRODUCT-BRIEF.md, cli/redline/ai.py, and vale-packages/FinCompliance/SECProhibitedClaims.yml. Renamed file from marketing-rule-206-4-7.yml to marketing-rule-206-4-1.yml |
| ADV-01 | Generic "must not contain prohibited claims" | Rewritten to cite 15 USC 80b-3(c)(1)(A) and criminal penalty provisions (18 USC 1001, 15 USC 80b-17) |
| ADV-02 | Cited only "17 CFR 275.204-1" (amendment filing rule) | cfr_reference now cites 17 CFR 279.1 (Form ADV), 275.204-1 (amendments), and 15 USC 80b-3/80b-4 (statutory authority). Description specifies 18-item Part 2A brochure format |
| MKT-01 | Generic "prohibited misleading claims" | Rewritten to cite Rule 206(4)-1(a)(1)-(3) general prohibitions specifically |
| MKT-03 | Said "must include required disclosures" -- vague | Now specifies client status, compensation, conflicts disclosures, written agreement requirement, and disqualification provisions per Rule 206(4)-1(b) |
| MKT-04 | Said "must include prominent disclaimers" -- not what the rule says | Rewritten: hypothetical performance requires adopted policies/procedures for audience relevance, not just disclaimers |
| MKT-05 | Said "fee disclosures must be clear and complete" -- vague | Now cites Rule 206(4)-1(a)(6) fair and balanced performance presentation and (a)(7) catch-all prohibition |
| MKT-06 | Said "net of fees with appropriate time periods" -- imprecise | Now specifies retail-targeting requirement, equal prominence for net alongside gross, and 1/5/10-year time period requirements per Rule 206(4)-1(d)(2)-(3) |
| MKT-07 | Said "material risks must be disclosed alongside performance claims" -- generic | Rewritten to cite Rule 206(4)-1(a)(4) (risks alongside benefits) and (a)(5) (specific investment advice fairness) |

### Full Audit: SOC 2 (10) and ISO 27001 (10) (2026-04-08)

All 10 SOC 2 rules audited against AICPA Trust Services Criteria (TSC) 2017. All 10 ISO 27001 rules audited against ISO/IEC 27001:2022.

**SOC 2 (10 rules): 4 fixed, 6 verified.**

| Rule | Issue | Resolution |
|------|-------|-----------|
| SOC2-02 | Injected "specific hours or minutes" — CC7.4 requires a defined response program, not specific time units | Rewritten to match CC7.4 language: understand, contain, remediate, communicate |
| SOC2-03 | Demanded "explicit frequencies" — neither CC4.1 nor CC7.2 prescribes specific frequency requirements | Rewritten: ongoing/separate evaluations (CC4.1) and anomaly detection (CC7.2) |
| SOC2-04 | Required "documented scoring criteria" — CC3.2 requires risk analysis, not numeric scoring | Changed "scoring criteria" to "analysis criteria" |
| SOC2-07 | Injected "explicit schedules, retention periods, and recovery testing frequencies" — A1.2 does not use these terms | Rewritten: defined, documented, tested recovery procedures |

**ISO 27001 (10 rules): 8 fixed, 2 verified.** Seven rules used ISO 27001:2013 Annex A numbering while the file header claimed 2022 version.

| Rule | Issue | Resolution |
|------|-------|-----------|
| ISO27001-01 | Injected "implementation timelines" — Clause 6.1.3 does not mandate timelines | Removed; now says "risk owners and approval of the risk treatment plan" |
| ISO27001-02 | **Cited A.8 (2013: Asset Management)** — in 2022, A.8 is "Technological controls" | Updated to A.5.9, A.5.10, A.5.11 (Inventory, Acceptable Use, Return of Assets) |
| ISO27001-03 | **Cited A.9.1 (2013: Access Control)** — does not exist in 2022 | Updated to A.5.15, A.5.16, A.5.18 (Access Control, Identity Management, Access Rights) |
| ISO27001-04 | **Cited A.10 (2013: Cryptography)** — does not exist in 2022 | Updated to A.8.24 (Use of Cryptography); simplified description |
| ISO27001-05 | **Cited A.15 (2013: Supplier Relationships)** — does not exist in 2022 | Updated to A.5.19-A.5.22 (Supplier security lifecycle) |
| ISO27001-06 | **Cited A.16 (2013: Incident Management)** — does not exist in 2022 | Updated to A.5.24-A.5.28, A.6.8 (Incident management + event reporting) |
| ISO27001-07 | **Cited A.17 (2013: Business Continuity)** — does not exist in 2022 | Updated to A.5.29, A.5.30 (Disruption + ICT readiness) |
| ISO27001-08 | **Cited A.18 (2013: Compliance)** — does not exist in 2022 | Updated to A.5.31, A.5.35, A.5.36 (Legal requirements, independent review, policy compliance) |
| ISO27001-09 | Cited A.7.2.2 (2013 numbering) + Clause 7.3 | Updated A.7.2.2 to A.6.3; Clause 7.3 confirmed correct |

## Project Structure

```
redline/
├── regulations/           # 17 YAML rule files (95 rules total)
│   ├── gdpr/gdpr.yml      # 10 rules
│   ├── hipaa/hipaa.yml     # 10 rules
│   ├── sox/                # 11 rules (section-302, section-404, pcaob-standards)
│   ├── finra/              # 10 rules (rule-2111, rule-2210, rule-3110)
│   ├── bsa-aml/            # 15 rules (aml-program, cdd, ctr, sar)
│   ├── sec/                # 9 rules (marketing-rule, adv-filing)
│   ├── soc2/soc2.yml       # 10 rules
│   ├── iso27001/           # 10 rules
│   ├── quebec-law25/       # 10 rules
│   └── pipeda/pipeda.yml   # 10 rules
├── vale-packages/          # 88 Vale linting rules (FinCompliance)
├── cli/                    # Python CLI
├── templates/              # Report templates
├── tests/                  # Test documents
└── docs/                   # Landing page
```

## Rule Types

- **deterministic** — Vale pattern matching. Catches structural issues, prohibited terms, missing sections. No LLM needed. All 95 rules are deterministic as of 2026-04-08.

## Development

```bash
# Run linter against a document
python -m redline lint document.md --regulations gdpr,hipaa

# Run tests
python -m pytest tests/
```

## Product Roadmap

### Immediate
- ~~**Fix 7 audit findings** from spot-check~~ (done 2026-04-07)
- ~~**Audit GDPR (10) and HIPAA (10)**~~ (done 2026-04-08)
- ~~**Audit SOX (11) and BSA-AML (15)**~~ (done 2026-04-08)
- ~~**Audit SOC 2 (10) and ISO 27001 (10)**~~ (done 2026-04-08)
- ~~**Audit FINRA (10) and SEC (9)**~~ (done 2026-04-08)
- **All 95 rules audited.** Every rule now has `regulation_paragraph` with primary source citation.
- ~~**Add `legal_text` field** to rule YAML schema (matching AI Trace Auditor pattern)~~ (done 2026-04-08)
- ~~**Convert all 18 `check_type: ai` rules to deterministic Vale patterns**~~ (done 2026-04-08)
- **Add `verified_against_primary` flag** to each rule

### Near-term
- **PDF/Word input** — convert to markdown, then lint. Most compliance docs are Word/PDF.
- **Gap report generation** — "Your BSA/AML policy is missing: SAR filing timelines, CIP verification procedures, beneficial ownership thresholds"
- **Redline + AI Trace Auditor bundle** — lint documents AND traces for full compliance picture

### Medium-term
- **Regulatory change tracking** — monitor Federal Register, flag affected documents
- **Cross-document consistency** — detect contradictions between policies
- **Hosted SaaS** — upload docs, get instant compliance report

## Connection to Other Projects

- **AI Trace Auditor**: Shares YAML requirement pattern. Redline lints documents, Trace Auditor lints traces. Same buyer.
- **Comply**: Overlapping Vale rules for financial regulations. Comply targets credit unions specifically. Redline is broader (fintech, enterprise).
