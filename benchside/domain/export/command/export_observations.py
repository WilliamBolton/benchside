from pydantic import Field

from benchside.domain.export.service.export import ExportService
from benchside.domain.shared.command import Command, CommandHandler, Result
from benchside.domain.shared.model.ids import GrantId, ObservationId


class ExportObservations(Command):
    pass


class ObservationsSent(Result):
    grant_id: GrantId
    observation_ids: list[ObservationId] = Field(default_factory=list)
    payload_sha256: str


class ExportObservationsHandler(CommandHandler[ExportObservations, ObservationsSent]):
    export_service: ExportService

    def run(self, cmd: ExportObservations) -> ObservationsSent:
        record = self.export_service.export()
        return ObservationsSent(
            grant_id=record.grant_id,
            observation_ids=list(record.observation_ids),
            payload_sha256=record.payload_sha256,
        )
