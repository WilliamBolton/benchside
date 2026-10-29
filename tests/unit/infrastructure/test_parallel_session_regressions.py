"""Parallel Claude sessions must never acquire one another's identity or sitting."""
import pytest

from benchside.cli import runtime
from benchside.domain.shared.error import InvalidStateError
from benchside.domain.shared.model.ids import ProjectId
from benchside.infrastructure.session_context import current_session, register_session

PID = ProjectId("synthetic")


def test_parallel_registrations_refuse_ambiguous_fallback(paths, monkeypatch):
    for name in ("CLAUDE_SESSION_ID", "BENCHSIDE_SESSION_ID", "CLAUDE_ENV_FILE"):
        monkeypatch.delenv(name, raising=False)
    register_session(paths, PID, "session-a")
    register_session(paths, PID, "session-b")
    with pytest.raises(InvalidStateError, match="Several"):
        current_session(paths, PID)


def test_each_hook_exports_its_own_identity(paths, monkeypatch, tmp_path):
    for name in ("CLAUDE_SESSION_ID", "BENCHSIDE_SESSION_ID"):
        monkeypatch.delenv(name, raising=False)
    first = tmp_path / "first.env"
    second = tmp_path / "second.env"
    monkeypatch.setenv("CLAUDE_ENV_FILE", str(first))
    register_session(paths, PID, "session-a")
    monkeypatch.setenv("CLAUDE_ENV_FILE", str(second))
    register_session(paths, PID, "session-b")
    assert "export CLAUDE_SESSION_ID=session-a" in first.read_text()
    assert "session-b" not in first.read_text()
    assert "export CLAUDE_SESSION_ID=session-b" in second.read_text()
    monkeypatch.setenv("CLAUDE_SESSION_ID", "session-a")
    assert current_session(paths, PID) == "session-a"


def test_identified_session_does_not_adopt_only_other_session_pointer(paths, monkeypatch):
    monkeypatch.delenv("BENCHSIDE_SESSION_ID", raising=False)
    monkeypatch.delenv("BENCH_SITTING", raising=False)
    monkeypatch.setenv("CLAUDE_SESSION_ID", "session-b")
    runtime.write_pointer(paths, sitting_id="sitting-b", project_id=PID, persona_id="pi")
    monkeypatch.setenv("CLAUDE_SESSION_ID", "session-a")
    assert runtime.read_pointer(paths, PID) is None
