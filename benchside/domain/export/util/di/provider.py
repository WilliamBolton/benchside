from dishka import provide

from benchside.domain.export.command.export_observations import ExportObservationsHandler
from benchside.domain.export.command.grant_consent import GrantConsentHandler
from benchside.domain.export.command.revoke_consent import RevokeConsentHandler
from benchside.domain.export.query.consent_status import GetConsentStatusHandler
from benchside.domain.export.query.preview_export import PreviewExportHandler
from benchside.domain.export.service.consent import ConsentService
from benchside.domain.export.service.export import ExportService
from benchside.util.di import Provider, Scope


class ExportProvider(Provider):
    consent_service = provide(ConsentService, scope=Scope.UOW)
    export_service = provide(ExportService, scope=Scope.UOW)

    grant_handler = provide(GrantConsentHandler, scope=Scope.UOW)
    revoke_handler = provide(RevokeConsentHandler, scope=Scope.UOW)
    export_handler = provide(ExportObservationsHandler, scope=Scope.UOW)

    preview_handler = provide(PreviewExportHandler, scope=Scope.UOW)
    consent_status_handler = provide(GetConsentStatusHandler, scope=Scope.UOW)
