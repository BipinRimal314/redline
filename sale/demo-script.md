# Redline — 2-Minute Demo

Run this yourself after `pip install redline-compliance` and [Vale](https://vale.sh/docs/install/).

## Setup (10 seconds)

```bash
pip install redline-compliance
git clone https://github.com/BipinRimal314/redline.git
cd redline
```

## Demo 1: Lint a document (30 seconds)

```bash
# Lint a compliance doc against all loaded rules
redline lint fixtures/failing/aml-policy-bad.md

# You'll see:
# - Table of findings with level, line, rule, message, regulation ID
# - Errors (prohibited language, vague terms)
# - Warnings (missing elements, weak assertions)
# - Exit code 1 if errors found — CI-friendly
```

## Demo 2: Passing vs failing (20 seconds)

```bash
# Good doc passes clean
redline lint fixtures/passing/aml-policy-good.md

# Bad doc catches real problems
redline lint fixtures/failing/aml-policy-bad.md

# Same rules, deterministic results, every time
```

## Demo 3: Browse regulations (20 seconds)

```bash
# See all available regulations
redline regulations list

# Drill into SOC2
redline regulations info SOC2-TSC

# See each requirement mapped to its Vale rule + regulation paragraph
```

## Demo 4: Generate rules from new regulation (30 seconds)

```bash
# Preview rules the pipeline would generate (no files written)
export ANTHROPIC_API_KEY=sk-...
redline generate regulations-source/soc2-trust-services-criteria.md \
  --id SOC2-DEMO --authority AICPA --dry-run

# You'll see:
# - Table of generated rules with filenames, requirement IDs, paragraphs
# - Token counts per rule
# - No files written (dry run)
```

## Demo 5: Gap report (20 seconds)

```bash
# Generate a structured gap report
redline report fixtures/failing/aml-policy-bad.md --format json

# Output: JSON with findings grouped by regulation, severity, and requirement
```

## Key Points to Highlight for Buyers

1. **Deterministic** — same input, same output, every run. No LLM randomness.
2. **DLP-safe** — runs locally, no documents leave the machine
3. **Audit trail** — every flag traces: rule -> requirement -> regulation paragraph
4. **65 rules, 8 domains** — SOC2, GDPR, HIPAA, ISO 27001, BSA/AML, SEC, FINRA, SOX
5. **Rule generation pipeline** — `redline generate` turns any regulation into rules
6. **CI exit codes** — 0/1 pass/fail, drops into any pipeline
7. **Zero runtime LLM cost** — rules are regex/keywords, milliseconds per document
