"""Gate engine — wraps Morpheus's plan state and phase gate enforcement.

Calls Morpheus's core layer directly (engine + store + formatters).
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

_NOT_INSTALLED = (
    "Plumbline Gate engine is not installed. "
    "Run: pip install plumbline-ai[gate]"
)


def _get_config():  # type: ignore[return]
    """Load Morpheus config."""
    try:
        from morpheus_mcp.config import MorpheusConfig

        return MorpheusConfig.load()
    except ImportError:
        return None


async def init_plan(plan_file: str) -> str:
    """Load a plan file and begin tracking."""
    try:
        from morpheus_mcp.core.engine import check_oil_change_advisory, init_plan as _init
        from morpheus_mcp.core.parser import parse_plan_file
        from morpheus_mcp.core.store import MorpheusStore
        from morpheus_mcp.mcp.formatters import format_plan_summary
    except ImportError:
        return _NOT_INSTALLED

    config = _get_config()
    if config is None:
        return _NOT_INSTALLED

    try:
        plan, tasks = parse_plan_file(plan_file)
        with MorpheusStore(config.db_path) as store:
            _init(store, plan, tasks, oil_change_interval=config.gates.oil_change_interval)
            summary = format_plan_summary(plan, tasks)

            advisory = check_oil_change_advisory(
                store, plan.project, config.gates.oil_change_interval,
            )
            if advisory:
                summary = f"**OIL CHANGE:** {advisory}\n\n{summary}"

            return summary
    except (FileNotFoundError, ValueError, sqlite3.Error, OSError) as exc:
        return f"Gate engine error: {exc}"
    except Exception as exc:  # noqa: BLE001 — MCP boundary; must return text, not raise
        return f"Gate engine failed unexpectedly: {exc}"


async def advance_task(task_id: str, phase: str, evidence: dict[str, Any]) -> str:
    """Advance a task through a phase gate with evidence."""
    try:
        from morpheus_mcp.core.engine import _get_phase_order, advance
        from morpheus_mcp.core.store import MorpheusStore
        from morpheus_mcp.mcp.formatters import (
            format_advance_rejection,
            format_advance_success,
        )
        from morpheus_mcp.models.enums import Phase
    except ImportError:
        return _NOT_INSTALLED

    config = _get_config()
    if config is None:
        return _NOT_INSTALLED

    try:
        try:
            phase_enum = Phase(phase.upper())
        except ValueError:
            valid = ", ".join(p.value for p in Phase)
            return f"Error: Invalid phase '{phase}'. Valid phases: {valid}"

        evidence_dict = (
            evidence if isinstance(evidence, dict) else json.loads(str(evidence))
        )

        with MorpheusStore(config.db_path) as store:
            result, _phase_record = advance(
                store, task_id, phase_enum, evidence_dict,
                knowledge_gate_task_threshold=config.gates.knowledge_gate_task_threshold,
            )

            if not result.passed:
                return format_advance_rejection(phase_enum, result.message)

            task = store.get_task(task_id)
            if task is None:
                return f"Error: Task '{task_id}' not found after advance"

            active_phase_order = _get_phase_order(store, task.id)

            extra = ""
            if result.message and result.message != "Gate passed":
                extra = result.message

            return format_advance_success(
                phase_enum, task,
                phase_order=active_phase_order,
                extra_message=extra,
            )
    except json.JSONDecodeError as exc:
        return f"Error: Invalid evidence JSON: {exc}"
    except (FileNotFoundError, ValueError, sqlite3.Error, OSError) as exc:
        return f"Gate engine error: {exc}"
    except Exception as exc:  # noqa: BLE001 — MCP boundary; must return text, not raise
        return f"Gate engine failed unexpectedly: {exc}"


async def get_status(plan_id: str = "") -> str:
    """Get plan progress and current state."""
    try:
        from morpheus_mcp.core.store import MorpheusStore
        from morpheus_mcp.mcp.formatters import format_status
    except ImportError:
        return _NOT_INSTALLED

    config = _get_config()
    if config is None:
        return _NOT_INSTALLED

    try:
        with MorpheusStore(config.db_path) as store:
            if plan_id:
                plan = store.get_plan(plan_id)
            else:
                plans = store.list_plans()
                plan = plans[0] if plans else None

            if plan is None:
                return "No plans found. Use `plumbline_init` to load a plan."

            tasks = store.get_tasks(plan.id)
            phases_by_task = {t.id: store.get_phases(t.id) for t in tasks}
            active = [t for t in tasks if t.status.value == "in_progress"]
            progress_by_task = {t.id: store.get_progress(t.id) for t in active}
            return format_status(plan, tasks, phases_by_task, progress_by_task)
    except (FileNotFoundError, ValueError, sqlite3.Error, OSError) as exc:
        return f"Gate engine error: {exc}"
    except Exception as exc:  # noqa: BLE001 — MCP boundary; must return text, not raise
        return f"Gate engine failed unexpectedly: {exc}"
