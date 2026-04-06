"""Redline CLI -- compliance documentation linter."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from redline import __version__
from redline.config import load_config
from redline.generator import RuleGenerator, write_rule_set
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

    if ai:
        try:
            from redline.ai import AIAnalyzer

            config = load_config(path.parent / ".redline.yml" if path.is_file() else path / ".redline.yml")
            analyzer = AIAnalyzer(
                model=config.ai_model,
                confidence_threshold=config.confidence_threshold,
            )
            registry = Registry(REGULATIONS_DIR)
            for file in files:
                doc_text = file.read_text()
                ai_reqs = registry.get_ai_requirements("compliance-policy")
                if ai_reqs:
                    ai_findings = analyzer.analyze(doc_text, ai_reqs)
                    all_findings.extend(ai_findings)
                    console.print(
                        f"[dim]AI analysis: {len(ai_findings)} finding(s) for {file.name}[/dim]"
                    )
        except (ImportError, ValueError) as e:
            console.print(f"[yellow]AI analysis skipped:[/yellow] {e}")

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


@app.command()
def generate(
    source: Path = typer.Argument(..., help="Regulation text file (Markdown or plain text)"),
    regulation_id: str = typer.Option(..., "--id", help="Regulation ID (e.g., SOC2, GDPR, HIPAA)"),
    authority: str = typer.Option("", "--authority", help="Regulatory authority name"),
    document_types: str = typer.Option(
        "compliance-policy", "--doc-types", help="Comma-separated document types"
    ),
    model: str = typer.Option(
        "claude-sonnet-4-20250514", "--model", help="LLM model for rule generation"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Preview generated rules without writing files"
    ),
) -> None:
    """Generate Vale rules from regulation text. LLM reads the regulation once; rules run deterministically forever."""
    if not source.exists():
        console.print(f"[red]Error:[/red] {source} does not exist")
        raise typer.Exit(code=2)

    regulation_text = source.read_text()
    if len(regulation_text) < 100:
        console.print("[red]Error:[/red] Regulation text is too short. Provide the full regulation text.")
        raise typer.Exit(code=2)

    console.print(f"[bold]Reading regulation:[/bold] {source.name} ({len(regulation_text):,} chars)")
    console.print(f"[bold]Regulation ID:[/bold] {regulation_id}")
    console.print(f"[bold]Model:[/bold] {model}")
    console.print()

    try:
        gen = RuleGenerator(model=model)
    except (ValueError, ImportError) as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(code=2)

    with console.status("Generating rules from regulation text..."):
        rule_set = gen.generate(
            regulation_text=regulation_text,
            regulation_id=regulation_id,
            authority=authority,
            document_types=document_types.split(","),
            source_file=str(source),
        )

    console.print(f"\n[green]Generated {len(rule_set.rules)} rules[/green]\n")

    table = Table(title=f"Rules for {rule_set.regulation_name}")
    table.add_column("File")
    table.add_column("Requirement")
    table.add_column("Paragraph")
    table.add_column("Severity")
    table.add_column("Tokens", justify="right")

    for rule in rule_set.rules:
        table.add_row(
            rule.filename,
            rule.requirement_id,
            rule.regulation_paragraph,
            rule.severity,
            str(len(rule.vale_config.get("tokens", []))),
        )

    console.print(table)

    if dry_run:
        console.print("\n[yellow]Dry run — no files written.[/yellow]")
        return

    vale_dir = REPO_ROOT / "vale-packages" / "FinCompliance"
    created = write_rule_set(rule_set, vale_dir, REGULATIONS_DIR)

    console.print(f"\n[green]Written:[/green]")
    for category, paths in created.items():
        for p in paths:
            console.print(f"  {category}: {p.relative_to(REPO_ROOT)}")

    console.print(
        f"\n[bold]Next steps:[/bold]\n"
        f"  1. Review generated rules in vale-packages/FinCompliance/\n"
        f"  2. Review regulation YAML in regulations/\n"
        f"  3. Check audit trail for rule-to-paragraph mappings\n"
        f"  4. Test: redline lint <your-doc> to verify rules work\n"
        f"  5. Commit when satisfied"
    )


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", help="Show version"
    ),
) -> None:
    if version:
        console.print(f"redline {__version__}")
        raise typer.Exit()
