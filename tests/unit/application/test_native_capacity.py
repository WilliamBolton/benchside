import base64
import copy
import hashlib
import json
import uuid
import zlib

import pytest

from benchside.application import native
from benchside.domain.export.model.value import DeliveryReceipt
from benchside.domain.shared.error import BenchsideError
from benchside.infrastructure.http_sink import HttpExportSink


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def refuse(*args, **kwargs):
        raise AssertionError("No real submissions in native capacity tests")

    monkeypatch.setattr(HttpExportSink, "send", refuse)


class Notebook:
    def __init__(self):
        self.document = native.run_native({"action": "native.create"})["markdown"]

    def run(self, command, *, project=None, operation_id=None):
        result = native.run_native(
            {
                "action": "native.run",
                "document": self.document,
                "workspace_id": native.unpack(self.document)[0]["workspace_id"],
                "operation_id": operation_id or uuid.uuid4().hex,
                "request": command,
                **({"project_document": project} if project else {}),
            }
        )
        self.document = result["markdown"]
        return result

    def setup(self, host="chatgpt"):
        return self.run(
            {"action": "setup", "host": host, "project_key": "synthetic-journal"},
            project={"document_id": "synthetic-journal", "title": "Synthetic"},
        )["result"]


def feedback_draft(book):
    book.run({"action": "sharing.consent", "channel": "feedback", "enabled": True})
    feedback = book.run(
        {
            "action": "sharing.feedback",
            "feedback": {"ease": 4, "would_use_again": "yes", "comment": "Synthetic"},
        }
    )["result"]
    return book.run(
        {"action": "sharing.preview", "channel": "feedback", "feedback_id": feedback["id"]}
    )["result"][0]


def fake_receipts(monkeypatch):
    submitted = []

    def send(self, payload):
        submitted.append(payload)
        return DeliveryReceipt(
            status="stored",
            sha256=hashlib.sha256(payload.encode()).hexdigest(),
            received_at="2026-10-28T12:00:00+00:00",
            observations=1,
        )

    monkeypatch.setattr(HttpExportSink, "send", send)
    return submitted


def test_response_cache_is_bounded_without_forgetting_committed_operations():
    book = Notebook()
    context = book.setup()
    context["sitting_id"] = book.run({"action": "start", "role": "methods-clinic", **context})[
        "result"
    ]["sitting"]["id"]
    receipts = []
    for index in range(12):
        operation_id = uuid.uuid4().hex
        command = {
            "action": "decide",
            "decision": f"Synthetic {index} " + "a" * 8000,
            "rationale": "Synthetic",
            **context,
        }
        result = book.run(command, operation_id=operation_id)
        assert result["ok"]
        receipts.append((operation_id, command, result["result"]["recorded"]))
    snapshot, body = native.unpack(book.document)
    cached_bytes = sum(
        len(native._json(operation["result"]).encode())
        for operation in body["operations"].values()
        if not operation.get("result_compacted")
    )
    assert cached_bytes <= native.MAX_REPLAY_CACHE_BYTES
    assert all(operation_id in body["operations"] for operation_id, _, _ in receipts)
    compacted = next(
        item for item in receipts if body["operations"][item[0]].get("result_compacted")
    )
    replay = book.run(compacted[1], operation_id=compacted[0])
    assert replay["replayed"] and replay["result_compacted"] and not replay["changed"]
    assert replay["snapshot"] == snapshot
    assert replay["result"]["recorded"] == compacted[2]
    with pytest.raises(BenchsideError, match="different request"):
        book.run({**compacted[1], "decision": "Changed"}, operation_id=compacted[0])
    journal = native.unpack(book.document)[1]["files"][
        f"projects/{context['project_id']}/journal.jsonl"
    ]
    assert (
        sum(json.loads(line)["type"] == "DecisionRecorded" for line in journal.splitlines()) == 12
    )


