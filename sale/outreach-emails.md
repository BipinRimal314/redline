# Redline Outreach Email Templates

---

## Template 1: GRC Platforms (Hyperproof, Vanta, Drata, Sprinto, Secureframe)

**Subject:** Deterministic compliance doc linting — acquisition opportunity

**Body:**

Hi [NAME],

Your customers write compliance documents: SOC2 policies, GDPR privacy notices, HIPAA security plans. [COMPANY] manages the compliance program. But who checks that the documents themselves actually meet the regulation?

I built Redline, a compliance doc linter with 65 deterministic rules across 8 regulatory domains (SOC2, GDPR, HIPAA, ISO 27001, BSA/AML, SEC, FINRA, SOX). Every flag traces to a specific regulation paragraph. Zero LLM cost at runtime. Runs locally, so no DLP risk from uploading sensitive documents.

The differentiator: an LLM reads the regulation once and generates deterministic rules (regex, keyword patterns, structural checks). Those rules run in milliseconds on every document. When a regulation updates, regenerate the rule set. The rule sets are the product.

I'm selling the project outright: OSS CLI (49 tests, MIT), cloud version (FastAPI + Next.js + Docker), rule generation pipeline, and all 65 Vale rules with regulation mappings.

For [COMPANY], this means automated document quality checking alongside your existing compliance automation. For your customers, it means one more thing they don't have to do manually.

15 minutes to discuss?

GitHub: github.com/BipinRimal314/redline
Product brief attached.

Bipin Rimal

---

## Template 2: RegTech / Fintech Compliance (Hummingbird, Flagright, Sumsub, CUBE)

**Subject:** Compliance doc linter for [BSA/AML | regulated] documents — for sale

**Body:**

Hi [NAME],

Quick question: when your customers submit AML policies or SAR narratives, how do they know the documents meet regulatory standards before submission?

I built Redline, a compliance doc linter that catches non-compliant language deterministically. For BSA/AML specifically: it flags vague language ("adequate controls"), missing required elements (five pillars, risk methodology), and prohibited phrases. Every flag traces to a FinCEN CFR reference.

The tool runs locally (DLP-safe for sensitive financial docs), costs nothing at runtime (no per-document LLM calls), and produces an audit trail showing exactly which rule caught which issue at which paragraph.

It also covers SOC2, GDPR, HIPAA, ISO 27001, SEC, FINRA, and SOX. New regulations can be added through the rule generation pipeline: LLM reads the regulation once, outputs deterministic rules, rules run forever.

I'm selling the entire project: CLI + cloud version + 65 rules + rule generator + 30 days integration support.

For [COMPANY], this could be a new feature: "check your compliance docs before submission." For your regulated customers, it's peace of mind.

Worth a quick call?

GitHub: github.com/BipinRimal314/redline

Bipin Rimal

---

## Template 3: Bundle Pitch (for companies on both buyer lists)

**Subject:** Two compliance tools, one acquisition — AI system auditing + doc linting

**Body:**

Hi [NAME],

I'm reaching out about two complementary compliance tools I built and am selling together:

**AI Trace Auditor** — audits AI system traces against EU AI Act (Articles 11, 12, 13, 25), NIST AI RMF, and GDPR. 301 tests, published on PyPI, Apache 2.0. The only open-source tool that does multi-agent compliance auditing.

**Redline** — lints compliance documents against SOC2, GDPR, HIPAA, ISO 27001, BSA/AML, SEC, FINRA, SOX. 65 deterministic rules, each traceable to a regulation paragraph. Zero runtime LLM cost. 49 tests, MIT.

Together: complete compliance automation for both AI systems and their documentation. One covers the code, the other covers the docs.

Bundle: $40K-$60K for both. Includes source code, all rules/requirements, cloud version, and 30 days integration support.

[COMPANY] already does [WHAT THEY DO]. These tools extend that into AI system compliance and document quality — two gaps your customers will hit as EU AI Act enforcement begins August 2026.

15 minutes?

Bipin Rimal

---

## Personalization Notes

### CUBE
- Mention: "You just acquired 4CRisk for regulatory mapping. Redline is the next layer: mapping is knowing what the regulation says, linting is verifying that docs actually comply."
- Mention: RegTech100 recognition for both companies

### Hyperproof (Craig Unger)
- Mention: AI Guided Experiences launch at RSA 2026
- Mention: FedRAMP authorization — Redline's rules could be adapted for federal compliance docs

### Hummingbird (Joe Robinson / Matthew Van Buskirk)
- Mention: Their Treasury/OCC background — they understand regulatory document quality
- Mention: Specific BSA/AML rules: SAR narrative checks, five pillars, prohibited language

### Flagright (Baran Ozkan)
- Mention: RegTech100 for third consecutive year
- Mention: Smaller team = faster integration. "You ship this as a feature in weeks, not months."
