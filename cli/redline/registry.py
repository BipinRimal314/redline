"""Loads regulation YAML files and maps Vale rules to regulatory requirements."""

from pathlib import Path
from typing import Any

import yaml


class Registry:
    """Registry of regulatory requirements loaded from YAML files."""

    def __init__(self, regulations_dir: Path) -> None:
        self.regulations: dict[str, dict[str, Any]] = {}
        self._vale_rule_index: dict[str, list[dict[str, Any]]] = {}
        self._load_all(regulations_dir)

    def _load_all(self, regulations_dir: Path) -> None:
        for yml_path in sorted(regulations_dir.rglob("*.yml")):
            data = yaml.safe_load(yml_path.read_text())
            if data and "regulation" in data:
                reg = data["regulation"]
                self.regulations[reg["id"]] = reg
                self._index_vale_rules(reg)

    def _index_vale_rules(self, regulation: dict[str, Any]) -> None:
        for req in regulation.get("requirements", []):
            vale_rule = req.get("vale_rule")
            if vale_rule:
                entry = {
                    "regulation_id": regulation["id"],
                    "regulation_name": regulation["name"],
                    "authority": regulation["authority"],
                    "cfr_reference": regulation["cfr_reference"],
                    **req,
                }
                if vale_rule not in self._vale_rule_index:
                    self._vale_rule_index[vale_rule] = []
                self._vale_rule_index[vale_rule].append(entry)

    def get_regulation(self, regulation_id: str) -> dict[str, Any] | None:
        return self.regulations.get(regulation_id)

    def get_requirements_for_vale_rule(
        self, vale_rule: str
    ) -> list[dict[str, Any]]:
        return self._vale_rule_index.get(vale_rule, [])

    def get_regulations_for_document_type(
        self, document_type: str
    ) -> list[dict[str, Any]]:
        return [
            reg
            for reg in self.regulations.values()
            if document_type in reg.get("document_types", [])
        ]

    def list_regulation_ids(self) -> list[str]:
        return sorted(self.regulations.keys())

    def get_ai_requirements(
        self, document_type: str
    ) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for reg in self.get_regulations_for_document_type(document_type):
            for req in reg.get("requirements", []):
                if req.get("check_type") == "ai":
                    results.append(
                        {
                            "regulation_id": reg["id"],
                            "authority": reg["authority"],
                            **req,
                        }
                    )
        return results
