"""CLI entry point for DeckLens Semantic Diff."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .diff.engine import Change, DiffEngine
from .parsers.openradioss import parse_deck

def _make_console() -> Console:
    import sys
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, Exception):
            pass
    return Console(highlight=False, safe_box=True)


console = _make_console()

_SEVERITY_STYLE = {
    "CRITICAL": "bold red",
    "WARNING":  "bold yellow",
    "INFO":     "cyan",
}
_SEVERITY_LABEL = {
    "CRITICAL": "CRIT",
    "WARNING":  "WARN",
    "INFO":     "INFO",
}


def _fmt_value(v, unit: str | None) -> str:
    if v is None:
        return "-"
    u = f" {unit}" if unit else ""
    if isinstance(v, float):
        return f"{v:g}{u}"
    return f"{v}{u}"


def _pct_text(pct: float | None) -> Text:
    if pct is None:
        return Text("")
    sign = "+" if pct > 0 else ""
    color = "red" if abs(pct) >= 20 else "yellow" if abs(pct) >= 5 else "green"
    return Text(f"{sign}{pct:.1f}%", style=color)


def _build_table(changes: list[Change]) -> Table:
    table = Table(
        show_header=True,
        header_style="bold white on dark_blue",
        border_style="bright_black",
        safe_box=True,
    )
    table.add_column("Sev",       style="bold",  no_wrap=True)
    table.add_column("Category",  no_wrap=True)
    table.add_column("Type / ID", no_wrap=True)
    table.add_column("Name")
    table.add_column("Field",     ratio=2)
    table.add_column("Before",    justify="right", no_wrap=True)
    table.add_column("After",     justify="right", no_wrap=True)
    table.add_column("Change",    justify="right", no_wrap=True)

    for ch in changes:
        style = _SEVERITY_STYLE[ch.severity]
        icon = Text("[" + _SEVERITY_LABEL[ch.severity] + "]", style=style)
        table.add_row(
            icon,
            Text(ch.category, style="dim"),
            Text(f"{ch.item_type}/{ch.item_id}", style="bright_white"),
            Text(str(ch.item_name), style="white"),
            Text(str(ch.field)),
            Text(_fmt_value(ch.old_value, None)),
            Text(_fmt_value(ch.new_value, ch.unit)),
            _pct_text(ch.percent_change),
        )

    return table


def _build_summary(changes: list[Change]) -> Panel:
    counts = {"CRITICAL": 0, "WARNING": 0, "INFO": 0}
    for ch in changes:
        counts[ch.severity] += 1

    parts = []
    for sev in ("CRITICAL", "WARNING", "INFO"):
        n = counts[sev]
        style = _SEVERITY_STYLE[sev]
        parts.append(Text(f"  {n} {sev}  ", style=style))

    content = Text("").join(parts)
    return Panel(content, title="[bold]Summary", expand=False)


@click.group()
@click.version_option(package_name="DeckLens-Semantic-Diff-for-CAE")
def main() -> None:
    """DeckLens: Semantic Diff for CAE input files."""


@main.command()
@click.argument("before", type=click.Path(exists=True, path_type=Path))
@click.argument("after", type=click.Path(exists=True, path_type=Path))
@click.option("--no-ai", is_flag=True, default=False, help="Skip Claude AI analysis.")
@click.option(
    "--format", "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format.",
)
@click.option("--model", default="claude-opus-4-8", show_default=True,
              help="Claude model ID for AI analysis.")
@click.option("--min-severity",
              type=click.Choice(["INFO", "WARNING", "CRITICAL"], case_sensitive=False),
              default="INFO", show_default=True,
              help="Minimum severity level to display.")
def diff(
    before: Path,
    after: Path,
    no_ai: bool,
    output_format: str,
    model: str,
    min_severity: str,
) -> None:
    """Compare two OpenRadioss deck files and show engineering-aware changes.

    BEFORE and AFTER are paths to .rad input files.
    """
    _sev_rank = {"INFO": 0, "WARNING": 1, "CRITICAL": 2}
    min_rank = _sev_rank[min_severity.upper()]

    # Parse
    with console.status("[bold green]Parsing decks...", spinner="dots"):
        try:
            deck_before = parse_deck(before)
            deck_after = parse_deck(after)
        except Exception as exc:
            console.print(f"[red]Parse error: {exc}")
            sys.exit(1)

    # Diff
    engine = DiffEngine()
    all_changes = engine.diff(deck_before, deck_after)
    changes = [ch for ch in all_changes if _sev_rank[ch.severity] >= min_rank]

    if output_format == "json":
        import dataclasses
        click.echo(json.dumps([dataclasses.asdict(ch) for ch in changes], indent=2))
        return

    # Rich text output
    console.print()
    console.rule(f"[bold blue]DeckLens Semantic Diff")
    console.print(f"  [dim]Before:[/dim] [white]{before}")
    console.print(f"  [dim]After: [/dim] [white]{after}")
    console.print()

    if not changes:
        console.print("[green]No changes found above the specified severity threshold.[/green]")
        return

    console.print(_build_summary(all_changes))
    console.print()
    console.print(_build_table(changes))

    # AI analysis
    if not no_ai:
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        import os
        if not os.environ.get("ANTHROPIC_API_KEY"):
            console.print(
                "\n[yellow]Tip: Set ANTHROPIC_API_KEY in .env for AI analysis. "
                "Use --no-ai to suppress this message.[/yellow]"
            )
            return

        from .explainer.claude import ClaudeExplainer
        with console.status("[bold green]Generating AI analysis...", spinner="dots"):
            explainer = ClaudeExplainer(model=model)
        explainer.explain(changes, str(before), str(after), console=console)
