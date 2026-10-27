"""Opt-in studies and selected-session observation; no ambient chat access.

Call under App's transaction lock. Host tools discover only explicitly selected
scopes, then analyse sampled sessions in the host. This module never reads logs.
"""

import hashlib
import json
import os
import uuid
from datetime import UTC, date, datetime, timedelta
from urllib.error import URLError
from urllib.request import Request

from benchside import __version__
from benchside.application.submission_failures import record_submission_failure
from benchside.domain.export.model.metascience import (
    ActivityObservation,
    ActivityPayload,
    Candidate,
    Classification,
    MetaDraft,
    MetaState,
    Sample,
    Scope,
    StudyCatalog,
    SurveyPayload,
    canonical,
    digest,
)
from benchside.domain.shared.error import ConsentRequiredError, InfrastructureError, ValidationError
from benchside.infrastructure.files import atomic_json
from benchside.infrastructure.http_sink import COLLECTOR, HttpExportSink


class StudyClient:
    """Fixed trusted endpoint, bounded JSON, no redirects or participant parameters."""

    def __init__(self, endpoint=None, *, allow_local=False, opener=None):
        # Reuse the HTTPS and no-redirect boundary, never use a URL from a study.
        self.transport = HttpExportSink(
            endpoint or os.environ.get("BENCHSIDE_STUDIES_ENDPOINT", f"{COLLECTOR}/v1/studies"),
            allow_local=allow_local,
            opener=opener,
        )

    def fetch(self):
        try:
            request = Request(self.transport.destination, headers={"Accept": "application/json"})
            with self.transport._opener.open(request, timeout=10) as response:
                raw = response.read(131073)
                if response.status != 200 or len(raw) > 131072:
                    raise ValueError("Invalid catalog response")
            return StudyCatalog.model_validate_json(raw)
        except (URLError, OSError, ValueError) as err:
            if hasattr(err, "close"):
                err.close()
            raise InfrastructureError(
                "Study invitations are unavailable; continue research normally"
            ) from err


