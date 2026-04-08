"""AI semantic analysis layer using Claude API (BYOK)."""

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from redline.runner import Finding


@dataclass(frozen=True)
class AIPrompt:
    """A structured prompt for AI compliance analysis."""

    key: str
    category: str
    system_prompt: str
    user_template: str


PROMPTS: dict[str, AIPrompt] = {
    "sar_activity_pattern_adequacy": AIPrompt(
        key="sar_activity_pattern_adequacy",
        category="adequacy",
        system_prompt="You are a BSA/AML compliance reviewer. Evaluate whether a SAR narrative adequately describes the suspicious activity pattern.",
        user_template="""Evaluate this SAR narrative section for adequacy of suspicious activity pattern description.

Document text:
{document_text}

Regulatory requirement: The narrative must clearly identify the suspicious activity pattern, including what made the activity suspicious, how it deviates from expected behavior, and any connections between transactions.

For each finding, respond in this JSON format:
{{
  "findings": [
    {{
      "text": "exact quote from document",
      "issue": "what is missing or inadequate",
      "regulation_id": "SAR-04",
      "severity": "error",
      "confidence": 0.0-1.0,
      "remediation": "specific suggestion"
    }}
  ]
}}

If the document adequately addresses the requirement, return {{"findings": []}}.""",
    ),
    "sar_detection_method": AIPrompt(
        key="sar_detection_method",
        category="adequacy",
        system_prompt="You are a BSA/AML compliance reviewer. Evaluate whether a SAR narrative describes how suspicious activity was detected.",
        user_template="""Evaluate this SAR narrative for description of detection method.

Document text:
{document_text}

Regulatory requirement: The narrative should describe how the suspicious activity was initially detected (e.g., transaction monitoring system, employee referral, law enforcement inquiry).

Respond in JSON format:
{{
  "findings": [
    {{
      "text": "exact quote from document",
      "issue": "what is missing or inadequate",
      "regulation_id": "SAR-05",
      "severity": "warning",
      "confidence": 0.0-1.0,
      "remediation": "specific suggestion"
    }}
  ]
}}

If adequately addressed, return {{"findings": []}}.""",
    ),
    "sar_five_ws_coverage": AIPrompt(
        key="sar_five_ws_coverage",
        category="adequacy",
        system_prompt="You are a BSA/AML compliance reviewer. Evaluate whether a SAR narrative covers the five W's.",
        user_template="""Evaluate this SAR narrative for coverage of the five W's (who, what, when, where, why).

Document text:
{document_text}

For each missing W, create a finding. Respond in JSON:
{{
  "findings": [
    {{
      "text": "relevant section or 'not found'",
      "issue": "which W is missing and why it matters",
      "regulation_id": "SAR-06",
      "severity": "warning",
      "confidence": 0.0-1.0,
      "remediation": "what to add"
    }}
  ]
}}

If all five W's are covered, return {{"findings": []}}.""",
    ),
    "aml_risk_assessment_adequacy": AIPrompt(
        key="aml_risk_assessment_adequacy",
        category="adequacy",
        system_prompt="You are a BSA/AML compliance reviewer. Evaluate AML program risk assessment methodology.",
        user_template="""Evaluate this AML program document for adequacy of risk assessment methodology.

Document text:
{document_text}

Regulatory requirement: The AML program must describe how the institution assesses BSA/AML risk, including customer risk ratings, product risk, geographic risk, and how risk levels are determined.

Respond in JSON:
{{
  "findings": [
    {{
      "text": "exact quote or 'not found'",
      "issue": "what is missing",
      "regulation_id": "AML-03",
      "severity": "warning",
      "confidence": 0.0-1.0,
      "remediation": "specific suggestion"
    }}
  ]
}}""",
    ),
    "sec_net_of_fees_adequacy": AIPrompt(
        key="sec_net_of_fees_adequacy",
        category="adequacy",
        system_prompt="You are an SEC compliance reviewer. Evaluate whether performance is properly presented net of fees.",
        user_template="""Evaluate this document for proper net-of-fees performance presentation.

Document text:
{document_text}

SEC Marketing Rule 206(4)-1 requires that performance be presented net of all advisory fees and expenses. Gross performance may only be shown alongside net performance with equal prominence.

Respond in JSON:
{{
  "findings": [
    {{
      "text": "exact quote",
      "issue": "what is missing or non-compliant",
      "regulation_id": "MKT-06",
      "severity": "error",
      "confidence": 0.0-1.0,
      "remediation": "specific suggestion"
    }}
  ]
}}""",
    ),
    "sec_risk_disclosure_adequacy": AIPrompt(
        key="sec_risk_disclosure_adequacy",
        category="adequacy",
        system_prompt="You are an SEC compliance reviewer. Evaluate risk disclosure adequacy.",
        user_template="""Evaluate this document for adequate risk disclosure alongside performance claims.

Document text:
{document_text}

SEC requires that material risks be disclosed prominently when performance is discussed. Risk disclosures must not be buried in footnotes or presented in a way that minimizes their importance.

Respond in JSON:
{{
  "findings": [
    {{
      "text": "exact quote",
      "issue": "what is missing or inadequate",
      "regulation_id": "MKT-07",
      "severity": "error",
      "confidence": 0.0-1.0,
      "remediation": "specific suggestion"
    }}
  ]
}}""",
    ),
    "sox_control_effectiveness_evaluation": AIPrompt(
        key="sox_control_effectiveness_evaluation",
        category="adequacy",
        system_prompt="You are a SOX compliance reviewer. Evaluate control documentation for completeness.",
        user_template="""Evaluate this control documentation for adequate evaluation of design and operating effectiveness.

Document text:
{document_text}

SOX Section 404 and PCAOB AS 2201 require that management assess both the design effectiveness (is the control designed to prevent/detect the risk?) and operating effectiveness (has the control operated as designed throughout the period?).

Respond in JSON:
{{
  "findings": [
    {{
      "text": "exact quote or 'not found'",
      "issue": "what is missing",
      "regulation_id": "404-05",
      "severity": "error",
      "confidence": 0.0-1.0,
      "remediation": "specific suggestion"
    }}
  ]
}}""",
    ),
}


