"""Context engine — wraps Sentinel's project intelligence.

Calls Sentinel's core layer directly (KnowledgeStore + formatters),
not the MCP tool closures. Same code path, no MCP overhead.
"""

from __future__ import annotations

from pathlib import Path


def _open_store(project_root: str = ""):  # type: ignore[return]
    """Open a Sentinel KnowledgeStore, or return None."""
    try:
        from sentinel.core.knowledge import KnowledgeStore
    except ImportError:
        return None

    sentinel_dir = _find_sentinel_dir(project_root)
    if sentinel_dir is None:
        return None
    db_path = sentinel_dir / "sentinel.db"
    if not db_path.is_file():
        return None
    return KnowledgeStore(db_path)


def _find_sentinel_dir(project_root: str = "") -> Path | None:
    """Walk up from project_root (or cwd) looking for .sentinel/."""
    start = Path(project_root) if project_root else Path.cwd()
    current = start.resolve()
    for _ in range(20):
        candidate = current / ".sentinel"
        if candidate.is_dir():
            return candidate
        if current.parent == current:
            break
        current = current.parent
    return None


_NOT_INSTALLED = (
    "Plumbline Context engine is not installed. "
    "Run: pip install plumbline-ai[context]"
)

_NO_SENTINEL = (
    "No `.sentinel/` directory found in this project. "
    "Run `sentinel init` in your project root first, then try again."
)


async def get_project_context(project_root: str = "") -> str:
    """Full project intelligence summary."""
    try:
        from sentinel.mcp.formatters import format_project_context
    except ImportError:
        return _NOT_INSTALLED

    store = _open_store(project_root)
    if store is None:
        return _NO_SENTINEL
    with store:
        return format_project_context(store)


async def search_knowledge(query: str, limit: int = 20, project_root: str = "") -> str:
    """Free-text search across project knowledge."""
    try:
        from sentinel.mcp.formatters import format_query_results
    except ImportError:
        return _NOT_INSTALLED

    store = _open_store(project_root)
    if store is None:
        return _NO_SENTINEL
    with store:
        results = store.search(query, limit=limit, offset=0)
        return format_query_results(results, query, total=None, offset=0)


async def get_co_changes(file_path: str, limit: int = 50, project_root: str = "") -> str:
    """Find files that change together."""
    try:
        from sentinel.mcp.formatters import format_co_changes
    except ImportError:
        return _NOT_INSTALLED

    store = _open_store(project_root)
    if store is None:
        return _NO_SENTINEL
    with store:
        co_changes = store.get_co_changes(file_path, limit=limit)
        return format_co_changes(file_path, co_changes)
