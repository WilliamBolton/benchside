"""One review flow over three independently consented, separately stored channels."""

import json
import os
import uuid
from pathlib import Path
from typing import Literal

from pydantic import Field

from benchside import __version__
from benchside.config import Paths
from benchside.domain.export.event.reporting import ReportSubmitted
from benchside.domain.export.model.reporting import (
    Demographics,
    Feedback,
    ResearchProfile,
    StrictValue,
)
from benchside.domain.export.model.value import ExportPreview
from benchside.domain.export.service.consent import ConsentService
from benchside.domain.export.service.export import ExportService
from benchside.domain.export.service.reporting import ReportingService, week_start
from benchside.domain.shared.error import (
    BenchsideError,
    ConsentRequiredError,
    NotFoundError,
    ValidationError,
)
from benchside.domain.shared.model.ids import CONSENT_LEDGER_PROJECT
from benchside.infrastructure.files import atomic_json
from benchside.infrastructure.http_sink import COLLECTOR, HttpExportSink
from benchside.infrastructure.journal.projection import (
    JournalConsentRepository,
    JournalObservationReader,
)
from benchside.infrastructure.journal.store import JsonlJournal
from benchside.infrastructure.placeholders import RefusingExportSink
from benchside.infrastructure.redaction import TextRedactor


class SubmissionDraft(StrictValue):
    id: str = Field(pattern=r"^[a-f0-9]{32}$")
    channel: Literal["gaps", "feedback", "usage"]
    preview: ExportPreview
    demographics_revision: int | None = None


class ParticipationChoice(StrictValue):
    response: Literal["unasked", "declined", "deferred", "configured"] = "unasked"


