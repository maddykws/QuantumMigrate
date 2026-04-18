import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .scanner import scan_directory, clone_and_scan
from .reporter import print_rich_table, write_json, write_markdown

console = Console()


def _is_github_url(target: str) -> bool:
    return target.startswith("https://github.com") or target.startswith("git@github.com")


@click.group()
@click.version_option("0.1.0", prog_name="quantummigrate")
def cli() -> None:
    """QuantumMigrate — scan codebases for quantum-vulnerable cryptography."""


@cli.command()
@click.argument("target")
@click.option("--output", "-o", type=click.Choice(["table", "json", "markdown", "all"]), default="table", show_default=True, help="Output format.")
@click.option("--severity", "-s", type=click.Choice(["CRITICAL", "HIGH", "MEDIUM", "LOW"], case_sensitive=False), default=None, help="Filter by minimum severity.")
@click.option("--no-ai", is_flag=True, default=False, help="Skip Claude API analysis (pattern matching only).")
@click.option("--max-ai", default=20, show_default=True, help="Maximum number of findings to send to Claude API.")
@click.option("--json-out", default="quantum_report.json", show_default=True, help="JSON output file path.")
@click.option("--md-out", default="QUANTUM_MIGRATION.md", show_default=True, help="Markdown output file path.")
def scan(
    target: str,
    output: str,
    severity: str | None,
    no_ai: bool,
    max_ai: int,
    json_out: str,
    md_out: str,
) -> None:
    """Scan a local directory or GitHub URL for quantum-vulnerable cryptography.

    \b
    Examples:
      quantummigrate scan ./my-project
      quantummigrate scan https://github.com/owner/repo
      quantummigrate scan ./my-project --output json
      quantummigrate scan ./my-project --severity critical
      quantummigrate scan ./my-project --no-ai
    """
    use_ai = not no_ai and not os.environ.get("QUANTUM_MIGRATE_NO_AI", "").lower() in ("1", "true")

    if use_ai and not os.environ.get("ANTHROPIC_API_KEY"):
        console.print("[yellow]Warning: ANTHROPIC_API_KEY not set. Running in --no-ai mode.[/yellow]")
        use_ai = False

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as progress:
        if _is_github_url(target):
            task = progress.add_task(f"Cloning and scanning {target}...", total=None)
            try:
                findings, repo_dir = clone_and_scan(target, severity_filter=severity)
            except Exception as e:
                console.print(f"[red]Failed to clone repository: {e}[/red]")
                sys.exit(1)
            progress.update(task, description=f"Scanned {repo_dir}")
        else:
            local_path = Path(target).resolve()
            task = progress.add_task(f"Scanning {local_path}...", total=None)
            try:
                findings = scan_directory(local_path, severity_filter=severity)
            except FileNotFoundError as e:
                console.print(f"[red]{e}[/red]")
                sys.exit(1)
            progress.update(task, description=f"Scanned {len(findings)} finding(s)")

        analyses = None
        if use_ai and findings:
            from .analyzer import analyze_findings
            ai_task = progress.add_task(f"Analysing {min(max_ai, len(findings))} finding(s) with Claude...", total=None)
            analyses = analyze_findings(findings, max_ai=max_ai)
            progress.update(ai_task, description="AI analysis complete")

    if output in ("table", "all"):
        print_rich_table(findings, analyses)

    if output in ("json", "all"):
        write_json(findings, analyses, json_out)

    if output in ("markdown", "all"):
        write_markdown(findings, analyses, md_out)

    if not findings:
        sys.exit(0)

    has_critical = any(f.severity == "CRITICAL" for f in findings)
    sys.exit(2 if has_critical else 1)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
