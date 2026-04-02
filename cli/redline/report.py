"""Gap report generation from compliance findings."""

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from redline import __version__
from redline.runner import Finding


TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


def generate_report(
    findings: list[Finding],
    document: str,
    regulations_checked: list[str],
    output_format: str = "json",
) -> str:
    """Generate a compliance gap report in the specified format."""
    report_data = _build_report_data(findings, document, regulations_checked)

    if output_format == "json":
        return json.dumps(report_data, indent=2)

    if output_format == "markdown":
        return _render_markdown(report_data)

    raise ValueError(f"Unsupported output format: {output_format}")


def _build_report_data(
    findings: list[Finding],
    document: str,
    regulations_checked: list[str],
) -> dict[str, Any]:
    level_counts = Counter(f.level for f in findings)
    source_counts = Counter(f.source for f in findings)
    reg_counts = Counter(
        f.regulation_id for f in findings if f.regulation_id
    )

    total = len(findings)
    error_count = level_counts.get("error", 0)
    pass_rate = (
        "100%"
        if total == 0
        else f"{max(0, 100 - (error_count / max(total, 1) * 100)):.0f}%"
    )

    return {
        "report": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "redline_version": __version__,
            "document": document,
            "regulations_checked": regulations_checked,
        },
        "summary": {
            "total_findings": total,
            "errors": level_counts.get("error", 0),
            "warnings": level_counts.get("warning", 0),
            "suggestions": level_counts.get("suggestion", 0),
            "by_source": dict(source_counts),
            "by_regulation": dict(reg_counts),
            "pass_rate": pass_rate,
        },
        "findings": [
            {
                "id": f"FC-{i+1:03d}",
                "source": f.source,
                "rule": f.rule,
                "regulation_id": f.regulation_id,
                "regulation_name": f.regulation_name,
                "authority": f.authority,
                "cfr_reference": f.cfr_reference,
                "requirement_id": f.requirement_id,
                "level": f.level,
                "line": f.line,
                "text": f.text,
                "message": f.message,
                "confidence": f.confidence,
            }
            for i, f in enumerate(findings)
        ],
    }


def _render_markdown(report_data: dict[str, Any]) -> str:
    if TEMPLATES_DIR.exists():
        env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
        try:
            template = env.get_template("report.md.j2")
            return template.render(**report_data)
        except Exception:
            pass

    # Fallback: inline markdown generation
    lines: list[str] = []
    lines.append("# Redline Compliance Gap Report\n")
    lines.append(f"**Document:** {report_data['report']['document']}")
    lines.append(f"**Generated:** {report_data['report']['generated_at']}")
    lines.append(
        f"**Regulations:** {', '.join(report_data['report']['regulations_checked'])}"
    )
    lines.append(f"**Pass Rate:** {report_data['summary']['pass_rate']}\n")

    summary = report_data["summary"]
    lines.append("## Summary\n")
    lines.append("| Level | Count |")
    lines.append("|---|---|")
    lines.append(f"| Errors | {summary['errors']} |")
    lines.append(f"| Warnings | {summary['warnings']} |")
    lines.append(f"| Suggestions | {summary['suggestions']} |")
    lines.append(f"| **Total** | **{summary['total_findings']}** |\n")

    if report_data["findings"]:
        lines.append("## Findings\n")
        for f in report_data["findings"]:
            level_marker = {
                "error": "E",
                "warning": "W",
                "suggestion": "S",
            }.get(f["level"], "?")
            lines.append(f"### [{level_marker}] {f['id']}: {f['rule']}\n")
            lines.append(f"**Line {f['line']}:** `{f['text']}`\n")
            lines.append(f"{f['message']}\n")
            if f.get("regulation_id"):
                lines.append(
                    f"**Regulation:** {f['regulation_id']} ({f['authority']}) — {f['cfr_reference']}\n"
                )
    else:
        lines.append("## Findings\n")
        lines.append(
            "No findings. Document passes all checked regulations.\n"
        )

    return "\n".join(lines)
