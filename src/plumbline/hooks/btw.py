"""The /btw spotter — PreToolUse hook that injects context before writes.

This hook fires before Write/Edit tool calls. It doesn't ask the agent to
reach for help — it puts help where the agent is already looking.

Three levels:
  - INFORM:    Inject co-changes, conventions. Agent sees it, may use it.
  - CHALLENGE: Force agent to articulate intent before writing.
  - GATE:      Block the write until plumbline_check passes (delegates to Seraph Tier 1).

v1 ships INFORM only. CHALLENGE and GATE levels require testing to tune
signal-to-noise ratio.
"""

from __future__ import annotations

import json
import sys


def handle_pre_tool_use(event: dict) -> dict:
    """Process a PreToolUse hook event.

    Reads the tool name and input from the event. If the tool is Write or Edit,
    queries Plumbline Context for relevant intelligence about the target file
    and returns it as injected context.

    Returns a dict with:
      - "result": "allow" (always, in v1 — INFORM level doesn't block)
      - "context": str with /btw briefing, or empty if nothing relevant
    """
    tool_name = event.get("tool_name", "")

    if tool_name not in ("Write", "Edit"):
        return {"result": "allow"}

    tool_input = event.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        return {"result": "allow"}

    briefing = _build_briefing(file_path)

    if not briefing:
        return {"result": "allow"}

    return {"result": "allow", "context": briefing}


def _build_briefing(file_path: str) -> str:
    """Build a /btw briefing for the given file.

    v1: co-changes only (fast, proven 67% hit rate in dogfood).
    Future: conventions, recent pitfalls, security notes.
    """
    try:
        from sentinel.core.knowledge import KnowledgeStore

        store = KnowledgeStore()
        co_changes = store.get_co_changes(file_path, limit=5)

        if not co_changes:
            return ""

        partners = [c.partner_path for c in co_changes]
        lines = [f"/btw — {file_path} usually changes with:"]
        for p in partners:
            lines.append(f"  - {p}")
        lines.append("Did you read these before editing?")

        return "\n".join(lines)

    except (ImportError, Exception):
        return ""


def main() -> None:
    """Entry point when invoked as a Claude Code hook."""
    event = json.loads(sys.stdin.read())
    result = handle_pre_tool_use(event)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
