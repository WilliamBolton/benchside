from benchside.domain.export.service.consent import ConsentService
from benchside.domain.shared.command import Command, CommandHandler, Result
from benchside.domain.shared.model.ids import GrantId


class GrantConsent(Command):
    grant_id: GrantId
    gap_kinds: frozenset[str]


class ConsentRecorded(Result):
    grant_id: GrantId
    gap_kinds: frozenset[str]
    status: str


class GrantConsentHandler(CommandHandler[GrantConsent, ConsentRecorded]):
    consent_service: ConsentService

    def run(self, cmd: GrantConsent) -> ConsentRecorded:
        grant = self.consent_service.grant(grant_id=cmd.grant_id, gap_kinds=cmd.gap_kinds)
        return ConsentRecorded(
            grant_id=grant.id,
            gap_kinds=grant.gap_kinds,
            status=grant.status,
        )
