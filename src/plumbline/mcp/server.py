"""Plumbline MCP server — unified agent surface for write-time verification."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger("plumbline")

mcp = FastMCP(
    "plumbline",
    instructions="Write-time verification for AI-generated code",
)


# ---------------------------------------------------------------------------
# Context tools (powered by Sentinel)
# ---------------------------------------------------------------------------


@mcp.tool()
async def plumbline_context(project_root: str = "") -> str:
    """Get project intelligence at session start.

    Returns conventions, pitfalls, architectural decisions, hot files,
    and co-change patterns — everything an AI needs to write
    project-consistent code. Call this first.
    """
    from plumbline.context.engine import get_project_context

    return await get_project_context(project_root)


@mcp.tool()
async def plumbline_query(query: str, limit: int = 20, project_root: str = "") -> str:
    """Search project knowledge mid-task.

    Free-text search across conventions, decisions, pitfalls, and patterns.
    Use when you need to look something up: 'Has this pattern been tried before?'
    'What's the convention for error handling here?'
    """
    from plumbline.context.engine import search_knowledge

    return await search_knowledge(query, limit, project_root)


@mcp.tool()
async def plumbline_co_changes(file_path: str, limit: int = 50, project_root: str = "") -> str:
    """Find files that change together with this file.

    Call before editing a file. If auth.py and auth_test.py always change
    together, you should read auth_test.py before editing auth.py.
    Prevents the 'fixed the function, forgot the test' mistake.
    """
    from plumbline.context.engine import get_co_changes

    return await get_co_changes(file_path, limit, project_root)


# ---------------------------------------------------------------------------
# Verify tools (powered by Seraph)
# ---------------------------------------------------------------------------


@mcp.tool()
async def plumbline_check(file_path: str, diff: str = "", project_root: str = "") -> str:
    """Fast pre-write verification. Run before writing or editing a file.

    Checks imports, security surface, escalation detection, and spec drift.
    Returns ALLOW or BLOCK with structured findings. Target: <500ms.

    If BLOCK: do not write the file. Read the findings. Fix first.
    """
    from plumbline.verify.engine import run_check

    return await run_check(file_path, diff, project_root)


@mcp.tool()
async def plumbline_verify(project_root: str = "") -> str:
    """Deep pre-commit verification. Run before committing.

    Runs targeted mutation testing on changed lines and spec compliance
    checks. Returns ACCEPT, ACCEPT_WITH_WARNINGS, REJECT, or PARTIAL.
    Target: <30s.

    Surviving mutants are reported as questions: 'Your code still passes
    tests if X is changed to Y. Is that intentional?'

    If REJECT: do not commit. Read the findings. Fix first.
    """
    from plumbline.verify.engine import run_gate

    return await run_gate(project_root)


@mcp.tool()
async def plumbline_explain(finding_id: str, project_root: str = "") -> str:
    """Explain a rejection in detail.

    After plumbline_check returns BLOCK or plumbline_verify returns REJECT,
    call this with the finding ID to understand: what was detected, why it
    matters, what the fix should look like, and what the confidence score means.
    """
    from plumbline.verify.engine import explain_finding

    return await explain_finding(finding_id, project_root)


# ---------------------------------------------------------------------------
# Gate tools (powered by Morpheus)
# ---------------------------------------------------------------------------


@mcp.tool()
async def plumbline_init(plan_file: str) -> str:
    """Start tracking a development plan.

    Load a markdown plan file, parse tasks, and begin tracking state.
    Use this when starting multi-step work (3+ tasks). The plan keeps
    you honest — evidence gates prevent quality decay on later tasks.
    """
    from plumbline.gate.engine import init_plan

    return await init_plan(plan_file)


@mcp.tool()
async def plumbline_advance(
    task_id: str,
    phase: str,
    evidence: dict[str, Any] | None = None,
) -> str:
    """Advance a task through a phase gate with evidence.

    Each phase requires specific evidence. The gate validates your evidence
    is real (not bare assertions like 'yes' or 'ok'). Returns success with
    next phase instructions, or rejection with what's missing.

    Phases: CHECK → CODE → TEST → GRADE → COMMIT → ADVANCE
    """
    from plumbline.gate.engine import advance_task

    return await advance_task(task_id, phase, evidence or {})


@mcp.tool()
async def plumbline_status(plan_id: str = "") -> str:
    """Check plan progress and current state.

    Returns task states, active phase, and completion percentage.
    If plan_id is omitted, returns the most recently created plan.
    """
    from plumbline.gate.engine import get_status

    return await get_status(plan_id)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the Plumbline MCP server."""
    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
