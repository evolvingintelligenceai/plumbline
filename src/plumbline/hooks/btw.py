"""The /btw spotter — PreToolUse hook that injects context before writes.

This hook fires before Write/Edit tool calls. It doesn't ask the agent to
reach for help — it puts help where the agent is already looking.

Three levels:
  - INFORM:    Inject co-changes, conventions. Agent sees it, may use it.
  - CHALLENGE: Force agent to articulate intent before writing.
  - GATE:      Block the write until plumbline_check passes (delegates to Seraph Tier 1).

v1 ships INFORM only. CHALLENGE and GATE levels require testing to tune
signal-to-noise ratio.

Output schema follows the current Claude Code PreToolUse hook contract:
  {"hookSpecificOutput": {"hookEventName": "PreToolUse", "additionalContext": "..."}}

When there's nothing to inject, emit an empty object so the hook is a no-op.
"""

from __future__ import annotations

import json
import sys


_EMPTY: dict = {}


def handle_pre_tool_use(event: dict) -> dict:
    """Process a PreToolUse hook event.

    For Write/Edit tool calls with a resolvable file_path, queries Plumbline
    Context for co-changes and returns them as `additionalContext`. For every
    other event, returns an empty object (no-op).
    """
    if event.get("tool_name") not in ("Write", "Edit"):
        return _EMPTY

    file_path = event.get("tool_input", {}).get("file_path", "")
    if not file_path:
        return _EMPTY

    project_root = event.get("cwd", "") or ""
    briefing = _build_briefing(file_path, project_root=project_root)

    if not briefing:
        return _EMPTY

    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": briefing,
        }
    }


def _build_briefing(file_path: str, project_root: str = "") -> str:
    """Build a /btw briefing for the given file.

    v1: co-changes only (fast, proven 67% hit rate in dogfood).
    Future: conventions, recent pitfalls, security notes.
    """
    from plumbline.context.engine import _open_store

    store = _open_store(project_root)
    if store is None:
        return ""

    try:
        with store:
            co_changes = store.get_co_changes(file_path, limit=5)
    except Exception:
        return ""

    if not co_changes:
        return ""

    partners = [
        c.file_b if c.file_a == file_path else c.file_a
        for c in co_changes
    ]
    lines = [f"/btw — {file_path} usually changes with:"]
    for p in partners:
        lines.append(f"  - {p}")
    lines.append("Did you read these before editing?")

    return "\n".join(lines)


def main() -> None:
    """Entry point when invoked as a Claude Code hook."""
    event = json.loads(sys.stdin.read())
    result = handle_pre_tool_use(event)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
