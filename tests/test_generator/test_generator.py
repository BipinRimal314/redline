"""Tests for the rule generation pipeline."""

import json
from pathlib import Path

import pytest
import yaml

from redline.generator import (
    GeneratedRule,
    GeneratedRuleSet,
    write_rule_set,
)


@pytest.fixture
def sample_rule_set() -> GeneratedRuleSet:
    return GeneratedRuleSet(
        regulation_id="TEST-REG",
        regulation_name="Test Regulation",
        authority="Test Authority",
        cfr_reference="Test CFR 123.456",
        document_types=["compliance-policy"],
        rules=[
            GeneratedRule(
                filename="TestVagueLanguage.yml",
                vale_config={
                    "extends": "existence",
                    "message": "Vague language: '%s'. Test Regulation requires specific terms.",
                    "link": "https://example.com/test-reg",
                    "level": "error",
                    "ignorecase": True,
                    "tokens": ["adequate controls", "reasonable efforts"],
                },
                regulation_paragraph="Section 1.1",
                requirement_id="TEST-01",
                requirement_description="Must avoid vague language",
                severity="error",
            ),
            GeneratedRule(
                filename="TestMissingDisclosure.yml",
                vale_config={
                    "extends": "existence",
                    "message": "Missing disclosure indicator: '%s'.",
                    "link": "https://example.com/test-reg",
                    "level": "warning",
                    "ignorecase": True,
                    "tokens": ["not applicable", "N/A"],
                },
                regulation_paragraph="Section 2.3",
                requirement_id="TEST-02",
                requirement_description="Must include required disclosures",
                severity="warning",
            ),
        ],
        generated_at="2026-04-06T00:00:00+00:00",
        model_used="test-model",
        source_file="test-regulation.md",
    )


def test_write_rule_set_creates_vale_rules(
    sample_rule_set: GeneratedRuleSet, tmp_path: Path
) -> None:
    vale_dir = tmp_path / "vale-packages" / "FinCompliance"
    reg_dir = tmp_path / "regulations"

    created = write_rule_set(sample_rule_set, vale_dir, reg_dir)

    assert len(created["vale_rules"]) == 2

    rule1 = vale_dir / "TestVagueLanguage.yml"
    assert rule1.exists()
    content = yaml.safe_load(rule1.read_text())
    assert content["extends"] == "existence"
    assert content["level"] == "error"
    assert "adequate controls" in content["tokens"]


def test_write_rule_set_creates_regulation_yaml(
    sample_rule_set: GeneratedRuleSet, tmp_path: Path
) -> None:
    vale_dir = tmp_path / "vale-packages" / "FinCompliance"
    reg_dir = tmp_path / "regulations"

    write_rule_set(sample_rule_set, vale_dir, reg_dir)

    reg_yaml = reg_dir / "test_reg" / "test_reg.yml"
    assert reg_yaml.exists()

    data = yaml.safe_load(reg_yaml.read_text())
    reg = data["regulation"]
    assert reg["id"] == "TEST-REG"
    assert reg["authority"] == "Test Authority"
    assert len(reg["requirements"]) == 2
    assert reg["requirements"][0]["vale_rule"] == "FinCompliance.TestVagueLanguage"
    assert reg["requirements"][0]["regulation_paragraph"] == "Section 1.1"


def test_write_rule_set_creates_audit_trail(
    sample_rule_set: GeneratedRuleSet, tmp_path: Path
) -> None:
    vale_dir = tmp_path / "vale-packages" / "FinCompliance"
    reg_dir = tmp_path / "regulations"

    created = write_rule_set(sample_rule_set, vale_dir, reg_dir)

    assert len(created["audit_trail"]) == 1
    audit_path = created["audit_trail"][0]
    assert audit_path.exists()

    audit = json.loads(audit_path.read_text())
    assert audit["regulation_id"] == "TEST-REG"
    assert audit["model_used"] == "test-model"
    assert audit["rule_count"] == 2
    assert len(audit["mappings"]) == 2
    assert audit["mappings"][0]["regulation_paragraph"] == "Section 1.1"
    assert audit["mappings"][0]["vale_rule"] == "FinCompliance.TestVagueLanguage"


def test_write_rule_set_regulation_paragraph_traceability(
    sample_rule_set: GeneratedRuleSet, tmp_path: Path
) -> None:
    """Every rule must trace back to a specific regulation paragraph."""
    vale_dir = tmp_path / "vale-packages" / "FinCompliance"
    reg_dir = tmp_path / "regulations"

    write_rule_set(sample_rule_set, vale_dir, reg_dir)

    reg_yaml = reg_dir / "test_reg" / "test_reg.yml"
    data = yaml.safe_load(reg_yaml.read_text())

    for req in data["regulation"]["requirements"]:
        assert "regulation_paragraph" in req
        assert req["regulation_paragraph"], "Regulation paragraph must not be empty"


def test_generated_rule_is_immutable() -> None:
    rule = GeneratedRule(
        filename="Test.yml",
        vale_config={"extends": "existence"},
        regulation_paragraph="Section 1",
        requirement_id="T-01",
        requirement_description="Test",
        severity="warning",
    )
    with pytest.raises(AttributeError):
        rule.filename = "Changed.yml"  # type: ignore[misc]
