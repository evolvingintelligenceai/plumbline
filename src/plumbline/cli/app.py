"""Plumbline CLI — setup, diagnostics, and power-user tools."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="plumbline",
    help="Write-time intelligence for AI-generated code.",
    no_args_is_help=True,
)
console = Console()


# ---------------------------------------------------------------------------
# setup — write config files, wire engines
# ---------------------------------------------------------------------------


@app.command()
def setup(
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would change without writing."
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite existing plumbline entries."
    ),
    skip_sentinel: bool = typer.Option(
        False, "--skip-sentinel", help="Skip Sentinel git-hook install + swarm."
    ),
) -> None:
    """Configure Plumbline for this project.

    Writes `.mcp.json` and `.claude/settings.json`, installs the `/btw`
    PreToolUse hook, installs Sentinel's git hooks, and runs an initial
    Sentinel swarm. Safe to re-run — existing entries are preserved unless
    `--force` is passed.
    """
    project_root = Path.cwd()
    venv_bin = Path(sys.executable).parent
    plumbline_mcp = venv_bin / "plumbline-mcp"
    plumbline_btw = venv_bin / "plumbline-btw"

    console.print("\n[bold]Plumbline Setup[/bold]\n")
    console.print(f"Project: {project_root}")
    console.print(f"Python:  {sys.executable}")
    if dry_run:
        console.print("[yellow]DRY RUN — no files will be written.[/yellow]")
    console.print()

    # 1. .mcp.json — register plumbline-mcp
    _configure_mcp_json(project_root, plumbline_mcp, dry_run=dry_run, force=force)

    # 2. .claude/settings.json — install /btw PreToolUse hook
    _configure_claude_hook(project_root, plumbline_btw, dry_run=dry_run, force=force)

    # 3. Sentinel — install git hooks + initial swarm
    if skip_sentinel:
        console.print("\n[dim]Skipping Sentinel wiring (--skip-sentinel).[/dim]")
    else:
        _configure_sentinel(project_root, venv_bin, dry_run=dry_run)

    console.print("\n[green]Setup complete.[/green]")
    if not dry_run:
        console.print(
            "If Claude Code is running in this project, restart it to activate "
            "the /btw hook."
        )


def _configure_mcp_json(
    project_root: Path, plumbline_mcp: Path, *, dry_run: bool, force: bool
) -> None:
    """Register plumbline in the project's .mcp.json, merging into existing config."""
    mcp_path = project_root / ".mcp.json"
    entry = {"command": str(plumbline_mcp), "args": []}

    if mcp_path.exists():
        try:
            config = json.loads(mcp_path.read_text())
        except json.JSONDecodeError:
            console.print(f"[red]✗[/red] {mcp_path} exists but isn't valid JSON — skipping.")
            return
        servers = config.setdefault("mcpServers", {})
        if "plumbline" in servers and not force:
            console.print(f"[yellow]•[/yellow] {mcp_path} already has `plumbline` entry — unchanged (use --force to overwrite).")
            return
        servers["plumbline"] = entry
        past, present = ("updated", "update") if "plumbline" in servers else ("extended", "extend")
    else:
        config = {"mcpServers": {"plumbline": entry}}
        past, present = "created", "create"

    if dry_run:
        console.print(f"[cyan]would {present}[/cyan] {mcp_path}:")
        console.print_json(json.dumps(config))
    else:
        mcp_path.write_text(json.dumps(config, indent=2) + "\n")
        console.print(f"[green]✓[/green] {past} {mcp_path}")


