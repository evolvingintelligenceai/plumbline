"""Verify engine — wraps Seraph's tiered code verification.

Calls Seraph's core layer directly (run_checks, run_gate + formatters).
"""

from __future__ import annotations

import os
from pathlib import Path

_NOT_INSTALLED = (
    "Plumbline Verify engine is not installed. "
    "Run: pip install plumbline-ai[verify]"
)


def _get_repo_path(project_root: str = "") -> Path:
    """Determine repo path from arg, env, or cwd."""
    if project_root:
        return Path(project_root).resolve()
    return Path(os.environ.get("SERAPH_REPO_PATH", os.getcwd())).resolve()


async def run_check(file_path: str, diff: str = "", project_root: str = "") -> str:
    """Tier 1 fast pre-write checks."""
    try:
        from seraph.config import SeraphConfig
        from seraph.core.checks import run_checks
        from seraph.mcp.formatters import format_check_result
    except ImportError:
        return _NOT_INSTALLED

    repo_path = _get_repo_path(project_root)
    config = SeraphConfig.load(repo_path)
    try:
        result = run_checks(
            file_path=file_path,
            content="",  # content read from file at check time
            diff=diff,
        )
        return format_check_result(result, max_chars=config.pipeline.max_output_chars)
    except Exception as exc:
        return f"Check failed: {exc}"


async def run_gate(project_root: str = "") -> str:
    """Tier 2 pre-commit verification gate."""
    try:
        from seraph.config import SeraphConfig
        from seraph.core.gate import run_gate as _run_gate
        from seraph.mcp.formatters import format_gate_result
    except ImportError:
        return _NOT_INSTALLED

    repo_path = _get_repo_path(project_root)
    config = SeraphConfig.load(repo_path)
    try:
        import subprocess

        diff = subprocess.run(
            ["git", "diff", "--cached"],
            cwd=str(repo_path),
            capture_output=True,
            text=True,
            check=False,
        ).stdout
        if not diff:
            return "Nothing staged. Stage your changes with `git add` before verifying."

        result = _run_gate(
            repo_path=repo_path,
            diff=diff,
        )
        return format_gate_result(result, max_chars=config.pipeline.max_output_chars)
    except Exception as exc:
        return f"Gate failed: {exc}"


async def explain_finding(
    finding_id: str, project_root: str = ""
) -> str:
    """Explain a check/gate finding in detail."""
    try:
        from seraph.mcp.formatters import format_explain
    except ImportError:
        return _NOT_INSTALLED

    try:
        return format_explain(
            check_category=finding_id,
            description="",
        )
    except Exception as exc:
        return f"Explain failed: {exc}"