def test_capacity_preflight_refuses_before_post_and_preserves_approved_draft(monkeypatch):
    book = Notebook()
    draft = feedback_draft(book)
    submitted = fake_receipts(monkeypatch)
    snapshot, before = native.unpack(book.document)
    monkeypatch.setattr(
        native,
        "MAX_DOCUMENT_BYTES",
        len(native._json(snapshot).encode()) + native.DOCUMENT_CONTROL_RESERVE + 1024,
    )
    result = book.run(
        {
            "action": "sharing.send",
            "draft_id": draft["id"],
            "approved_sha256": draft["preview"]["payload_sha256"],
        }
    )
    assert not result["ok"] and result["code"] == "native_capacity"
    assert submitted == []
    assert native.unpack(book.document)[1] == before


def test_submission_with_headroom_still_saves_its_receipt(monkeypatch):
    book = Notebook()
    draft = feedback_draft(book)
    submitted = fake_receipts(monkeypatch)
    result = book.run(
        {
            "action": "sharing.send",
            "draft_id": draft["id"],
            "approved_sha256": draft["preview"]["payload_sha256"],
        }
    )
    assert result["ok"] and result["changed"]
    assert submitted == [draft["preview"]["payload"]]
    history = book.run({"action": "sharing.history"})["result"]
    assert len(history) == 1 and history[0]["payload_sha256"] == draft["preview"]["payload_sha256"]


def test_unexpected_post_delivery_capacity_failure_returns_the_receipt(monkeypatch):
    book = Notebook()
    draft = feedback_draft(book)
    original = native.unpack(book.document)[1]
    submitted = fake_receipts(monkeypatch)
    send = HttpExportSink.send

    def changed_limit(self, payload):
        receipt = send(self, payload)
        monkeypatch.setattr(native, "MAX_STATE_BYTES", len(native._json(original).encode()) + 1)
        return receipt

    monkeypatch.setattr(HttpExportSink, "send", changed_limit)
    result = book.run(
        {
            "action": "sharing.send",
            "draft_id": draft["id"],
            "approved_sha256": draft["preview"]["payload_sha256"],
        }
    )
    assert len(submitted) == 1
    assert not result["ok"] and result["delivery_confirmed"] and not result["changed"]
    assert result["result"]["payload_sha256"] == draft["preview"]["payload_sha256"]
    assert "receipt could not be saved" in result["error"]
    assert native.unpack(book.document)[1] == original


@pytest.mark.parametrize(
    "action,field,choice",
    [
        ("sharing.consent", "channel", "gaps"),
        ("sharing.consent", "channel", "feedback"),
        ("sharing.consent", "channel", "usage"),
        ("metascience.consent", "choice", "invitations"),
        ("metascience.consent", "choice", "analysis"),
        ("metascience.consent", "choice", "sharing"),
    ],
)
def test_reserved_capacity_allows_every_sharing_choice_to_be_withdrawn(
    monkeypatch, action, field, choice
):
    book = Notebook()
    grant = {"action": action, field: choice, "enabled": True}
    if choice == "gaps":
        grant["kinds"] = ["missing_index"]
    assert book.run(grant)["ok"]
    raw_size = len(native._json(native.unpack(book.document)[1]).encode())
    monkeypatch.setattr(native, "MAX_STATE_BYTES", raw_size + native.STATE_CONTROL_RESERVE - 1)
    refused = book.run(
        {
            "action": "sharing.feedback",
            "feedback": {"ease": 4, "would_use_again": "yes", "comment": "Synthetic"},
        }
    )
    assert not refused["ok"] and refused["code"] == "native_capacity"
    withdrawn = book.run({"action": action, field: choice, "enabled": False})
    assert withdrawn["ok"] and withdrawn["changed"]
    status = book.run(
        {"action": "sharing.status" if action == "sharing.consent" else "metascience.status"}
    )["result"]
    assert not (
        status[choice]["enabled"] if action == "sharing.consent" else status["choices"][choice]
    )


