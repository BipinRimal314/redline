"""Rule generation pipeline: LLM reads a regulation once, outputs deterministic Vale rules."""

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class GeneratedRule:
    """A Vale rule generated from regulation text."""

    filename: str
    vale_config: dict[str, Any]
    regulation_paragraph: str
    requirement_id: str
    requirement_description: str
    severity: str


@dataclass(frozen=True)
class GeneratedRuleSet:
    """Complete output of the rule generation pipeline."""

    regulation_id: str
    regulation_name: str
    authority: str
    cfr_reference: str
    document_types: list[str]
    rules: list[GeneratedRule]
    generated_at: str
    model_used: str
    source_file: str


GENERATION_SYSTEM_PROMPT = """You are a compliance rule engineer. Your job is to read regulatory text and generate deterministic text-matching rules in Vale format.

Vale is a prose linter. Rules use YAML and support these extension types:
- `existence`: flags when specific tokens/patterns ARE found (bad patterns)
- `substitution`: flags a word and suggests a replacement
- `occurrence`: flags when something appears too many/few times
- `conditional`: flags when a term is used without a corresponding definition

For compliance doc linting, `existence` is most common — it catches prohibited language, vague terms, and missing specificity.

Here is an example Vale rule (existence type):
```yaml
extends: existence
message: "Vague control description: '%s'. SOX Section 404 requires specific, testable control descriptions."
link: "https://pcaobus.org/oversight/standards/auditing-standards/details/AS2201"
level: error
ignorecase: true
tokens:
  - adequate controls
  - appropriate controls
  - reasonable controls
```

And here is an example regulation YAML that maps rules to requirements:
```yaml
regulation:
  id: "BSA-AML-PROG"
  name: "Anti-Money Laundering Program Requirements"
  authority: "FinCEN"
  cfr_reference: "31 CFR 1020.210"
  document_types:
    - compliance-policy
  requirements:
    - id: "AML-01"
      description: "Program must include all five BSA/AML pillars"
      severity: error
      check_type: deterministic
      vale_rule: "FinCompliance.RequiredProgramElements"
```

IMPORTANT RULES:
1. Each Vale rule filename must be PascalCase, no spaces, no hyphens
2. Vale rule filenames must start with the domain prefix (e.g., SOC2, GDPR, HIPAA)
3. Tokens should be specific phrases that indicate non-compliance, NOT general words
4. Each rule must trace back to a specific regulation section/paragraph
5. Generate rules that catch REAL compliance problems, not trivial style issues
6. Prefer false negatives over false positives — only flag things that are genuinely problematic
7. The `message` field must explain WHY this is a problem and cite the regulation section
8. Set severity: error for mandatory requirements, warning for recommended practices

Respond with a JSON object containing:
{
  "regulation": {
    "id": "string",
    "name": "string",
    "authority": "string",
    "cfr_reference": "string",
    "document_types": ["string"]
  },
  "rules": [
    {
      "filename": "PascalCase.yml",
      "vale_config": {
        "extends": "existence",
        "message": "string with %s placeholder",
        "link": "url to regulation",
        "level": "error|warning|suggestion",
        "ignorecase": true,
        "tokens": ["phrase1", "phrase2"]
      },
      "regulation_paragraph": "exact section reference (e.g., CC6.1, Article 5(1)(a))",
      "requirement_id": "short ID (e.g., SOC2-CC6-01)",
      "requirement_description": "what the regulation requires",
      "severity": "error|warning"
    }
  ]
}"""

GENERATION_USER_TEMPLATE = """Read the following regulation text and generate Vale compliance rules.

Regulation ID: {regulation_id}
Authority: {authority}
Document types these rules should apply to: {document_types}

---
REGULATION TEXT:
{regulation_text}
---

Generate Vale rules that catch non-compliance in documents subject to this regulation. Focus on:
1. Prohibited language or vague terms that regulators flag
2. Missing required elements (e.g., required disclosures, mandatory sections)
3. Incorrect formatting or citation patterns
4. Terms that indicate weak or non-specific compliance language

Generate between 5-15 rules depending on the regulation's complexity. Quality over quantity."""


