"""What the scientist reads before deciding to share.

The payload is the literal bytes an export would send, not a summary of them.
"""

from pydantic import Field

from benchside.domain.export.service.export import ExportService
from benchside.domain.shared.command import Result
from benchside.domain.shared.model.ids import ObservationId
from benchside.domain.shared.query import Query, QueryHandler


class PreviewExport(Query):
    pass


class ExportPreviewDetail(Result):
    payload: str
    observation_ids: list[ObservationId] = Field(default_factory=list)
    withheld: list[ObservationId] = Field(default_factory=list)
    redaction_findings: list[str] = Field(default_factory=list)
    has_active_grant: bool = False


class PreviewExportHandler(QueryHandler[PreviewExport, ExportPreviewDetail]):
    export_service: ExportService

    def run(self, query: PreviewExport) -> ExportPreviewDetail:
        preview = self.export_service.preview()
        return ExportPreviewDetail(
            payload=preview.payload,
            observation_ids=list(preview.observation_ids),
            withheld=list(preview.withheld),
            redaction_findings=list(preview.redaction_findings),
            has_active_grant=self.export_service.consent.has_active_grant(),
        )
