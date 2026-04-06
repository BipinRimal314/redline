# Redline — Product Map

**Goal:** Sell the product outright for $15K-$25K (or $40K-$60K bundled with AI Trace Auditor).
**Core thesis:** LLM reads a regulation once, generates deterministic rule sets. Rules run in milliseconds on every document thereafter. Zero LLM cost at runtime.
**Buyer profile:** RegTech platforms (Hummingbird, Flagright, Sumsub), compliance-as-code (Vanta, Laika, Secureframe), document management for regulated industries.

---

## What's Built

| Component | Status | Details |
|---|---|---|
| Vale rule engine | Done | 25 rules across 4 fintech domains |
| Regulatory domains | Done | BSA/AML, SEC, FINRA, SOX |
| Regulation YAML files | Done | 12 files with CFR references + requirement mappings |
| AI semantic analysis | Done | BYOK Claude integration, 7 structured prompts, confidence gating, hallucination rejection |
| Python CLI | Done | `redline lint`, `lint --ai`, `report`, `regulations`, `init` |
| Test fixtures | Done | 10 fixtures (passing + failing per domain) |
| Tests | Done | 44 passing |
| GitHub repo | Done | Public, BipinRimal314/redline |
| License | Done | MIT |

### Cloud Version (Projects/redline-cloud/)

| Component | Status | Details |
|---|---|---|
| FastAPI backend | Skeleton | Scan endpoint, reports, regulations, billing webhook |
| Next.js 14 frontend | Skeleton | Landing page, scan page, gap report viewer, regulations browser |
| Document conversion | Done | PDF/DOCX -> Markdown via MarkItDown |
| Docker Compose | Done | API + Web + PostgreSQL + Redis |
| Auth | Not started | Needs NextAuth.js |
| Billing | Skeleton | Webhook handler, no Stripe setup |
| Persistence | Not started | In-memory stores only |

## The Expansion: Deterministic Compliance Linter

### What Changes

Current Redline: 25 hand-written Vale rules for fintech only.
Expanded Redline: LLM-generated rule sets for ANY regulation, running deterministically at runtime.

### Why This Wins

1. **DLP-safe:** Runs locally. No uploading 200 internal policy docs to ChatGPT.
2. **Audit trail:** Every flag traces to a specific rule, which traces to a specific regulation paragraph. LLM outputs can't do this.
3. **Zero runtime LLM cost:** Rules are regex/keyword/structural. Milliseconds per document.
4. **Versioned rule sets as the moat:** When SOC2 updates, the rule set updates. This is the subscription value.

### New Regulatory Domains to Add

- [x] **SOC2** — 10 rules covering CC1-CC9 + availability + confidentiality + privacy (2026-04-06)
- [x] **GDPR** — 10 rules covering Articles 5-49 (2026-04-06)
- [ ] **HIPAA** — documentation requirements (policies, BAAs, risk assessments)
- [ ] **ISO 27001** — ISMS documentation (Statement of Applicability, risk treatment plans)

### Rule Generation Pipeline (NEW — must build)

```
[Regulation text (PDF/HTML)]
    -> LLM reads regulation once
    -> Generates Vale rule set (regex, keywords, structural checks)
    -> Human review + version tag
    -> Rule set published to vale-packages/
    -> Runs deterministically on all documents thereafter
```

Each rule set includes:
- Rule files (.yml) with Vale syntax
- Regulation mapping (which rule -> which paragraph)
- Version + effective date
- Changelog

## What's Needed for Sale

### Tier 1: Must Have (blocks outreach)

- [x] **Rule generation pipeline** — generator.py built with full CLI command (2026-04-06)
  - [x] Prompt that reads a regulation and outputs Vale-compatible rules
  - [x] Mapping file format (rule -> regulation paragraph)
  - [x] Audit trail JSON output
  - [x] SOC2 + GDPR rule sets created (10 rules each, 2026-04-06)
- [x] **Audit trail output** — runner already maps findings to regulation_id + requirement_id. Audit trail JSONs created per rule set.
- [x] **README rewrite** — buyer-facing, leads with DLP-safe + deterministic + audit trail (2026-04-06)
- [x] **Product brief** — PRODUCT-BRIEF.md created (2026-04-06)
- [ ] **Acquire.com listing** — you handle (account + identity verification)

### Tier 2: Strengthens Pitch (parallel with outreach)

- [x] **HIPAA + ISO 27001 rule sets** — 10 rules each, total 65 rules across 8 domains (2026-04-06)
- [x] **Buyer list** — 9 companies across 3 categories (sale/buyer-list.md, 2026-04-06)
- [x] **Outreach emails** — 3 templates + bundle pitch (sale/outreach-emails.md, 2026-04-06)
- [ ] **Demo script** — 2-minute walkthrough: lint a doc, see flags with regulation traceability
- [ ] **Cloud version working demo** — Docker Compose boots, scan flow works end-to-end
- [ ] **PyPI publish** — `pip install redline-lint` or similar

### Tier 3: Nice to Have

- [x] **Landing page** — docs/index.html created (2026-04-06). Enable GitHub Pages in repo settings -> docs/ folder
- [ ] **Rule set versioning system** — git-tagged releases per regulation
- [ ] **Stripe billing** in cloud version
- [ ] **Demo video**

## Competitive Position

No compliance doc linter with deterministic rules + regulation traceability exists.
- ChatGPT/Claude can review docs but: no audit trail, DLP risk, non-deterministic, no versioning
- Manual compliance review: $200-$500/hour consultant time
- Generic doc linters (Vale, textlint): no compliance rule sets, no regulation mapping

**The moat is the curated, versioned rule sets per regulation.** The CLI is the delivery mechanism.

## Sale Assets

What the buyer gets:
1. GitHub repos (redline + redline-cloud, full history, tests, CI)
2. Rule generation pipeline (LLM -> deterministic rules)
3. Curated rule sets for 4-6 regulatory domains
4. Cloud version (FastAPI + Next.js + Docker Compose)
5. Vale integration (industry-standard prose linter)
6. MIT license — buyer can do anything

## Asking Price

$15K-$25K standalone. $40K-$60K bundled with AI Trace Auditor.

Justification:
- 2-3 months to replicate the CLI + rules
- Rule generation pipeline is the real IP — novel approach
- Regulation-to-rule mappings require domain expertise
- Cloud version skeleton saves 3-4 weeks of boilerplate
- $19B RegTech market, no equivalent tool
