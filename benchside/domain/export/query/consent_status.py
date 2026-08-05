from pydantic import Field

from benchside.domain.export.service.consent import ConsentService
from benchside.domain.shared.command import Result
from benchside.domain.shared.model.ids import GrantId
from benchside.domain.shared.query import Query, QueryHandler


class GetConsentStatus(Query):
    pass


class ConsentStatus(Result):
    has_active_grant: bool
    grant_id: GrantId | None = None
    gap_kinds: list[str] = Field(default_factory=list)


class GetConsentStatusHandler(QueryHandler[GetConsentStatus, ConsentStatus]):
    consent_service: ConsentService

    def run(self, query: GetConsentStatus) -> ConsentStatus:
        grant = self.consent_service.active_grant()
        if grant is None:
            return ConsentStatus(has_active_grant=False)
        return ConsentStatus(
            has_active_grant=True,
            grant_id=grant.id,
            gap_kinds=sorted(grant.gap_kinds),
        )
