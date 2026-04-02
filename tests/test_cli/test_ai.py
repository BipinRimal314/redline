"""Tests for AI semantic analysis module (mocked API calls)."""

import json
from unittest.mock import MagicMock, patch

import pytest

from redline.ai import AIAnalyzer, AIPrompt, PROMPTS, _validate_findings_standalone
from redline.runner import Finding


class TestPromptRegistry:
    def test_prompts_dict_is_not_empty(self):
        assert len(PROMPTS) > 0

    def test_all_prompts_have_required_fields(self):
        for key, prompt in PROMPTS.items():
            assert prompt.key == key
            assert prompt.category in ("adequacy", "consistency", "clarity")
            assert len(prompt.system_prompt) > 0
            assert len(prompt.user_template) > 0
            assert "{document_text}" in prompt.user_template

    def test_sar_prompts_exist(self):
        assert "sar_activity_pattern_adequacy" in PROMPTS
        assert "sar_detection_method" in PROMPTS
        assert "sar_five_ws_coverage" in PROMPTS

    def test_sec_prompts_exist(self):
        assert "sec_net_of_fees_adequacy" in PROMPTS
        assert "sec_risk_disclosure_adequacy" in PROMPTS

    def test_sox_prompts_exist(self):
        assert "sox_control_effectiveness_evaluation" in PROMPTS


class TestFindingValidation:
    def test_filters_below_confidence_threshold(self):
        raw_findings = [
            {
                "text": "some text",
                "issue": "low confidence issue",
                "regulation_id": "TEST-01",
                "severity": "warning",
                "confidence": 0.3,
            }
        ]
        requirement = {"regulation_id": "TEST", "authority": "TEST"}
        result = _validate_findings_standalone(
            raw_findings, "some text in the document", requirement, 0.7
        )
        assert len(result) == 0

    def test_passes_above_confidence_threshold(self):
        raw_findings = [
            {
                "text": "specific quote",
                "issue": "high confidence issue",
                "regulation_id": "TEST-01",
                "severity": "error",
                "confidence": 0.9,
            }
        ]
        requirement = {"regulation_id": "TEST", "authority": "TEST"}
        result = _validate_findings_standalone(
            raw_findings, "document with specific quote in it", requirement, 0.7
        )
        assert len(result) == 1
        assert result[0].confidence == 0.9
        assert result[0].source == "ai"

    def test_rejects_hallucinated_quotes(self):
        raw_findings = [
            {
                "text": "text that does not exist in document",
                "issue": "hallucinated finding",
                "regulation_id": "TEST-01",
                "severity": "error",
                "confidence": 0.95,
            }
        ]
        requirement = {"regulation_id": "TEST", "authority": "TEST"}
        result = _validate_findings_standalone(
            raw_findings, "completely different document content", requirement, 0.7
        )
        assert len(result) == 0

    def test_allows_not_found_text(self):
        raw_findings = [
            {
                "text": "not found",
                "issue": "missing content",
                "regulation_id": "TEST-01",
                "severity": "warning",
                "confidence": 0.8,
            }
        ]
        requirement = {"regulation_id": "TEST", "authority": "TEST"}
        result = _validate_findings_standalone(
            raw_findings, "any document text", requirement, 0.7
        )
        assert len(result) == 1

    def test_findings_have_ai_source(self):
        raw_findings = [
            {
                "text": "found text",
                "issue": "an issue",
                "regulation_id": "TEST-01",
                "severity": "error",
                "confidence": 0.85,
            }
        ]
        requirement = {"regulation_id": "TEST", "authority": "TEST"}
        result = _validate_findings_standalone(
            raw_findings, "document with found text here", requirement, 0.7
        )
        assert len(result) == 1
        assert result[0].source == "ai"
        assert result[0].rule.startswith("AI.")


class TestAIAnalyzerInit:
    def test_raises_without_api_key(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
                AIAnalyzer(api_key=None)

    def test_raises_without_anthropic_package(self):
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            with patch.dict("sys.modules", {"anthropic": None}):
                with pytest.raises(ImportError):
                    AIAnalyzer(api_key="test-key")
