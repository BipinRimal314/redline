import json
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).parent.parent.parent
SCHEMA_PATH = REPO_ROOT / "regulations" / "schema.json"
REGULATIONS_DIR = REPO_ROOT / "regulations"


def test_schema_file_exists():
    assert SCHEMA_PATH.exists(), "regulations/schema.json must exist"


def test_schema_is_valid_json():
    schema = json.loads(SCHEMA_PATH.read_text())
    assert "properties" in schema
    assert "regulation" in schema["properties"]


def test_bsa_aml_sar_narrative_loads():
    path = REGULATIONS_DIR / "bsa-aml" / "sar-narrative.yml"
    assert path.exists(), "bsa-aml/sar-narrative.yml must exist"
    data = yaml.safe_load(path.read_text())
    reg = data["regulation"]
    assert reg["id"] == "BSA-SAR"
    assert reg["authority"] == "FinCEN"
    assert len(reg["requirements"]) > 0


def test_all_regulation_files_have_required_fields():
    required_fields = {
        "id",
        "name",
        "authority",
        "cfr_reference",
        "document_types",
        "requirements",
    }
    for yml_path in REGULATIONS_DIR.rglob("*.yml"):
        data = yaml.safe_load(yml_path.read_text())
        assert "regulation" in data, f"{yml_path} missing 'regulation' key"
        reg = data["regulation"]
        missing = required_fields - set(reg.keys())
        assert not missing, f"{yml_path} missing fields: {missing}"


def test_all_requirements_have_required_fields():
    req_fields = {"id", "description", "severity", "check_type"}
    for yml_path in REGULATIONS_DIR.rglob("*.yml"):
        data = yaml.safe_load(yml_path.read_text())
        for req in data["regulation"]["requirements"]:
            missing = req_fields - set(req.keys())
            assert not missing, (
                f"{yml_path} requirement {req.get('id', '?')} missing: {missing}"
            )
