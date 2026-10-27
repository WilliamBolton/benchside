"""The existing collector's strict v1 contract, including UTF-16 text limits."""

import json
import re

from benchside.domain.shared.error import ValidationError

MAX_BYTES = 512 * 1024
MAX_OBSERVATIONS = 1000
GAP_FIELDS = {
    "missing_tool": {"task", "reached_for", "why_failed"},
    "unfindable_data": {"sought", "where_searched"},
    "manual_toil": {"task", "frequency"},
    "dead_end": {"approach", "cost"},
    "missing_index": {"question"},
}


def validate_gap(gap: dict) -> None:
    if (
        not isinstance(gap, dict)
        or not isinstance(gap.get("kind"), str)
        or gap["kind"] not in GAP_FIELDS
    ):
        raise ValidationError("Unknown workflow observation kind")
    if set(gap) != GAP_FIELDS[gap["kind"]] | {"kind"}:
        raise ValidationError("Workflow observations contain missing or unknown fields")
    for key, value in gap.items():
        if key == "where_searched":
            if not isinstance(value, list) or len(value) > 50:
                raise ValidationError("where_searched must have at most 50 entries")
            for item in value:
                _text(item, 500)
        else:
            _text(value, 2000)


def _text(value, maximum):
    if not isinstance(value, str) or len(value.encode("utf-16-le")) // 2 > maximum:
        raise ValidationError(f"Shared text must be a string of at most {maximum} characters")


def validate_payload(payload: str) -> dict:
    if len(payload.encode("utf-8")) > MAX_BYTES:
        raise ValidationError("Batch exceeds the collector's 512 KiB limit")
    try:
        data = json.loads(payload)
    except (TypeError, json.JSONDecodeError) as err:
        raise ValidationError("Invalid export JSON") from err
    if not isinstance(data, dict) or set(data) != {"schema", "observations"}:
        raise ValidationError("Invalid export fields")
    observations = data["observations"]
    if data["schema"] != "benchside.gaps.v1" or not isinstance(observations, list):
        raise ValidationError("Invalid export schema")
    if not 1 <= len(observations) <= MAX_OBSERVATIONS:
        raise ValidationError("An export needs 1–1000 observations")
    seen = set()
    for observation in observations:
        if not isinstance(observation, dict) or set(observation) != {"id", "gap"}:
            raise ValidationError("Invalid observation fields")
        identifier = observation["id"]
        if not isinstance(identifier, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", identifier
        ):
            raise ValidationError("Invalid observation identifier")
        if identifier in seen:
            raise ValidationError("Repeated observation identifier")
        seen.add(identifier)
        validate_gap(observation["gap"])
    return data
