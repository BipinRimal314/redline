# Redline

Compliance documentation linter for financial regulations. Deterministic rules catch what patterns can match. AI catches the rest.

## Install

```bash
pip install redline-compliance
```

Requires [Vale](https://vale.sh/docs/install/) installed separately.

## Usage

```bash
# Lint a document against BSA/AML rules
redline lint policies/aml-policy.md

# Generate a gap report
redline report policies/aml-policy.md --format json

# Initialize config in your project
redline init
```

## Supported Regulations

- BSA/AML (Bank Secrecy Act / Anti-Money Laundering)
- SEC (Securities and Exchange Commission) -- coming soon
- FINRA (Financial Industry Regulatory Authority) -- coming soon
- SOX (Sarbanes-Oxley Act) -- coming soon

## License

MIT
