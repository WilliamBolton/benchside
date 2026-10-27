"""Which Claude session is this?

Claude Code does not export the session id to Bash subprocesses, so `bench`
cannot see it directly. The SessionStart hook — which does receive it —
registers it in a per-project file; everything bench writes is stamped from
there. CLAUDE_SESSION_ID still wins when set (tests, scripted use).

The registered id is also what links a journal entry to its conversation:
the archived transcript is `transcripts/<stamp>-<session_id>.jsonl`, and the
same id names Claude Code's own record in ~/.claude/projects/.
"""

import json
import os
import re
import shlex
from pathlib import Path

from benchside.config import Paths
from benchside.domain.shared.error import InvalidStateError
from benchside.domain.shared.model.ids import ProjectId
from benchside.infrastructure.files import atomic_json, file_lock


def validate_session_id(value: str) -> str:
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,127}", value):
        raise InvalidStateError("Invalid session identifier")
    return value


def _session_file(paths: Paths, project_id: ProjectId):
    return paths.home / "projects" / project_id.root / "current-session"


def register_session(paths: Paths, project_id: ProjectId, session_id: str) -> None:
    validate_session_id(session_id)
    path = _session_file(paths, project_id)
    with file_lock(path.with_suffix(".lock")):
        sessions = _registered(path)
        sessions.add(session_id)
        atomic_json(path, {"sessions": sorted(sessions)})
    # Each Claude session has its own environment file. This avoids the
    # last-started-session race of a shared per-project current-session file.
    env_file = os.environ.get("CLAUDE_ENV_FILE")
    if env_file:
        with Path(env_file).open("a", encoding="utf-8") as handle:
            handle.write(f"\nexport CLAUDE_SESSION_ID={shlex.quote(session_id)}\n")


def clear_session(paths: Paths, project_id: ProjectId, session_id: str) -> None:
    """Remove the registration, but only if it is still ours — a newer
    session on the same project must not be clobbered by our exit."""
    path = _session_file(paths, project_id)
    with file_lock(path.with_suffix(".lock")):
        sessions = _registered(path) - {session_id}
        if sessions:
            atomic_json(path, {"sessions": sorted(sessions)})
        else:
            path.unlink(missing_ok=True)


def current_session(paths: Paths, project_id: ProjectId) -> str | None:
    env = os.environ.get("BENCHSIDE_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
    if env:
        return validate_session_id(env)
    path = _session_file(paths, project_id)
    sessions = _registered(path)
    if len(sessions) > 1:
        raise InvalidStateError(
            "Several conversations are active; a session identifier is required to record safely",
            hint="Restart this conversation to load its session environment.",
        )
    return next(iter(sessions), None)


def _registered(path: Path) -> set[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return {validate_session_id(s) for s in data.get("sessions", [])} | (
            {validate_session_id(data["session_id"])} if data.get("session_id") else set()
        )
    except (OSError, json.JSONDecodeError):
        return set()