def _configure_claude_hook(
    project_root: Path, plumbline_btw: Path, *, dry_run: bool, force: bool
) -> None:
    """Install the /btw PreToolUse hook in .claude/settings.json.

    Uses the current Claude Code hook schema:
        hooks.PreToolUse[].hooks[] with {type: "command", command: "..."}
    """
    claude_dir = project_root / ".claude"
    settings_path = claude_dir / "settings.json"

    hook_entry = {"type": "command", "command": str(plumbline_btw)}

    if settings_path.exists():
        try:
            settings = json.loads(settings_path.read_text())
        except json.JSONDecodeError:
            console.print(
                f"[red]✗[/red] {settings_path} exists but isn't valid JSON — skipping."
            )
            return
    else:
        settings = {}

    hooks_section = settings.setdefault("hooks", {})
    pretooluse = hooks_section.setdefault("PreToolUse", [])

    # Check if a plumbline-btw hook entry is already present
    already_configured = False
    for matcher_block in pretooluse:
        inner_hooks = matcher_block.get("hooks", [])
        for h in inner_hooks:
            if h.get("command", "").endswith("plumbline-btw"):
                already_configured = True
                if force:
                    h["command"] = str(plumbline_btw)
                break
        if already_configured:
            break

    if already_configured and not force:
        console.print(
            f"[yellow]•[/yellow] {settings_path} already has a plumbline-btw hook — "
            f"unchanged (use --force to overwrite)."
        )
        return

    if not already_configured:
        pretooluse.append(
            {
                "matcher": "Write|Edit",
                "hooks": [hook_entry],
            }
        )

    if dry_run:
        console.print(f"[cyan]would write[/cyan] {settings_path}:")
        console.print_json(json.dumps(settings))
    else:
        claude_dir.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(json.dumps(settings, indent=2) + "\n")
        console.print(f"[green]✓[/green] wrote PreToolUse hook to {settings_path}")


def _configure_sentinel(project_root: Path, venv_bin: Path, *, dry_run: bool) -> None:
    """Install Sentinel git hooks and run initial swarm ingestion.

    Without this, the Context pillar never learns from commits. The Sentinel
    CLI handles its own idempotency — safe to re-run.
    """
    sentinel_cmd = venv_bin / "sentinel"
    if not sentinel_cmd.exists():
        # Fall back to PATH resolution
        sentinel_cmd_path = shutil.which("sentinel")
        if sentinel_cmd_path is None:
            console.print(
                "[yellow]•[/yellow] sentinel CLI not found — skipping hook install. "
                "Install via `pip install plumbline-ai[context]`."
            )
            return
        sentinel_cmd = Path(sentinel_cmd_path)

    if not (project_root / ".git").exists():
        console.print(
            "[yellow]•[/yellow] no .git directory — skipping Sentinel hook install "
            "(run `git init` first if you want Context pillar intelligence)."
        )
        return

    if dry_run:
        console.print(f"[cyan]would run[/cyan] {sentinel_cmd} watch --install")
        console.print(f"[cyan]would run[/cyan] {sentinel_cmd} swarm")
        return

    # Install git hooks
    try:
        result = subprocess.run(
            [str(sentinel_cmd), "watch", "--install"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        if result.returncode == 0:
            console.print("[green]✓[/green] installed Sentinel git hooks")
        else:
            console.print(f"[yellow]•[/yellow] sentinel watch --install exited {result.returncode}: {result.stderr.strip()[:200]}")
    except (subprocess.TimeoutExpired, OSError) as exc:
        console.print(f"[yellow]•[/yellow] sentinel watch --install failed: {exc}")

    # Run initial swarm to backfill commit history
    try:
        result = subprocess.run(
            [str(sentinel_cmd), "swarm"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        if result.returncode == 0:
            console.print("[green]✓[/green] ran initial Sentinel swarm")
        else:
            console.print(f"[yellow]•[/yellow] sentinel swarm exited {result.returncode}: {result.stderr.strip()[:200]}")
    except (subprocess.TimeoutExpired, OSError) as exc:
        console.print(f"[yellow]•[/yellow] sentinel swarm failed: {exc}")


# ---------------------------------------------------------------------------
# doctor — installation check
# ---------------------------------------------------------------------------


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
