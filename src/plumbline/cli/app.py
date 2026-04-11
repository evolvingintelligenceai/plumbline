"""Plumbline CLI — setup, diagnostics, and power-user tools."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="plumbline",
    help="Write-time verification for AI-generated code.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def setup() -> None:
    """Configure Plumbline for this project.

    Generates the mcp.json entry and installs the /btw hook.
    """
    mcp_config = {
        "mcpServers": {
            "plumbline": {
                "command": "plumbline-mcp",
                "args": [],
            }
        }
    }

    console.print("\n[bold]Plumbline Setup[/bold]\n")
    console.print("Add this to your .mcp.json:\n")
    console.print_json(json.dumps(mcp_config))

    hook_config = {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Write|Edit",
                    "command": "python -m plumbline.hooks.btw",
                }
            ]
        }
    }

    console.print("\nAdd this to your Claude Code settings for the /btw hook:\n")
    console.print_json(json.dumps(hook_config))
    console.print("\n[green]Done.[/green] Restart Claude Code to activate.\n")


@app.command()
def doctor() -> None:
    """Check which Plumbline engines are installed and healthy."""
    table = Table(title="Plumbline Health Check")
    table.add_column("Engine", style="bold")
    table.add_column("Package")
    table.add_column("Status")
    table.add_column("Version")

    engines = [
        ("Context", "git-sentinel", "sentinel"),
        ("Verify", "seraph-ai", "seraph"),
        ("Gate", "morpheus-mcp", "morpheus_mcp"),
    ]

    for name, package, module in engines:
        try:
            mod = __import__(module)
            version = getattr(mod, "__version__", "unknown")
            table.add_row(name, package, "[green]OK[/green]", version)
        except ImportError:
            table.add_row(name, package, "[red]NOT INSTALLED[/red]", "-")

    console.print()
    console.print(table)
    console.print()


@app.command()
def version() -> None:
    """Print Plumbline version."""
    from plumbline import __version__

    console.print(f"plumbline-ai {__version__}")


def main() -> None:
    """CLI entry point."""
    app()


if __name__ == "__main__":
    main()
