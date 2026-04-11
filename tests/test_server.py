"""Smoke tests for the Plumbline MCP server."""

from __future__ import annotations

from plumbline.mcp.server import mcp


def test_server_has_nine_tools() -> None:
    """The unified surface exposes exactly 9 tools."""
    tools = mcp._tool_manager._tools  # noqa: SLF001
    assert len(tools) == 9, f"Expected 9 tools, got {len(tools)}: {list(tools.keys())}"


def test_all_tools_have_plumbline_prefix() -> None:
    """Every tool name starts with plumbline_."""
    tools = mcp._tool_manager._tools  # noqa: SLF001
    for name in tools:
        assert name.startswith("plumbline_"), f"Tool {name!r} missing plumbline_ prefix"


def test_tool_names() -> None:
    """Verify the exact tool surface."""
    tools = mcp._tool_manager._tools  # noqa: SLF001
    expected = {
        "plumbline_context",
        "plumbline_query",
        "plumbline_co_changes",
        "plumbline_check",
        "plumbline_verify",
        "plumbline_explain",
        "plumbline_init",
        "plumbline_advance",
        "plumbline_status",
    }
    assert set(tools.keys()) == expected
