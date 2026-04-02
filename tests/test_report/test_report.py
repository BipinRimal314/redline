import json

from redline.runner import Finding
from redline.report import generate_report


SAMPLE_FINDINGS = [
    Finding(
        rule="FinCompliance.BSA-AML.ProhibitedLanguage",
        message="Prohibited vague language: 'large amount'",
        level="error",
        line=5,
        text="large amount",
        source="deterministic",
        regulation_id="BSA-SAR",
        regulation_name="SAR Narrative Requirements",
        authority="FinCEN",
        cfr_reference="31 CFR 1020.320",
        requirement_id="SAR-02",
        confidence=1.0,
    ),
    Finding(
        rule="FinCompliance.PassiveVoice",
        message="Passive voice detected",
        level="suggestion",
        line=10,
        text="was submitted",
        source="deterministic",
        regulation_id=None,
        regulation_name=None,
        authority=None,
        cfr_reference=None,
        requirement_id=None,
        confidence=1.0,
    ),
]


class TestReportGeneration:
    def test_json_report_is_valid_json(self):
        output = generate_report(
            findings=SAMPLE_FINDINGS,
            document="test.md",
            regulations_checked=["BSA-AML"],
            output_format="json",
        )
        data = json.loads(output)
        assert "report" in data
        assert "summary" in data
        assert "findings" in data

    def test_json_report_has_correct_summary(self):
        output = generate_report(
            findings=SAMPLE_FINDINGS,
            document="test.md",
            regulations_checked=["BSA-AML"],
            output_format="json",
        )
        data = json.loads(output)
        assert data["summary"]["total_findings"] == 2
        assert data["summary"]["errors"] == 1
        assert data["summary"]["suggestions"] == 1

    def test_json_report_findings_have_regulation_mapping(self):
        output = generate_report(
            findings=SAMPLE_FINDINGS,
            document="test.md",
            regulations_checked=["BSA-AML"],
            output_format="json",
        )
        data = json.loads(output)
        first = data["findings"][0]
        assert first["regulation_id"] == "BSA-SAR"
        assert first["authority"] == "FinCEN"

    def test_markdown_report_contains_findings(self):
        output = generate_report(
            findings=SAMPLE_FINDINGS,
            document="test.md",
            regulations_checked=["BSA-AML"],
            output_format="markdown",
        )
        assert "Prohibited vague language" in output
        assert "error" in output.lower()

    def test_empty_findings_produce_clean_report(self):
        output = generate_report(
            findings=[],
            document="test.md",
            regulations_checked=["BSA-AML"],
            output_format="json",
        )
        data = json.loads(output)
        assert data["summary"]["total_findings"] == 0
        assert data["summary"]["pass_rate"] == "100%"
