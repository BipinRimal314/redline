# Redline — Product Brief

## For Sale: Deterministic Compliance Document Linter With Regulation-Traceable Rules

**Asking price:** $15,000-$25,000 (full IP transfer: OSS CLI + cloud version + all rule sets)
**Bundle with AI Trace Auditor:** $40,000-$60,000

---

## The Opportunity

Compliance teams review policy documents manually at $200-$500/hour. LLM-based review (ChatGPT, Claude) is non-deterministic, violates DLP policies when documents contain sensitive information, and produces no audit trail.

The $19B+ RegTech market needs a compliance doc linter that:
1. Runs locally (DLP-safe)
2. Produces deterministic results (same input = same output, every time)
3. Traces every flag to a specific regulation paragraph (auditor-verifiable)
4. Costs zero at runtime (no per-document LLM calls)

Redline does all four.

## How It Works

LLM reads a regulation once. Generates deterministic rules (regex, keywords, structural checks). Those rules run in milliseconds on every document thereafter. The audit trail shows: which rule flagged which clause, traceable to which regulation paragraph.

```
[Regulation text] -> LLM (one-time) -> Vale rules -> Deterministic linting forever
```

## What You're Buying

### OSS CLI (Projects/redline/)

| Asset | Details |
|---|---|
| Python CLI | `redline lint`, `lint --ai`, `report`, `generate`, `regulations`, `init` |
| Vale rules | 45 rules across 6 regulatory domains |
| Regulation YAMLs | BSA/AML, SEC, FINRA, SOX, SOC2, GDPR |
| Rule generation pipeline | `redline generate` — LLM reads regulation, outputs Vale rules + mappings |
| AI semantic layer | BYOK Claude, 7 structured prompts, confidence gating, hallucination rejection |
| Tests | 49 passing |
| License | MIT |

### Cloud Version (Projects/redline-cloud/)

| Asset | Details |
|---|---|
| FastAPI backend | Upload -> convert -> lint -> AI -> report pipeline |
| Next.js 14 frontend | Landing page, scan page, gap report viewer, regulations browser |
| Document conversion | PDF/DOCX -> Markdown via MarkItDown |
| Docker Compose | API + Web + PostgreSQL + Redis |
| Billing skeleton | Usage metering + webhook handler (needs Stripe setup) |

### The Moat: Rule Generation Pipeline

This is the key differentiator. `redline generate <regulation-text> --id HIPAA` reads any regulation and outputs:
- Vale rule files (deterministic, run in milliseconds)
- Regulation YAML (maps rules to requirements with paragraph references)
- Audit trail JSON (which model generated which rule, when, from what source)

When a regulation updates, regenerate the rule set. Version and distribute to customers. This is the subscription value for a buyer who wants recurring revenue.

## Regulatory Coverage

| Domain | Rules | Regulation | Authority |
|---|---|---|---|
| BSA/AML | 6 | Bank Secrecy Act | FinCEN |
| SEC | 6 | Marketing Rule 206(4)-1 | SEC |
| FINRA | 5 | Communications with Public | FINRA |
| SOX | 5 | Section 404 | PCAOB |
| SOC2 | 10 | Trust Services Criteria | AICPA |
| GDPR | 10 | Regulation (EU) 2016/679 | EU |

Plus common quality rules (plain language, passive voice, sentence length, date formats).

## Why This Can't Be Easily Replicated

1. **Rule engineering is domain expertise.** Each rule must match non-compliant patterns without false positives. The tokens are curated multi-word phrases, not keywords.

2. **The audit trail format is novel.** Every finding chains: document location -> Vale rule -> requirement ID -> regulation paragraph -> authority. No other tool does this for compliance documents.

3. **The generation pipeline is the real IP.** A carefully engineered prompt teaches the LLM Vale syntax, compliance rule patterns, and the regulation YAML mapping format. Getting this prompt right took iteration.

4. **AI + deterministic hybrid.** Some requirements can't be checked with patterns ("is this risk assessment adequate?"). The AI layer handles those with BYOK Claude, confidence gating, and hallucination rejection. The hybrid approach is architecturally sound and hard to reproduce.

## Integration Paths for Buyers

- **RegTech platforms** (Hummingbird, Flagright): Add doc linting alongside transaction monitoring
- **GRC platforms** (Vanta, Drata, Sprinto): Lint compliance docs as part of continuous compliance
- **Document management platforms**: Add compliance checks to doc workflows
- **Compliance consulting firms**: White-label the tool for client engagements

## What's Included in the Sale

- Full source code for both repos (OSS CLI + cloud version)
- All 45 Vale rule files
- Rule generation pipeline (generator.py + prompts)
- 6 regulation YAML definitions with audit trails
- Docker Compose for cloud deployment
- 30 days of post-sale technical support
- MIT license (buyer can do anything)

## Contact

Bipin Rimal — bipinrimal314@gmail.com
GitHub: github.com/BipinRimal314/redline
