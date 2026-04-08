from pathlib import Path

from redline.registry import Registry

REPO_ROOT = Path(__file__).parent.parent.parent
REGULATIONS_DIR = REPO_ROOT / "regulations"


class TestRegistry:
    def setup_method(self):
        self.registry = Registry(REGULATIONS_DIR)

    def test_loads_all_regulation_files(self):
        assert len(self.registry.regulations) > 0

    def test_loads_bsa_sar(self):
        reg = self.registry.get_regulation("BSA-SAR")
        assert reg is not None
        assert reg["name"] == "Suspicious Activity Report Narrative Requirements"

    def test_loads_requirements(self):
        reg = self.registry.get_regulation("BSA-SAR")
        assert len(reg["requirements"]) > 0

    def test_get_requirements_by_vale_rule(self):
        reqs = self.registry.get_requirements_for_vale_rule(
            "FinCompliance.ProhibitedLanguage"
        )
        assert len(reqs) > 0

    def test_get_regulations_for_document_type(self):
        regs = self.registry.get_regulations_for_document_type("sar-narrative")
        assert any(r["id"] == "BSA-SAR" for r in regs)

    def test_list_all_regulation_ids(self):
        ids = self.registry.list_regulation_ids()
        assert "BSA-SAR" in ids
        assert "BSA-AML-PROG" in ids
        assert "BSA-CDD" in ids
        assert "BSA-CTR" in ids

    def test_get_nonexistent_regulation_returns_none(self):
        assert self.registry.get_regulation("DOES-NOT-EXIST") is None

    def test_get_ai_requirements_returns_empty(self):
        """All rules are now deterministic; no AI requirements remain."""
        ai_reqs = self.registry.get_ai_requirements("sar-narrative")
        assert len(ai_reqs) == 0

    def test_all_rules_are_deterministic(self):
        for reg in self.registry.regulations.values():
            for req in reg.get("requirements", []):
                assert req["check_type"] == "deterministic", (
                    f"{req['id']} is {req['check_type']}, expected deterministic"
                )

    def test_all_rules_have_legal_text(self):
        for reg in self.registry.regulations.values():
            for req in reg.get("requirements", []):
                assert "legal_text" in req, (
                    f"{req['id']} is missing legal_text field"
                )
                assert len(req["legal_text"]) > 0, (
                    f"{req['id']} has empty legal_text"
                )