class Metascience:
    def __init__(self, paths, *, catalog=None, sinks=None, today=None):
        self.paths = paths
        self.path = paths.home / "metascience" / "state.json"
        self.state = (
            MetaState.model_validate_json(self.path.read_text())
            if self.path.exists()
            else MetaState(seed=uuid.uuid4().hex)
        )
        self.catalog = catalog
        self.sinks = sinks
        self.today = today or datetime.now(UTC).date()

    def _save(self, **updates):
        data = {**self.state.model_dump(), **updates}
        state = MetaState.model_validate(data)
        atomic_json(self.path, state.model_dump(mode="json"))
        self.state = state

    def _require(self, *choices):
        if any(choice not in self.state.grants for choice in choices):
            raise ConsentRequiredError(
                "This optional metascience choice is off; nothing was shared"
            )
        return {choice: self.state.grants[choice] for choice in choices}

    def _sink(self, channel):
        if self.sinks is not None:
            return self.sinks[channel]
        return HttpExportSink(
            os.environ.get(f"BENCHSIDE_{channel.upper()}_ENDPOINT", f"{COLLECTOR}/v1/{channel}")
        )

    @staticmethod
    def _retired(week, sample):
        return sample.inventory_sha256 == digest(["benchside.retired-sample", week])

    @staticmethod
    def _retirement_message(week):
        next_week = (date.fromisoformat(week) + timedelta(days=7)).isoformat()
        return (
            f"The sample for {week} was retired after an analysis or source change. "
            "It cannot be resumed or re-sampled. Select approved sources and sample "
            f"a later UTC week, starting {next_week}."
        )

    def _retire_samples(self, weeks):
        """Erase private selections; retain a marker so consent changes cannot redraw a week."""
        keys = {f"activity:{week}" for week in weeks}
        samples = dict(self.state.samples)
        for week in weeks:
            previous = samples[week]
            samples[week] = Sample(
                id=previous.id,
                inventory_sha256=digest(["benchside.retired-sample", week]),
                eligible=0,
                selected={},
                revision=previous.revision,
            )
        return {
            "samples": samples,
            "latest": {k: v for k, v in self.state.latest.items() if k not in keys},
            "drafts": {
                key: draft
                for key, draft in self.state.drafts.items()
                if draft.key not in keys or key in self.state.receipts
            },
        }

    def _retained_drafts(self, drafts, latest):
        keep = set(latest.values()) | set(self.state.receipts)
        return {key: draft for key, draft in drafts.items() if key in keep}

    def status(self):
        return {
            "choices": {
                name: name in self.state.grants for name in ("invitations", "analysis", "sharing")
            },
            "scopes": [s.model_dump() for s in self.state.scopes],
            "last_invitation": self.state.last_invitation,
            "open_invitations": [
                s.model_dump()
                for key, s in self.state.studies.items()
                if "invitations" in self.state.grants
                and key not in self.state.completed
                and s.active(self.today.isoformat())
            ],
            "weeks": [
                week
                for week, sample in self.state.samples.items()
                if not self._retired(week, sample)
            ],
            "retired_weeks": [
                week for week, sample in self.state.samples.items() if self._retired(week, sample)
            ],
            "pending_drafts": [
                d for d in self.state.latest.values() if d not in self.state.receipts
            ],
            "limits": {"invitation_days": 7, "sample_percent": 10, "sessions_per_week": 5},
        }

    def consent(self, choice, enabled):
        if choice not in {"invitations", "analysis", "sharing"} or type(enabled) is not bool:
            raise ValidationError("Choose invitations, analysis or sharing and true or false")
        grants = dict(self.state.grants)
        if enabled:
            grants.setdefault(choice, uuid.uuid4().hex)
        else:
            grants.pop(choice, None)
        reset_scopes = choice == "analysis" and (not enabled or "analysis" not in self.state.grants)
        retired = self._retire_samples(self.state.samples) if reset_scopes else {}
        if reset_scopes:
            # Survey participation is independent. Keep submitted activity payloads
            # only as receipt evidence; they contain no source or session references.
            retired["latest"] = {
                k: v for k, v in retired["latest"].items() if not k.startswith("activity:")
            }
            retired["drafts"] = {
                k: d
                for k, d in retired["drafts"].items()
                if d.channel != "activity" or k in self.state.receipts
            }
        self._save(
            grants=grants,
            scopes=[] if reset_scopes else self.state.scopes,
            **retired,
        )
        return self.status()

    def scopes(self, scopes):
        self._require("analysis")
        selected = [Scope.model_validate(s) for s in scopes]
        if len({canonical(s.model_dump()) for s in selected}) != len(selected):
            raise ValidationError("Select each source only once")
        if selected != self.state.scopes:
            # Changing scope invalidates every pending observation approval.
            grants = {**self.state.grants, "analysis": uuid.uuid4().hex}
            current_week = (self.today - timedelta(days=self.today.weekday())).isoformat()
            narrowed = any(scope not in selected for scope in self.state.scopes)
            affected = [
                week
                for week, sample in self.state.samples.items()
                if (narrowed and week == current_week)
                or any(c.scope not in selected for c in sample.selected.values())
            ]
            self._save(scopes=selected, grants=grants, **self._retire_samples(affected))
        return self.status()

    def invitations(self):
        self._require("invitations")
        today = self.today.isoformat()
        if (
            self.state.last_invitation
            and (self.today - date.fromisoformat(self.state.last_invitation)).days < 7
        ):
            return {"invitation": None, "reason": "weekly_limit"}
        if self.state.last_check == today:
            return {"invitation": None, "reason": "already_checked_today"}
        # Persist the cooldown even if the endpoint is unavailable.
        self._save(last_check=today)
        catalog = (self.catalog or StudyClient()).fetch()
        for study in catalog.studies:
            if study.key in self.state.studies and study != self.state.studies[study.key]:
                raise ValidationError(
                    "Study changed without a version bump; do not invite or submit"
                )
            if (
                study.active(today)
                and study.id not in self.state.dismissed
                and study.key not in self.state.completed
                and study.key not in self.state.studies
            ):
                self._save(studies={**self.state.studies, study.key: study}, last_invitation=today)
                return {
                    "invitation": study.model_dump(),
                    "study_sha256": digest(study.model_dump()),
                }
        return {"invitation": None, "reason": "no_new_studies"}

    def dismiss(self, study_key, *, permanently=False):
        if type(permanently) is not bool or study_key not in self.state.studies:
            raise ValidationError("Choose an existing invitation")
        study = self.state.studies[study_key]
        self._save(
            completed=list(dict.fromkeys([*self.state.completed, study_key])),
            dismissed=list(dict.fromkeys([*self.state.dismissed, study.id]))
            if permanently
            else self.state.dismissed,
        )
        return {"dismissed": study_key, "permanently": permanently}

    def _preview(self, channel, key, payload, grants):
        sink = self._sink(channel)
        text = canonical(payload.model_dump(mode="json", by_alias=True))
        current = self.state.drafts.get(self.state.latest.get(key))
        if (
            current
            and current.payload == text
            and current.grants == grants
            and current.destination == sink.destination
        ):
            retained = self._retained_drafts(self.state.drafts, self.state.latest)
            if len(retained) != len(self.state.drafts):
                self._save(drafts=retained)
            return current.model_dump()
        draft = MetaDraft(
            id=uuid.uuid4().hex,
            channel=channel,
            key=key,
            grants=grants,
            payload=text,
            sha256=hashlib.sha256(text.encode()).hexdigest(),
            destination=sink.destination,
        )
        latest = {**self.state.latest, key: draft.id}
        retained = self._retained_drafts({**self.state.drafts, draft.id: draft}, latest)
        if len(retained) > 1000:
            raise ValidationError(
                "Metascience approval and receipt history is full; preserve the notebook "
                "and arrange archival before creating another draft. Consent can still be withdrawn."
            )
        self._save(drafts=retained, latest=latest)
        return draft.model_dump()

    def survey(self, study_key, answers):
        grants = self._require("invitations")
        study = self.state.studies.get(study_key)
        if (
            not study
            or not study.active(self.today.isoformat())
            or study_key in self.state.completed
        ):
            raise ValidationError("This survey is unavailable, dismissed or already answered")
        key = f"survey:{study_key}"
        previous = self.state.drafts.get(self.state.latest.get(key))
        response_id = json.loads(previous.payload)["response_id"] if previous else uuid.uuid4().hex
        payload = SurveyPayload(
            benchside_version=__version__,
            response_id=response_id,
            study_id=study.id,
            study_version=study.version,
            study_sha256=digest(study.model_dump()),
            answers=answers,
        )
        payload.check_study(study)
        return self._preview("surveys", key, payload, grants)

    def sample(self, candidates):
        self._require("analysis")
        if not self.state.scopes:
            raise ValidationError("Select accessible research projects or conversations first")
        if not isinstance(candidates, list) or len(candidates) > 500:
            raise ValidationError("Supply metadata for at most 500 eligible sessions")
        items = [Candidate.model_validate(c) for c in candidates]
        if any(c.scope not in self.state.scopes for c in items):
            raise ValidationError("A candidate is outside the researcher's selected sources")
        # The same conversation may be listed under more than one selected project.
        keyed = {digest([c.scope.host, c.session_ref]): c for c in items}
        if len(keyed) != len(items):
            raise ValidationError("A session was listed more than once")
        week = (self.today - timedelta(days=self.today.weekday())).isoformat()
        inventory = digest(sorted(keyed))
        previous = self.state.samples.get(week)
        if previous:
            if self._retired(week, previous):
                raise ValidationError(self._retirement_message(week))
            if any(c.scope not in self.state.scopes for c in previous.selected.values()):
                self._save(**self._retire_samples([week]))
                raise ValidationError(self._retirement_message(week))
            if inventory != previous.inventory_sha256:
                raise ValidationError(
                    "This week's sample is fixed; use metascience.batch to resume it"
                )
            return self.batch(week)
        eligible = {k: c for k, c in keyed.items() if k not in self.state.seen}
        # A fresh random seed is private; sorting hashes makes retries/order independent.
        ranked = sorted(eligible, key=lambda k: digest([self.state.seed, week, k]))
        chosen = ranked[: min(5, (len(eligible) + 9) // 10)]
        sample = Sample(
            id=uuid.uuid4().hex,
            inventory_sha256=inventory,
            eligible=len(eligible),
            selected={uuid.uuid4().hex: eligible[k] for k in chosen},
        )
        self._save(samples={**self.state.samples, week: sample}, seen=[*self.state.seen, *chosen])
        return self.batch(week)

    def _sample(self, week):
        self._require("analysis")
        sample = self.state.samples.get(week)
        if not sample:
            raise ValidationError("No sample is available within the current selected sources")
        if self._retired(week, sample):
            raise ValidationError(self._retirement_message(week))
        if any(c.scope not in self.state.scopes for c in sample.selected.values()):
            self._save(**self._retire_samples([week]))
            raise ValidationError(self._retirement_message(week))
        return sample

    def batch(self, week):
        return {"week": week, **self._sample(week).model_dump()}

    def record(self, week, token, classification):
        sample = self._sample(week)
        if token not in sample.selected:
            raise ValidationError("Only selected sessions can be classified")
        record = Classification.model_validate(classification)
        data = sample.model_dump()
        data["records"][token] = record
        # An earlier preview no longer represents the reviewed local findings.
        self._save(
            samples={**self.state.samples, week: Sample.model_validate(data)},
            latest={k: v for k, v in self.state.latest.items() if k != f"activity:{week}"},
        )
        return {"recorded": token, "week": week}

    def preview_activity(self, week, tokens=None):
        grants = self._require("analysis", "sharing")
        sample = self._sample(week)
        selected = sorted(sample.records if tokens is None else tokens)
        if (
            not selected
            or len(set(selected)) != len(selected)
            or any(t not in sample.records for t in selected)
        ):
            raise ValidationError("Choose one or more classified sessions, without duplicates")
        observations = [
            ActivityObservation(
                **sample.records[t].model_dump(),
                host=sample.selected[t].scope.host,
            )
            for t in selected
        ]
        payload = ActivityPayload(
            benchside_version=__version__,
            batch_id=sample.id,
            revision=sample.revision + 1,
            week=week,
            eligible=sample.eligible,
            selected=len(sample.selected),
            observations=observations,
        )
        # An identical repeat preview uses the existing bytes and approval token.
        key = f"activity:{week}"
        previous = self.state.drafts.get(self.state.latest.get(key))
        if previous:
            prior = ActivityPayload.model_validate_json(previous.payload)
            if payload.model_copy(update={"revision": prior.revision}) == prior:
                payload = prior
        data = sample.model_dump()
        data["revision"] = payload.revision
        self._save(samples={**self.state.samples, week: Sample.model_validate(data)})
        return self._preview("activity", key, payload, grants)

    def send(self, draft_id, approved_sha256):
        try:
            return self._send(draft_id, approved_sha256)
        except Exception as err:
            record_submission_failure(self.paths, err)
            raise

    def _send(self, draft_id, approved_sha256):
        draft = self.state.drafts.get(draft_id)
        if not draft or self.state.latest.get(draft.key) != draft_id:
            raise ConsentRequiredError("Review the current metascience draft first")
        if self._require(*draft.grants) != draft.grants:
            raise ConsentRequiredError("Consent changed; prepare and review a new draft")
        sink = self._sink(draft.channel)
        if approved_sha256 != draft.sha256 or sink.destination != draft.destination:
            raise ValidationError(
                "Approve the exact payload and destination in the current preview"
            )
        if draft.id in self.state.receipts:
            return self.state.receipts[draft.id].model_dump()
        if draft.channel == "surveys":
            key = draft.key.removeprefix("survey:")
            study = self.state.studies[key]
            if not study.active(self.today.isoformat()) or key in self.state.completed:
                raise ConsentRequiredError("The survey has closed or was dismissed")
            SurveyPayload.model_validate_json(draft.payload).check_study(study)
        receipt = sink.send(draft.payload)
        if receipt is None:
            raise InfrastructureError(
                "The collector did not acknowledge the submission",
                code="submission_receipt_invalid",
            )
        result = {
            "channel": draft.channel,
            "destination": draft.destination,
            **receipt.model_dump(mode="json"),
        }
        completed = self.state.completed
        if draft.channel == "surveys":
            completed = [*completed, draft.key.removeprefix("survey:")]
        self._save(receipts={**self.state.receipts, draft.id: result}, completed=completed)
        return result

    def dispatch(self, request):
        match request["action"]:
            case "metascience.status":
                return self.status()
            case "metascience.consent":
                return self.consent(request["choice"], request["enabled"])
            case "metascience.scopes":
                return self.scopes(request["scopes"])
            case "metascience.invitations":
                return self.invitations()
            case "metascience.dismiss":
                return self.dismiss(
                    request["study_key"], permanently=request.get("permanently", False)
                )
            case "metascience.survey":
                return self.survey(request["study_key"], request["answers"])
            case "metascience.sample":
                return self.sample(request["candidates"])
            case "metascience.batch":
                return self.batch(request["week"])
            case "metascience.record":
                return self.record(request["week"], request["token"], request["classification"])
            case "metascience.preview":
                return self.preview_activity(request["week"], request.get("tokens"))
            case "metascience.send":
                return self.send(request["draft_id"], request["approved_sha256"])
            case "metascience.history":
                return [r.model_dump() for r in self.state.receipts.values()]
            case _:
                raise ValidationError("Unknown metascience action")
