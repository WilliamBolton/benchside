import hashlib
import io
import json
from urllib.error import HTTPError

import pytest

from benchside.domain.shared.error import BenchsideError
from benchside.infrastructure.http_sink import HttpExportSink

PAYLOAD = '{"schema":"benchside.gaps.v1","observations":[{"id":"o1","gap":{"kind":"missing_index","question":"🧬"}}]}'


class Response(io.BytesIO):
    status = 201


class Opener:
    def __init__(self, *, status=201, overrides=None):
        self.status = status
        self.overrides = overrides or {}
        self.requests = []

    def open(self, request, timeout):
        self.requests.append(request)
        assert timeout == 10
        data = {
            "status": "stored" if self.status == 201 else "duplicate",
            "sha256": hashlib.sha256(request.data).hexdigest(),
            "received_at": "2026-10-21T10:00:00Z",
            "observations": 1,
            **self.overrides,
        }
        response = Response(json.dumps(data).encode())
        response.status = self.status
        return response


@pytest.mark.parametrize("status", [200, 201])
def test_exact_bytes_and_verified_receipt(status):
    opener = Opener(status=status)
    sink = HttpExportSink("https://collector.example/v1/gaps", opener=opener)
    receipt = sink.send(PAYLOAD)
    assert opener.requests[0].data == PAYLOAD.encode("utf-8")
    assert receipt.sha256 == hashlib.sha256(PAYLOAD.encode("utf-8")).hexdigest()
    assert opener.requests[0].get_method() == "POST"


@pytest.mark.parametrize(
    "overrides",
    [
        {"sha256": "wrong"},
        {"observations": 2},
        {"observations": True},
        {"received_at": "yesterday"},
        {"received_at": "2026-10-21T10:00:00"},
        {"status": "ok"},
        {"unexpected": "metadata"},
    ],
)
def test_unverifiable_receipt_is_a_failure(overrides):
    with pytest.raises(BenchsideError, match="receipt"):
        HttpExportSink(
            "https://collector.example/v1/gaps", opener=Opener(overrides=overrides)
        ).send(PAYLOAD)


@pytest.mark.parametrize("status", [302, 400, 413, 422, 429, 503])
def test_http_errors_do_not_get_treated_as_success(status):
    class Failing:
        def open(self, *args, **kwargs):
            raise HTTPError("https://collector.example", status, "failure", {}, None)

    with pytest.raises(BenchsideError):
        HttpExportSink("https://collector.example/v1/gaps", opener=Failing()).send(PAYLOAD)


@pytest.mark.parametrize(
    "url",
    [
        "http://collector.example",
        "https://user:secret@collector.example",
        "https://collector.example/?key=secret",
        "file:///tmp/output",
    ],
)
def test_insecure_or_credentialled_destinations_rejected(url):
    with pytest.raises(BenchsideError):
        HttpExportSink(url)
