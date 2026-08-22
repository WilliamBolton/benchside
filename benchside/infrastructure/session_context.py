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

from benchside.config import Paths
from benchside.domain.shared.model.ids import ProjectId


def _session_file(paths: Paths, project_id: ProjectId):
    return paths.home / "projects" / project_id.root / "current-session"


def register_session(paths: Paths, project_id: ProjectId, session_id: str) -> None:
    path = _session_file(paths, project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"session_id": session_id}), encoding="utf-8")


def clear_session(paths: Paths, project_id: ProjectId, session_id: str) -> None:
    """Remove the registration, but only if it is still ours — a newer
    session on the same project must not be clobbered by our exit."""
    path = _session_file(paths, project_id)
    try:
        if json.loads(path.read_text(encoding="utf-8")).get("session_id") == session_id:
            path.unlink(missing_ok=True)
    except (OSError, json.JSONDecodeError):
        pass


def current_session(paths: Paths, project_id: ProjectId) -> str | None:
    env = os.environ.get("CLAUDE_SESSION_ID")
    if env:
        return env
    path = _session_file(paths, project_id)
    try:
        return json.loads(path.read_text(encoding="utf-8")).get("session_id")
    except (OSError, json.JSONDecodeError):
        return None
