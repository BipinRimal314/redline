"""Redline CLI -- compliance documentation linter."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from redline import __version__
from redline.config import load_config
from redline.registry import Registry
from redline.report import generate_report
from redline.runner import ValeRunner

app = typer.Typer(
    name="redline",
    help="Compliance documentation linter for financial regulations.",
    no_args_is_help=True,
)
regulations_app = typer.Typer(help="Browse available regulations.")
app.add_typer(regulations_app, name="regulations")

console = Console()

REPO_ROOT = Path(__file__).parent.parent.parent
VALE_INI = REPO_ROOT / ".vale.ini"
REGULATIONS_DIR = REPO_ROOT / "regulations"


def _get_runner() -> ValeRunner:
    return ValeRunner(vale_config=VALE_INI, regulations_dir=REGULATIONS_DIR)


@app.command()
def lint(
    path: Path = typer.Argument(..., help="File or directory to lint"),
    ai: bool = typer.Option(
        False, "--ai", help="Enable AI semantic analysis (requires ANTHROPIC_API_KEY)"
    ),
) -> None:
    """Lint compliance documents against regulatory rules."""
    if not path.exists():
        console.print(f"[red]Error:[/red] {path} does not exist")
        raise typer.Exit(code=2)

    try:
        runner = _get_runner()
    except RuntimeError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)

    files = [path] if path.is_file() else sorted(path.glob("**/*.md"))
    if not files:
        console.print(f"[yellow]No markdown files found in {path}[/yellow]")
        raise typer.Exit(code=0)

    all_findings = []
    for file in files:
        findings = runner.lint(file)
        all_findings.extend(findings)

    errors = [f for f in all_findings if f.level == "error"]
    warnings = [f for f in all_findings if f.level == "warning"]
    suggestions = [f for f in all_findings if f.level == "suggestion"]

    if all_findings:
        table = Table(title="Compliance Findings")
        table.add_column("Level", style="bold")
        table.add_column("Line", justify="right")
        table.add_column("Rule")
        table.add_column("Message")
        table.add_column("Regulation")

        for f in all_findings:
            level_style = {
                "error": "red",
                "warning": "yellow",
                "suggestion": "blue",
            }.get(f.level, "white")
            table.add_row(
                f"[{level_style}]{f.level}[/{level_style}]",
                str(f.line),
                f.rule,
                f.message[:80],
                f.regulation_id or "-",
            )

        console.print(table)

    console.print(
        f"\n{len(errors)} error(s), {len(warnings)} warning(s), {len(suggestions)} suggestion(s)"
    )

    if errors:
        raise typer.Exit(code=1)


@app.command()
def report(
    path: Path = typer.Argument(..., help="File or directory to analyze"),
    format: str = typer.Option(
        "json", "--format", "-f", help="Output format: json, markdown"
    ),
) -> None:
    """Generate a compliance gap report."""
    if not path.exists():
        console.print(f"[red]Error:[/red] {path} does not exist")
        raise typer.Exit(code=2)

    try:
        runner = _get_runner()
    except RuntimeError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)

    files = [path] if path.is_file() else sorted(path.glob("**/*.md"))
    all_findings = []
    for file in files:
        all_findings.extend(runner.lint(file))

    config = load_config(path.parent / ".redline.yml")
    output = generate_report(
        findings=all_findings,
        document=str(path),
        regulations_checked=config.regulations,
        output_format=format,
    )
    console.print(output)


@regulations_app.command("list")
def regulations_list() -> None:
    """List all available regulations."""
    registry = Registry(REGULATIONS_DIR)
    table = Table(title="Available Regulations")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Authority")
    table.add_column("Requirements", justify="right")

    for reg_id in registry.list_regulation_ids():
        reg = registry.get_regulation(reg_id)
        if reg:
            table.add_row(
                reg["id"],
                reg["name"],
                reg["authority"],
                str(len(reg["requirements"])),
            )

    console.print(table)


@regulations_app.command("info")
def regulations_info(
    regulation_id: str = typer.Argument(
        ..., help="Regulation ID (e.g., BSA-SAR)"
    ),
) -> None:
    """Show details for a specific regulation."""
    registry = Registry(REGULATIONS_DIR)
    reg = registry.get_regulation(regulation_id)

    if not reg:
        console.print(f"[red]Regulation '{regulation_id}' not found.[/red]")
        raise typer.Exit(code=1)

    console.print(f"\n[bold]{reg['id']}[/bold] -- {reg['name']}")
    console.print(f"Authority: {reg['authority']}")
    console.print(f"CFR Reference: {reg['cfr_reference']}")
    console.print(f"Document Types: {', '.join(reg['document_types'])}")
    console.print(f"\nRequirements ({len(reg['requirements'])}):\n")

    table = Table()
    table.add_column("ID")
    table.add_column("Description")
    table.add_column("Severity")
    table.add_column("Check")

    for req in reg["requirements"]:
        table.add_row(
            req["id"],
            req["description"][:60],
            req["severity"],
            req["check_type"],
        )

    console.print(table)


@app.command()
def init(
    directory: Path = typer.Option(
        ".", help="Directory to create .redline.yml in"
    ),
) -> None:
    """Initialize a .redline.yml config file."""
    config_path = directory / ".redline.yml"
    if config_path.exists():
        console.print(f"[yellow]{config_path} already exists[/yellow]")
        raise typer.Exit(code=0)

    config_path.write_text(
        """# Redline compliance linter configuration
regulations:
  - bsa-aml

# Map file patterns to document types
# document_types:
#   policies/*.md: compliance-policy
#   sar/*.md: sar-narrative

output:
  format: json
  directory: .redline/reports

ai:
  enabled: false
  # model: claude-sonnet-4-20250514
  # confidence_threshold: 0.7
"""
    )
    console.print(f"[green]Created {config_path}[/green]")


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="Show version"
    ),
) -> None:
    if version:
        console.print(f"redline {__version__}")
        raise typer.Exit()
