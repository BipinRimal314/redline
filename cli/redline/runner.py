"""Runs Vale as a subprocess and maps findings to regulatory requirements."""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from redline.registry import Registry


@dataclass(frozen=True)
class Finding:
    """A single compliance finding from Vale or AI analysis."""

    rule: str
    message: str
    level: str
    line: int
    text: str
    source: str
    regulation_id: str | None
    regulation_name: str | None
    authority: str | None
    cfr_reference: str | None
    requirement_id: str | None
    confidence: float


def _check_vale_installed() -> None:
    try:
        subprocess.run(
            ["vale", "--version"],
            capture_output=True,
            check=True,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Vale is not installed. Install it: https://vale.sh/docs/install/"
        )


class ValeRunner:
    """Orchestrates Vale subprocess and maps results to regulations."""

    def __init__(
        self,
        vale_config: Path,
        regulations_dir: Path,
    ) -> None:
        _check_vale_installed()
        self.vale_config = vale_config
        self.registry = Registry(regulations_dir)

    def lint(self, file_path: Path) -> list[Finding]:
        raw_findings = self._run_vale(file_path)
        return self._map_to_findings(raw_findings)

    def _run_vale(self, file_path: Path) -> list[dict]:
        result = subprocess.run(
            [
                "vale",
                "--config",
                str(self.vale_config),
                "--output",
                "JSON",
                str(file_path),
            ],
            capture_output=True,
            text=True,
        )

        if not result.stdout.strip():
            return []

        data = json.loads(result.stdout)
        findings: list[dict] = []
        for file_findings in data.values():
            findings.extend(file_findings)
        return findings

    def _map_to_findings(self, raw_findings: list[dict]) -> list[Finding]:
        findings: list[Finding] = []
        for raw in raw_findings:
            rule = raw.get("Check", "")
            reg_mappings = self.registry.get_requirements_for_vale_rule(rule)

            if reg_mappings:
                for mapping in reg_mappings:
                    findings.append(
                        Finding(
                            rule=rule,
                            message=raw.get("Message", ""),
                            level=raw.get("Severity", "warning"),
                            line=raw.get("Line", 0),
                            text=raw.get("Match", ""),
                            source="deterministic",
                            regulation_id=mapping.get("regulation_id"),
                            regulation_name=mapping.get("regulation_name"),
                            authority=mapping.get("authority"),
                            cfr_reference=mapping.get("cfr_reference"),
                            requirement_id=mapping.get("id"),
                            confidence=1.0,
                        )
                    )
            else:
                findings.append(
                    Finding(
                        rule=rule,
                        message=raw.get("Message", ""),
                        level=raw.get("Severity", "warning"),
                        line=raw.get("Line", 0),
                        text=raw.get("Match", ""),
                        source="deterministic",
                        regulation_id=None,
                        regulation_name=None,
                        authority=None,
                        cfr_reference=None,
                        requirement_id=None,
                        confidence=1.0,
                    )
                )

        return findings