def _validate_findings_standalone(
    raw_findings: list[dict[str, Any]],
    document_text: str,
    requirement: dict[str, Any],
    confidence_threshold: float,
) -> list[Finding]:
    """Validate AI findings: confidence gate + deterministic grounding. Standalone for testing."""
    validated: list[Finding] = []

    for raw in raw_findings:
        confidence = raw.get("confidence", 0.0)
        if confidence < confidence_threshold:
            continue

        quoted_text = raw.get("text", "")
        if quoted_text and quoted_text != "not found":
            if quoted_text.lower() not in document_text.lower():
                continue

        validated.append(
            Finding(
                rule=f"AI.{raw.get('regulation_id', 'unknown')}",
                message=raw.get("issue", ""),
                level=raw.get("severity", "warning"),
                line=0,
                text=quoted_text,
                source="ai",
                regulation_id=requirement.get("regulation_id"),
                regulation_name=None,
                authority=requirement.get("authority"),
                cfr_reference=None,
                requirement_id=raw.get("regulation_id"),
                confidence=confidence,
            )
        )

    return validated


class AIAnalyzer:
    """BYOK Claude integration for semantic compliance analysis."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-20250514",
        confidence_threshold: float = 0.7,
    ) -> None:
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable required for AI analysis. "
                "Set it or pass api_key parameter."
            )
        self.model = model
        self.confidence_threshold = confidence_threshold

        try:
            import anthropic

            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "anthropic package required for AI analysis. "
                "Install with: pip install redline-compliance[ai]"
            )

    def analyze(
        self,
        document_text: str,
        ai_requirements: list[dict[str, Any]],
    ) -> list[Finding]:
        """Run AI analysis on a document for the given requirements."""
        all_findings: list[Finding] = []

        for req in ai_requirements:
            prompt_key = req.get("ai_prompt_key", "")
            prompt = PROMPTS.get(prompt_key)
            if not prompt:
                continue

            raw_findings = self._call_api(prompt, document_text)
            validated = self._validate_findings(
                raw_findings, document_text, req
            )
            all_findings.extend(validated)

        return all_findings

    def _call_api(
        self, prompt: AIPrompt, document_text: str
    ) -> list[dict[str, Any]]:
        """Call Claude API with a structured prompt."""
        user_message = prompt.user_template.format(
            document_text=document_text
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            system=prompt.system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        return self._parse_response(response.content[0].text)

    def _parse_response(
        self, response_text: str
    ) -> list[dict[str, Any]]:
        """Parse JSON findings from Claude response."""
        json_match = re.search(
            r"\{[\s\S]*\"findings\"[\s\S]*\}", response_text
        )
        if not json_match:
            return []

        try:
            data = json.loads(json_match.group())
            return data.get("findings", [])
        except json.JSONDecodeError:
            return []

    def _validate_findings(
        self,
        raw_findings: list[dict[str, Any]],
        document_text: str,
        requirement: dict[str, Any],
    ) -> list[Finding]:
        """Validate AI findings: confidence gate + deterministic grounding."""
        return _validate_findings_standalone(
            raw_findings, document_text, requirement, self.confidence_threshold
        )
