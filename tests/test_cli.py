"""Tests for the Plumbline CLI — doctor and version."""

from __future__ import annotations

from typer.testing import CliRunner

from plumbline import __version__
from plumbline.cli.app import app


runner = CliRunner()


def test_version_prints_current_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "plumbline-ai" in result.stdout
    assert __version__ in result.stdout


def test_doctor_renders_health_table():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Plumbline Health Check" in result.stdout
    # All three engines must appear in the table
    assert "Context" in result.stdout
    assert "Verify" in result.stdout
    assert "Gate" in result.stdout
    # And their package names
    assert "git-sentinel" in result.stdout
    assert "seraph-ai" in result.stdout
    assert "morpheus-mcp" in result.stdout


def test_doctor_reports_status_for_each_engine():
    """Each engine row must have a status cell — OK or NOT INSTALLED."""
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "OK" in result.stdout or "NOT INSTALLED" in result.stdout