def test_emergency_withdrawal_preserves_science_receipts_and_replay_ids(monkeypatch):
    book = Notebook()
    context = book.setup()
    book.run({"action": "start", "role": "methods-clinic", **context})
    draft = feedback_draft(book)
    submitted = fake_receipts(monkeypatch)
    book.run(
        {
            "action": "sharing.send",
            "draft_id": draft["id"],
            "approved_sha256": draft["preview"]["payload_sha256"],
        }
    )
    book.run({"action": "sharing.consent", "channel": "usage", "enabled": True})
    pending = book.run({"action": "sharing.preview", "channel": "usage"})["result"][0]
    snapshot, body = native.unpack(book.document)
    native._compact_operations(body, all_results=True)
    book.document = native.markdown(
        native.pack(body, snapshot["workspace_id"], snapshot["revision"])
    )
    science = body["files"][f"projects/{context['project_id']}/journal.jsonl"]
    receipt = next(
        json.loads(line)
        for line in body["files"]["projects/consent-ledger/journal.jsonl"].splitlines()
        if json.loads(line)["type"] == "ReportSubmitted"
    )
    old_operations = copy.deepcopy(body["operations"])
    original_limit = native.MAX_STATE_BYTES
    monkeypatch.setattr(native, "MAX_STATE_BYTES", len(native._json(body).encode()) + 64)
    result = book.run({"action": "sharing.consent", "channel": "usage", "enabled": False})
    assert result["ok"] and result["control_history_compacted"]
    after = native.unpack(book.document)[1]
    assert after["files"][f"projects/{context['project_id']}/journal.jsonl"] == science
    assert receipt in [
        json.loads(line)
        for line in after["files"]["projects/consent-ledger/journal.jsonl"].splitlines()
    ]
    assert all(
        after["operations"][key]["request_sha256"] == value["request_sha256"]
        for key, value in old_operations.items()
    )
    assert not book.run({"action": "sharing.status"})["result"]["usage"]["enabled"]
    monkeypatch.setattr(native, "MAX_STATE_BYTES", original_limit)
    book.run({"action": "sharing.consent", "channel": "usage", "enabled": True})
    refused = book.run(
        {
            "action": "sharing.send",
            "draft_id": pending["id"],
            "approved_sha256": pending["preview"]["payload_sha256"],
        }
    )
    assert not refused["ok"] and "consent" in refused["error"].lower()
    assert len(submitted) == 1


def test_same_native_document_from_another_app_uses_existing_project():
    book = Notebook()
    first = book.setup("chatgpt")
    second = book.setup("claude")
    assert first["project_id"] == second["project_id"]
    assert first["session_id"] != second["session_id"]
    body = native.unpack(book.document)[1]
    assert len(body["projects"]) == 1
    assert (
        json.loads(body["files"][f"app-sessions/{second['session_id']}.json"])["host"] == "claude"
    )


@pytest.mark.parametrize("future", ["event", "field"])
def test_newer_record_types_require_an_update_without_discarding_data(future):
    book = Notebook()
    context = book.setup()
    book.run({"action": "start", "role": "methods-clinic", **context})
    snapshot, body = native.unpack(book.document)
    name = f"projects/{context['project_id']}/journal.jsonl"
    record = json.loads(body["files"][name])
    if future == "event":
        record["type"] = "FutureScientificRecord"
    else:
        record["data"]["future_context"] = {"preserve": "Synthetic future record"}
    body["files"][name] = json.dumps(record) + "\n"
    snapshot["payload"] = base64.b64encode(zlib.compress(native._json(body).encode())).decode()
    snapshot["sha256"] = native._digest(
        {key: value for key, value in snapshot.items() if key != "sha256"}
    )
    before = copy.deepcopy(snapshot)
    with pytest.raises(BenchsideError) as caught:
        native.unpack(snapshot)
    assert caught.value.code == "native_update_required"
    assert "Update the installed" in str(caught.value)
    assert snapshot == before