class SharingFlow:
    """Call under the installation transaction lock (CLI and app adapter do so)."""

    def __init__(self, paths: Paths, *, sinks=None):
        self.paths = paths
        self.journal = JsonlJournal(paths)
        self.reporting = ReportingService(journal=self.journal)
        self.ledger = JournalConsentRepository(self.journal)
        self.consent = ConsentService(repository=self.ledger, journal=self.journal)
        self.redactor = TextRedactor()
        self.sinks = sinks or {
            channel: self._sink(channel) for channel in ("gaps", "feedback", "usage")
        }
        self.export = ExportService(
            observations=JournalObservationReader(self.journal),
            consent=self.consent,
            redactor=self.redactor,
            sink=self.sinks["gaps"],
            ledger=self.ledger,
            journal=self.journal,
        )

    @staticmethod
    def _sink(channel):
        endpoint = os.environ.get(
            f"BENCHSIDE_{channel.upper()}_ENDPOINT", f"{COLLECTOR}/v1/{channel}"
        )
        return HttpExportSink(endpoint) if endpoint else RefusingExportSink()

    def profile(self):
        path = self.paths.home / "reporting/profile.json"
        return (
            ResearchProfile.model_validate_json(path.read_text())
            if path.exists()
            else ResearchProfile()
        )

    def participation(self):
        path = self.paths.home / "reporting/participation.json"
        return (
            ParticipationChoice.model_validate_json(path.read_text())
            if path.exists()
            else ParticipationChoice()
        )

    def set_participation(self, response):
        choice = ParticipationChoice(response=response)
        if choice.response == "unasked":
            raise ValidationError("Record a choice; do not reset an answered invitation")
        if choice.response in {"declined", "deferred"}:
            from benchside.domain.export.model.metascience import MetaState

            meta_path = self.paths.home / "metascience/state.json"
            grants = (
                MetaState.model_validate_json(meta_path.read_text()).grants
                if meta_path.exists()
                else {}
            )
            if any(
                self.status()[channel]["enabled"] for channel in ("gaps", "feedback", "usage")
            ) or any(key in grants for key in ("invitations", "analysis", "sharing")):
                raise ValidationError(
                    "Turn off active participation choices before declining or deferring"
                )
        atomic_json(
            self.paths.home / "reporting/participation.json", choice.model_dump(mode="json")
        )
        return choice.model_dump(mode="json")

    def set_profile(self, demographics, include_in_usage):
        previous = self.profile()
        profile = ResearchProfile(
            demographics=Demographics.model_validate(demographics),
            include_in_usage=include_in_usage,
            revision=previous.revision + 1,
        )
        atomic_json(self.paths.home / "reporting/profile.json", profile.model_dump(mode="json"))
        return profile.model_dump(mode="json")

    def status(self):
        grant = self.consent.active_grant()
        installation = self.paths.home / "reporting" / "installation.json"
        return {
            "gaps": {"enabled": bool(grant), "kinds": sorted(grant.gap_kinds) if grant else []},
            "feedback": {"enabled": bool(self.reporting.active_grant("feedback"))},
            "usage": {"enabled": bool(self.reporting.active_grant("usage"))},
            "installation_id": json.loads(installation.read_text())["id"]
            if installation.exists()
            else None,
        }

    def set_consent(self, channel, enabled, *, kinds=None):
        if channel == "gaps":
            active = self.consent.active_grant()
            if not enabled:
                if active:
                    self.consent.revoke()
                return
            selected = frozenset(kinds or ())
            if active and active.gap_kinds == selected:
                return
            # Validate before revoking an existing grant.
            from benchside.domain.shared.model.gap import GAP_KINDS

            if not selected or not selected <= GAP_KINDS:
                raise ValidationError("Choose one or more valid workflow observation kinds")
            if active:
                self.consent.revoke()
            self.consent.grant(grant_id=f"g-{uuid.uuid4().hex}", gap_kinds=selected)
        elif channel in {"feedback", "usage"}:
            self.reporting.set_consent(channel, enabled)
        else:
            raise ValidationError("Unknown sharing channel")

    def feedback(self, **values):
        return self.reporting.record_feedback(Feedback(id=uuid.uuid4().hex, **values))

    def prepare(self, channel, *, only=None, edits=None, feedback_id=None, comment=None, week=None):
        if channel == "gaps":
            previews = self.export.previews(only=only, edits=edits)
        else:
            if channel not in {"feedback", "usage"}:
                raise ValidationError("Unknown sharing channel")
            grant = self.reporting.active_grant(channel)
            if not grant:
                raise ConsentRequiredError(
                    f"{channel.title()} reporting is off; nothing was shared"
                )
            if channel == "feedback":
                payload = self.reporting.feedback_payload(feedback_id, __version__)
                if comment is not None:
                    from benchside.domain.export.model.reporting import FeedbackPayload

                    data = json.loads(payload)
                    data["feedback"]["comment"] = comment
                    payload = FeedbackPayload.model_validate(data).model_dump_json(by_alias=True)
            else:
                payload = self._usage(week or week_start())
            payload = self.redactor.apply(payload)
            previews = (
                ExportPreview(
                    payload=payload,
                    observation_ids=(),
                    grant_id=grant,
                    payload_sha256=ExportService._digest(payload),
                    destination=self.sinks[channel].destination,
                    redaction_findings=tuple(
                        f"{f.tier}:{f.category} in {f.field}" for f in self.redactor.scan(payload)
                    ),
                ),
            )
        drafts = []
        for preview in previews:
            draft = SubmissionDraft(
                id=uuid.uuid4().hex,
                channel=channel,
                preview=preview,
                demographics_revision=self.profile().revision if channel == "usage" else None,
            )
            atomic_json(self._draft_path(draft.id), draft.model_dump(mode="json"))
            drafts.append(draft)
        return drafts

    def _usage(self, week):
        directory = self.paths.home / "reporting"
        identity_path = directory / "installation.json"
        if identity_path.exists():
            identity = json.loads(identity_path.read_text())["id"]
        else:
            identity = uuid.uuid4().hex
            atomic_json(identity_path, {"id": identity})
        # Validate the week before using it as a filename.
        from datetime import date

        parsed_week = date.fromisoformat(week)
        if parsed_week.isoformat() != week or parsed_week.weekday() != 0:
            raise ValidationError("Choose a Monday in YYYY-MM-DD form")
        path = directory / f"usage-{week}.json"
        previous = json.loads(path.read_text()) if path.exists() else None
        payload = self.reporting.usage_payload(
            installation_id=identity,
            report_id=previous["report_id"] if previous else uuid.uuid4().hex,
            week=week,
            revision=previous["revision"] if previous else 1,
            version=__version__,
        ).model_dump(mode="json", by_alias=True, exclude_none=True)
        profile = self.profile()
        demographics = profile.demographics.model_dump(mode="json", exclude_none=True)
        if profile.include_in_usage and demographics:
            payload["demographics"] = demographics
        if previous and payload != previous:
            payload["revision"] += 1
        atomic_json(path, payload)
        return json.dumps(payload, ensure_ascii=False, indent=2)

    def _draft_path(self, identifier: str) -> Path:
        import re

        if not re.fullmatch(r"[a-f0-9]{32}", identifier):
            raise ValidationError("Invalid draft identifier")
        return self.paths.home / "sharing" / "drafts" / f"{identifier}.json"

    def load(self, identifier):
        path = self._draft_path(identifier)
        if not path.exists():
            raise NotFoundError("Submission draft was not found; prepare a preview first")
        return SubmissionDraft.model_validate_json(path.read_text())

    def send(self, identifier, approved_sha256):
        draft = self.load(identifier)
        try:
            if draft.channel == "gaps":
                return self.export.export(
                    preview=draft.preview,
                    approved_sha256=approved_sha256,
                )
            if draft.channel == "usage":
                # Never send an old week revision after a newer local snapshot.
                from benchside.domain.export.model.reporting import UsagePayload

                data = UsagePayload.model_validate_json(draft.preview.payload).model_dump()
                if (draft.demographics_revision or 0) != self.profile().revision:
                    raise ValidationError(
                        "Demographic preferences changed; review a new usage preview"
                    )
                current = self.paths.home / "reporting" / f"usage-{data['week']}.json"
                if (
                    current.exists()
                    and json.loads(current.read_text())["revision"] > data["revision"]
                ):
                    raise ValidationError("A newer usage snapshot exists; review that version")
            return self.reporting.send(
                channel=draft.channel,
                preview=draft.preview,
                approved_sha256=approved_sha256,
                sink=self.sinks[draft.channel],
                redactor=self.redactor,
            )
        except Exception as err:
            try:
                self.reporting.failure(getattr(err, "code", "submission_invalid"))
            except (BenchsideError, OSError):
                pass  # Preserve the original failure even if its counter cannot be saved.
            raise

    def history(self):
        entries = [
            {"channel": "gaps", **r.model_dump(mode="json")} for r in self.ledger.load().exports
        ]
        entries += [
            e.model_dump(mode="json")
            for e in self.journal.read(CONSENT_LEDGER_PROJECT)
            if isinstance(e, ReportSubmitted)
        ]
        return entries
