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

| Regulation | Rules | Domain |
|---|---|---|
| BSA/AML | 6 rules | Financial crime |
| SEC Marketing Rule | 6 rules | Investment advisors |
| FINRA Communications | 5 rules | Broker-dealers |
| SOX Section 404 | 5 rules | Internal controls |
| SOC2 Trust Services | 10 rules | Security/compliance |
| GDPR | 10 rules | Data protection |

Plus common quality rules (plain language, sentence length, date formats, passive voice).

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
├── vale-packages/FinCompliance/  # 42+ Vale rules
├── regulations/                   # YAML requirement definitions
│   ├── bsa-aml/                  # BSA/AML, CDD, CTR, SAR
│   ├── sec/                      # SEC Marketing Rule
│   ├── finra/                    # FINRA Communications
│   ├── sox/                      # SOX Section 404
│   ├── soc2/                     # SOC2 Trust Services (NEW)
│   └── gdpr/                     # GDPR (NEW)
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
