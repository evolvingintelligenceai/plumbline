"""Tests for degraded-engine paths.

Each of the 9 MCP tool functions must return its engine's 'not installed'
message when the backing package (sentinel / seraph / morpheus_mcp) cannot
be imported. No exceptions may escape.
"""

from __future__ import annotations

import asyncio
from unittest.mock import patch


SENTINEL_MODULES = [
    "sentinel",
    "sentinel.core",
    "sentinel.core.knowledge",
    "sentinel.mcp",
    "sentinel.mcp.formatters",
]

SERAPH_MODULES = [
    "seraph",
    "seraph.config",
    "seraph.core",
    "seraph.core.checks",
    "seraph.core.gate",
    "seraph.mcp",
    "seraph.mcp.formatters",
]

MORPHEUS_MODULES = [
    "morpheus_mcp",
    "morpheus_mcp.config",
    "morpheus_mcp.core",
    "morpheus_mcp.core.engine",
    "morpheus_mcp.core.parser",
    "morpheus_mcp.core.store",
    "morpheus_mcp.mcp",
    "morpheus_mcp.mcp.formatters",
    "morpheus_mcp.models",
    "morpheus_mcp.models.enums",
]


def _block(modules):
    return patch.dict("sys.modules", {m: None for m in modules})


def _run(coro):
    return asyncio.run(coro)


# --- Context engine (Sentinel) -----------------------------------------------


class TestContextDegraded:
    def test_get_project_context(self):
        from plumbline.context.engine import get_project_context

        with _block(SENTINEL_MODULES):
            result = _run(get_project_context())
        assert "Context engine is not installed" in result

    def test_search_knowledge(self):
        from plumbline.context.engine import search_knowledge

        with _block(SENTINEL_MODULES):
            result = _run(search_knowledge("foo"))
        assert "Context engine is not installed" in result

    def test_get_co_changes(self):
        from plumbline.context.engine import get_co_changes

        with _block(SENTINEL_MODULES):
            result = _run(get_co_changes("auth.py"))
        assert "Context engine is not installed" in result


# --- Verify engine (Seraph) --------------------------------------------------


class TestVerifyDegraded:
    def test_run_gate(self):
        from plumbline.verify.engine import run_gate

        with _block(SERAPH_MODULES):
            result = _run(run_gate())
        assert "Verify engine is not installed" in result

    def test_explain_finding(self):
        from plumbline.verify.engine import explain_finding

        with _block(SERAPH_MODULES):
            result = _run(explain_finding("finding-id"))
        assert "Verify engine is not installed" in result


# --- Gate engine (Morpheus) --------------------------------------------------


class TestGateDegraded:
    def test_init_plan(self):
        from plumbline.gate.engine import init_plan

        with _block(MORPHEUS_MODULES):
            result = _run(init_plan("/nonexistent/plan.md"))
        assert "Gate engine is not installed" in result

    def test_advance_task(self):
        from plumbline.gate.engine import advance_task

        with _block(MORPHEUS_MODULES):
            result = _run(advance_task("task-1", "CHECK", {"foo": "bar"}))
        assert "Gate engine is not installed" in result

    def test_get_status(self):
        from plumbline.gate.engine import get_status

        with _block(MORPHEUS_MODULES):
            result = _run(get_status())
        assert "Gate engine is not installed" in result


# --- Sentinel directory discovery --------------------------------------------


def test_find_sentinel_dir_returns_none_when_no_sentinel(tmp_path):
    from plumbline.context.engine import _find_sentinel_dir

    result = _find_sentinel_dir(str(tmp_path))
    assert result is None
