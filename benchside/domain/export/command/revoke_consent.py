from benchside.domain.export.service.consent import ConsentService
from benchside.domain.shared.command import Command, CommandHandler, Result
from benchside.domain.shared.model.ids import GrantId


class RevokeConsent(Command):
    pass


class ConsentRevocation(Result):
    grant_id: GrantId
    status: str


class RevokeConsentHandler(CommandHandler[RevokeConsent, ConsentRevocation]):
    consent_service: ConsentService

    def run(self, cmd: RevokeConsent) -> ConsentRevocation:
        revoked = self.consent_service.revoke()
        return ConsentRevocation(grant_id=revoked.id, status=revoked.status)
