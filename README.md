# Redline

**Compliance documentation linter with deterministic, regulation-traceable rules.** Every flag traces to a specific rule, which traces to a specific regulation paragraph. Zero LLM cost at runtime. Runs locally.

Upload 200 internal policy docs to ChatGPT? That violates your DLP policy. Run Redline locally instead.

## The Problem

Compliance teams review documents manually. $200-$500/hour. Inconsistent. Slow. LLM-based review is non-deterministic, produces no audit trail, and creates DLP risk when documents contain sensitive information.

Redline generates deterministic rules from regulations once (LLM reads the regulation, outputs regex/keyword/structural rules). Those rules run in milliseconds on every document thereafter. Each flag is traceable to a regulation paragraph. Auditors can verify the rule set. Compliance teams get consistency.

## How It Works

```
[Regulation text]
    -> redline generate (LLM reads regulation once)
    -> Deterministic Vale rules (regex, keywords, structural checks)
    -> Human review + version tag
    -> redline lint (runs in milliseconds, zero LLM cost)
    -> Findings traceable to regulation paragraphs
```

## Install

```bash
pip install redline-compliance
```

Requires [Vale](https://vale.sh/docs/install/) installed separately.

## Quick Start

```bash
# Lint a document against all loaded regulations
redline lint policies/aml-policy.md

# Lint with AI semantic analysis (BYOK, optional)
redline lint policies/aml-policy.md --ai

# Generate rules from a new regulation
redline generate regulation-text.md --id SOC2 --authority AICPA

# Generate a gap report
redline report policies/aml-policy.md --format json

# Browse available regulations
redline regulations list

# Initialize config
redline init
```

## Supported Regulations

105 rules across 10 frameworks, in 18 regulation files.

| Regulation | Rules | Domain | Audited against primary source |
|---|---|---|---|
| BSA/AML | 15 | Financial crime | Yes (2026-04-08) |
| SOX (302, 404, PCAOB) | 11 | Internal controls | Yes (2026-04-08) |
| GDPR | 10 | Data protection | Yes (2026-04-08) |
| HIPAA Security Rule | 10 | Protected health information | Yes (2026-04-08) |
| SOC 2 Trust Services | 10 | Security/compliance | Yes (2026-04-08) |
| ISO 27001 | 10 | Information security | Yes (2026-04-08) |
| FINRA | 10 | Broker-dealers | Yes (2026-04-08) |
| SEC (Marketing Rule, ADV) | 9 | Investment advisors | Yes (2026-04-08) |
| PIPEDA | 10 | Canadian privacy | **No** |
| Quebec Law 25 | 10 | Quebec privacy | **No** |

Plus common quality rules (plain language, sentence length, date formats, passive voice).

Redline does not cover PCI-DSS. That lives in the sibling project, [Comply](https://github.com/BipinRimal314/comply).

## Rule Verification Status

This section exists because a rule set that cites regulations is worthless if the citations are wrong, and there is no way to know without checking.

**The spot-check (2026-04-07).** I audited 10 of the then-85 rules against primary sources. Three were clean. Seven were not:

| Rule | Issue | Resolution |
|---|---|---|
| GDPR-02 | Cited Article 7, but the consent definition is Article 4(11) | Now cites both |
| GDPR-05 | Said "30-day timeline"; GDPR says "one month" | Fixed, with Article 12(3) |
| GDPR-08 | Presented the 72-hour deadline as absolute | Added "where feasible" per Article 33(1) |
| HIPAA-01 | Bundled Required and Addressable specs as equals | Now distinguishes them |
| HIPAA-07 | Injected "role-based access criteria" | Rewritten to §164.514(d)(2) language |
| HIPAA-09 | **Fabricated** — attributed NIST 800-88 concepts to HIPAA | Rewritten to §164.310(d)(2)(i-ii) |
| SOX 404-05 | Attributed PCAOB AS 2201 concepts to the statute | Now cites 15 USC 7262(a) and AS 2201 separately |

A 70% error rate on a sample of 10. One rule described a requirement that does not exist in the regulation it named.

That is the failure mode this architecture predicts. The LLM writes the rules; the LLM can be wrong; the difference from an LLM-in-the-loop reviewer is that the error sits in a YAML file where it can be found once and fixed permanently, rather than resurfacing unpredictably on every run.

**The full pass (2026-04-08).** All 85 rules existing at that point were then audited line by line against primary sources — GDPR, HIPAA, SOX, BSA/AML, SOC 2, ISO 27001, FINRA, SEC. Each now carries a `regulation_paragraph` citation and a `legal_text` quotation from the source. Six further corrections came out of it (HIPAA-05, 06, 10 had injected requirements the regulation does not state, such as recovery time objectives, which are not a HIPAA term).

**Not yet audited.** The 20 PIPEDA and Quebec Law 25 rules were added 2026-04-09, after that pass. They have not been checked against primary sources. Treat their citations as unverified.

## Rule Generation Pipeline

The differentiator: LLM generates rules, rules run deterministically.

```bash
# Point at any regulation text
redline generate hipaa-security-rule.md --id HIPAA --authority HHS

# Preview without writing files
redline generate hipaa-security-rule.md --id HIPAA --dry-run

# Output:
#   vale-packages/FinCompliance/HIPAAVagueAccessControls.yml
#   regulations/hipaa/hipaa.yml
#   regulations/hipaa/hipaa_audit_trail.json
```

Each generated rule set includes:
- **Vale rule files** — deterministic, run in milliseconds
- **Regulation YAML** — maps rules to requirements with paragraph references
- **Audit trail** — which model generated which rule, when, from what source

## Audit Trail

Every finding is traceable:

```
Finding: "adequate controls" flagged at line 47
  Rule: FinCompliance.SOC2VagueAccessControls
  Requirement: SOC2-CC6-01
  Regulation: SOC 2 Trust Services Criteria, CC6.1
  Authority: AICPA
  Severity: error
  Source: deterministic (confidence: 1.0)
```

An auditor can verify: the rule exists, it maps to CC6.1, and the token matched. No black box.

## Architecture

```
redline/
├── cli/redline/
│   ├── cli.py          # Typer CLI: lint, report, generate, regulations, init
│   ├── runner.py       # Vale subprocess orchestrator + finding mapper
│   ├── generator.py    # LLM-to-Vale rule generation pipeline
│   ├── ai.py           # BYOK Claude semantic analysis (optional)
│   ├── registry.py     # Regulation YAML loader + Vale rule index
│   ├── report.py       # Gap report generation (JSON, Markdown)
│   └── config.py       # .redline.yml config loader
├── vale-packages/FinCompliance/  # 103 Vale rules
├── regulations/                   # YAML requirement definitions, 105 rules
│   ├── bsa-aml/                  # BSA/AML program, CDD, CTR, SAR
│   ├── sec/                      # SEC Marketing Rule, ADV filing
│   ├── finra/                    # FINRA 2111, 2210, 3110
│   ├── sox/                      # SOX 302, 404, PCAOB standards
│   ├── soc2/                     # SOC 2 Trust Services
│   ├── gdpr/                     # GDPR
│   ├── hipaa/                    # HIPAA Security Rule
│   ├── iso27001/                 # ISO 27001 (2022 Annex A)
│   ├── pipeda/                   # PIPEDA (unaudited)
│   └── quebec-law25/             # Quebec Law 25 (unaudited)
├── regulations-source/           # Source regulation texts
├── fixtures/                     # Test documents (passing + failing)
└── tests/                        # 49 tests
```

## AI Semantic Analysis (Optional)

For requirements that can't be checked with patterns (e.g., "does this risk assessment methodology cover all required areas?"), Redline uses BYOK Claude with:
- 7 structured prompts per regulatory domain
- Confidence gating (default 0.7 threshold)
- Hallucination rejection (quoted text must appear in document)
- Findings marked as `source: ai` with confidence scores

```bash
export ANTHROPIC_API_KEY=sk-...
redline lint policies/aml-policy.md --ai
```

## License

MIT
