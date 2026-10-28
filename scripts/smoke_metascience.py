"""Synthetic HTTP integration check; refuses every non-loopback destination.

Run against an isolated local Worker with the synthetic fixture catalog. Never
publish that catalog to staging/production just to run this development check.
"""

import argparse
import json
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

from benchside.application.metascience import Metascience, StudyClient
from benchside.config import Paths
from benchside.domain.shared.error import BenchsideError, InfrastructureError
from benchside.infrastructure.http_sink import HttpExportSink


def smoke(endpoint):
    url = urlsplit(endpoint)
    if (
        url.scheme != "http"
        or url.hostname not in {"localhost", "127.0.0.1", "::1"}
        or url.username
        or url.password
        or url.query
        or url.fragment
        or url.path not in {"", "/"}
    ):
        raise ValueError("This synthetic check only permits a local loopback Worker")
    endpoint = endpoint.rstrip("/")
    with tempfile.TemporaryDirectory(prefix="benchside-meta-review-") as temporary:
        root = Path(temporary)
        flow = Metascience(
            Paths(home=root / "private", repo_root=root),
            catalog=StudyClient(f"{endpoint}/v1/studies", allow_local=True),
            sinks={
                c: HttpExportSink(f"{endpoint}/v1/{c}", allow_local=True)
                for c in ("surveys", "activity")
            },
        )
        flow.consent("invitations", True)
        invitation = flow.invitations()["invitation"]
        assert invitation and invitation["id"] == "synthetic-verification", (
            "Use the isolated synthetic catalog"
        )
        survey = flow.survey("synthetic-verification@1", {"checked": "yes"})
        survey_receipt = flow.send(survey["id"], survey["sha256"])
        assert survey_receipt["status"] == "stored"
        assert flow.sinks["surveys"].send(survey["payload"]).status == "duplicate"
        flow.consent("analysis", True)
        scope = {"host": "claude", "source_id": "synthetic-project"}
        flow.scopes([scope])
        sample = flow.sample([{"scope": scope, "session_ref": f"synthetic-{i}"} for i in range(21)])
        assert len(sample["selected"]) == 20, "The automatic sample must respect the 20-session cap"
        for token in sample["selected"]:
            flow.record(
                sample["week"],
                token,
                {
                    "benchside_role": "none",
                    "activity": {"value": "analysis", "basis": "model_inferred"},
                    "obstacle": {"value": "unknown", "basis": "unknown"},
                    "verification": {"value": "none_visible", "basis": "model_inferred"},
                    "outcome": {"value": "not_reported", "basis": "unknown"},
                },
            )
        flow.consent("sharing", True)
        activity = flow.preview_activity(sample["week"])
        activity_receipt = flow.send(activity["id"], activity["sha256"])
        assert activity_receipt["status"] == "stored" and activity_receipt["observations"] == 20
        assert flow.sinks["activity"].send(activity["payload"]).status == "duplicate"
        invalid = json.loads(activity["payload"])
        invalid["transcript"] = "Synthetic forbidden field"
        try:
            flow.sinks["activity"].send(json.dumps(invalid))
        except InfrastructureError as error:
            assert error.code == "submission_rejected" and "422" in str(error)
        else:
            raise AssertionError("Collector accepted forbidden text")
        flow.consent("sharing", False)
        try:
            flow.send(activity["id"], activity["sha256"])
        except BenchsideError:
            pass
        else:
            raise AssertionError("Revocation did not block submission")
        assert not (flow.path.parent.parent / "reporting/installation.json").exists()
        print(
            json.dumps(
                {
                    "catalog": "synthetic invitation retrieved",
                    "surveys": "stored; duplicate retry verified",
                    "activity": "20 selected sessions stored; duplicate retry verified",
                    "forbidden_transcript": "HTTP 422",
                    "revoked_sharing": "blocked before HTTP",
                    "production_requests": 0,
                },
                indent=2,
            )
        )

        return {"surveys": survey["payload"], "activity": activity["payload"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", default="http://127.0.0.1:8880")
    smoke(parser.parse_args().endpoint)
