"""Tests for the /btw PreToolUse hook.

Covers three shapes:
  - Non-matching events (Bash, Read, empty, no file_path) → no-op `{}`
  - Matching events with no Sentinel data → no-op `{}`
  - Matching events with co-changes → hookSpecificOutput with additionalContext

Uses Sentinel's real CoChange dataclass (not MagicMock) so a field rename
in Sentinel will break this test, not hide behind a mock.
"""

from __future__ import annotations

from unittest.mock import patch

from sentinel.models.knowledge import CoChange

from plumbline.hooks.btw import handle_pre_tool_use


def _no_sentinel():
    return patch("plumbline.context.engine._open_store", return_value=None)


def _fake_store_with(co_changes: list[CoChange]):
    """Patch _open_store to return a minimal stand-in that supports the
    `with store:` context manager and `store.get_co_changes(...)`."""

    class _FakeStore:
        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def get_co_changes(self, file_path, limit=5):
            return co_changes

    return patch("plumbline.context.engine._open_store", return_value=_FakeStore())


class TestPassthrough:
    """Non-Write events and malformed events must be no-ops."""

    def test_bash_event_is_noop(self):
        assert handle_pre_tool_use({"tool_name": "Bash", "tool_input": {"command": "ls"}}) == {}

    def test_read_event_is_noop(self):
        assert handle_pre_tool_use({"tool_name": "Read", "tool_input": {"file_path": "/x"}}) == {}

    def test_empty_event_is_noop(self):
        assert handle_pre_tool_use({}) == {}

    def test_unknown_tool_is_noop(self):
        assert handle_pre_tool_use({"tool_name": "Grep"}) == {}


class TestWriteEventsWithoutSentinel:
    """Write/Edit events must still be no-ops when Sentinel is unavailable."""

    def test_write_noop_when_no_sentinel(self):
        with _no_sentinel():
            result = handle_pre_tool_use({
                "tool_name": "Write",
                "tool_input": {"file_path": "/tmp/foo.py"},
            })
        assert result == {}

    def test_edit_noop_when_no_sentinel(self):
        with _no_sentinel():
            result = handle_pre_tool_use({
                "tool_name": "Edit",
                "tool_input": {"file_path": "/tmp/foo.py"},
            })
        assert result == {}

    def test_write_without_file_path_is_noop(self):
        assert handle_pre_tool_use({
            "tool_name": "Write",
            "tool_input": {},
        }) == {}

    def test_write_with_empty_file_path_is_noop(self):
        assert handle_pre_tool_use({
            "tool_name": "Write",
            "tool_input": {"file_path": ""},
        }) == {}


class TestBriefingInjection:
    """When Sentinel returns co-changes, the hook emits the current
    PreToolUse hookSpecificOutput schema with additionalContext."""

    def test_schema_matches_claude_code_contract(self):
        co = CoChange(file_a="src/auth.py", file_b="tests/test_auth.py", change_count=7)
        with _fake_store_with([co]):
            result = handle_pre_tool_use({
                "tool_name": "Write",
                "tool_input": {"file_path": "src/auth.py"},
            })

        assert set(result.keys()) == {"hookSpecificOutput"}
        spec = result["hookSpecificOutput"]
        assert spec["hookEventName"] == "PreToolUse"
        assert "additionalContext" in spec
        assert "src/auth.py" in spec["additionalContext"]
        assert "tests/test_auth.py" in spec["additionalContext"]

    def test_partner_extraction_when_file_is_file_a(self):
        co = CoChange(file_a="src/auth.py", file_b="tests/test_auth.py", change_count=7)
        with _fake_store_with([co]):
            result = handle_pre_tool_use({
                "tool_name": "Write",
                "tool_input": {"file_path": "src/auth.py"},
            })
        assert "tests/test_auth.py" in result["hookSpecificOutput"]["additionalContext"]

    def test_partner_extraction_when_file_is_file_b(self):
        co = CoChange(file_a="tests/test_auth.py", file_b="src/auth.py", change_count=7)
        with _fake_store_with([co]):
            result = handle_pre_tool_use({
                "tool_name": "Write",
                "tool_input": {"file_path": "src/auth.py"},
            })
        assert "tests/test_auth.py" in result["hookSpecificOutput"]["additionalContext"]

    def test_empty_co_changes_returns_noop(self):
        with _fake_store_with([]):
            result = handle_pre_tool_use({
                "tool_name": "Write",
                "tool_input": {"file_path": "src/auth.py"},
            })
        assert result == {}


class TestCwdPropagation:
    """The hook must pass the event's cwd through to Sentinel project
    discovery, not silently fall back to process cwd."""

    def test_cwd_from_event_is_passed_to_open_store(self):
        co = CoChange(file_a="src/auth.py", file_b="tests/test_auth.py", change_count=3)

        class _FakeStore:
            def __enter__(self):
                return self

            def __exit__(self, *exc):
                return False

            def get_co_changes(self, file_path, limit=5):
                return [co]

        with patch(
            "plumbline.context.engine._open_store",
            return_value=_FakeStore(),
        ) as mocked:
            handle_pre_tool_use({
                "tool_name": "Write",
                "tool_input": {"file_path": "src/auth.py"},
                "cwd": "/some/project/root",
            })

        mocked.assert_called_once_with("/some/project/root")