class RuleGenerator:
    """Generates Vale rules from regulation text using an LLM."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-20250514",
    ) -> None:
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY required for rule generation. "
                "Set the environment variable or pass api_key parameter."
            )
        self.model = model

        try:
            import anthropic

            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "anthropic package required for rule generation. "
                "Install with: pip install redline-compliance[ai]"
            )

    def generate(
        self,
        regulation_text: str,
        regulation_id: str,
        authority: str = "",
        document_types: list[str] | None = None,
        source_file: str = "",
    ) -> GeneratedRuleSet:
        """Read regulation text and generate a complete rule set."""
        doc_types = document_types or ["compliance-policy"]

        user_message = GENERATION_USER_TEMPLATE.format(
            regulation_id=regulation_id,
            authority=authority,
            document_types=", ".join(doc_types),
            regulation_text=regulation_text[:50000],
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            system=GENERATION_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        return self._parse_response(
            response.content[0].text,
            regulation_id=regulation_id,
            source_file=source_file,
        )

    def _parse_response(
        self,
        response_text: str,
        regulation_id: str,
        source_file: str,
    ) -> GeneratedRuleSet:
        """Parse LLM response into a structured rule set."""
        json_match = re.search(
            r"\{[\s\S]*\"regulation\"[\s\S]*\"rules\"[\s\S]*\}",
            response_text,
        )
        if not json_match:
            raise ValueError("LLM response did not contain valid JSON rule set")

        data = json.loads(json_match.group())
        reg = data["regulation"]
        rules = [
            GeneratedRule(
                filename=r["filename"],
                vale_config=r["vale_config"],
                regulation_paragraph=r["regulation_paragraph"],
                requirement_id=r["requirement_id"],
                requirement_description=r["requirement_description"],
                severity=r.get("severity", "warning"),
            )
            for r in data["rules"]
        ]

        return GeneratedRuleSet(
            regulation_id=reg["id"],
            regulation_name=reg["name"],
            authority=reg["authority"],
            cfr_reference=reg.get("cfr_reference", ""),
            document_types=reg.get("document_types", ["compliance-policy"]),
            rules=rules,
            generated_at=datetime.now(timezone.utc).isoformat(),
            model_used=self.model,
            source_file=source_file,
        )


def write_rule_set(
    rule_set: GeneratedRuleSet,
    vale_dir: Path,
    regulations_dir: Path,
) -> dict[str, list[Path]]:
    """Write generated rules to the filesystem.

    Returns dict with keys 'vale_rules', 'regulation_yaml', 'audit_trail'.
    """
    created: dict[str, list[Path]] = {
        "vale_rules": [],
        "regulation_yaml": [],
        "audit_trail": [],
    }

    # 1. Write Vale rule files
    vale_dir.mkdir(parents=True, exist_ok=True)
    for rule in rule_set.rules:
        rule_path = vale_dir / rule.filename
        rule_path.write_text(
            yaml.dump(rule.vale_config, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        created["vale_rules"].append(rule_path)

    # 2. Write regulation YAML
    reg_domain = rule_set.regulation_id.lower().replace("-", "_").replace(" ", "_")
    reg_dir = regulations_dir / reg_domain
    reg_dir.mkdir(parents=True, exist_ok=True)

    regulation_data = {
        "regulation": {
            "id": rule_set.regulation_id,
            "name": rule_set.regulation_name,
            "authority": rule_set.authority,
            "cfr_reference": rule_set.cfr_reference,
            "document_types": rule_set.document_types,
            "requirements": [
                {
                    "id": rule.requirement_id,
                    "description": rule.requirement_description,
                    "severity": rule.severity,
                    "check_type": "deterministic",
                    "vale_rule": f"FinCompliance.{rule.filename.replace('.yml', '')}",
                    "regulation_paragraph": rule.regulation_paragraph,
                }
                for rule in rule_set.rules
            ],
        }
    }

    reg_path = reg_dir / f"{reg_domain}.yml"
    reg_path.write_text(
        yaml.dump(regulation_data, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )
    created["regulation_yaml"].append(reg_path)

    # 3. Write audit trail
    audit_trail = {
        "generated_at": rule_set.generated_at,
        "model_used": rule_set.model_used,
        "source_file": rule_set.source_file,
        "regulation_id": rule_set.regulation_id,
        "rule_count": len(rule_set.rules),
        "mappings": [
            {
                "vale_rule": f"FinCompliance.{rule.filename.replace('.yml', '')}",
                "requirement_id": rule.requirement_id,
                "regulation_paragraph": rule.regulation_paragraph,
                "description": rule.requirement_description,
                "severity": rule.severity,
                "token_count": len(rule.vale_config.get("tokens", [])),
            }
            for rule in rule_set.rules
        ],
    }

    audit_path = reg_dir / f"{reg_domain}_audit_trail.json"
    audit_path.write_text(
        json.dumps(audit_trail, indent=2),
        encoding="utf-8",
    )
    created["audit_trail"].append(audit_path)

    return created
