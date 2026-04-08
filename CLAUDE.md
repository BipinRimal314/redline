# Redline — Compliance Documentation Linter

Deterministic compliance documentation linter. 85 rules across 16 regulations. Every flag traces to a specific rule, which traces to a specific regulation paragraph. Zero LLM cost at runtime.

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

**31 rules remain unaudited.** Priority: FINRA (10 rules), SEC (9 rules), SOC 2 (10 rules), ISO 27001 (10 rules). [NEEDS VERIFICATION: actual count is 39 if ISO 27001 has 10.]

## Project Structure

```
redline/
├── regulations/           # 16 YAML rule files (85 rules total)
│   ├── gdpr/gdpr.yml      # 10 rules
│   ├── hipaa/hipaa.yml     # 10 rules
│   ├── sox/                # 11 rules (section-302, section-404, pcaob-standards)
│   ├── finra/              # 10 rules (rule-2111, rule-2210, rule-3110)
│   ├── bsa-aml/            # 15 rules (aml-program, cdd, ctr, sar)
│   ├── sec/                # 9 rules (marketing-rule, adv-filing)
│   ├── soc2/soc2.yml       # 10 rules
│   └── iso27001/           # 10 rules
├── vale-packages/          # 68 Vale linting rules (FinCompliance)
├── cli/                    # Python CLI
├── templates/              # Report templates
├── tests/                  # Test documents
└── docs/                   # Landing page
```

## Rule Types

- **deterministic** — Vale pattern matching. Catches structural issues, prohibited terms, missing sections. No LLM needed.
- **ai** — Claude API for substantive adequacy checks (e.g., "is this net-of-fees disclosure adequate?"). Flagged for human review.

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
- **Audit remaining rules** — FINRA (10), SEC (9), SOC 2 (10), ISO 27001 (10)
- **Add `legal_text` field** to rule YAML schema (matching AI Trace Auditor pattern)
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
