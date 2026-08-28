"""Consultation DI wiring: this domain's service and handlers.

Ports are bound to implementations in benchside/infrastructure/, not here.
"""

from dishka import provide

from benchside.domain.consultation.command.capture_gap import CaptureGapHandler
from benchside.domain.consultation.command.close import CloseConsultationHandler
from benchside.domain.consultation.command.open import OpenConsultationHandler
from benchside.domain.consultation.command.raise_critique import RaiseCritiqueHandler
from benchside.domain.consultation.command.record_decision import RecordDecisionHandler
from benchside.domain.consultation.command.resolve_critique import ResolveCritiqueHandler
from benchside.domain.consultation.command.state_hypothesis import StateHypothesisHandler
from benchside.domain.consultation.query.get_consultation import GetConsultationHandler
from benchside.domain.consultation.query.recall_project import RecallProjectHandler
from benchside.domain.consultation.service.consultation import ConsultationService
from benchside.util.di import Provider, Scope


class ConsultationProvider(Provider):
    service = provide(ConsultationService, scope=Scope.UOW)

    open_handler = provide(OpenConsultationHandler, scope=Scope.UOW)
    state_hypothesis_handler = provide(StateHypothesisHandler, scope=Scope.UOW)
    raise_critique_handler = provide(RaiseCritiqueHandler, scope=Scope.UOW)
    resolve_critique_handler = provide(ResolveCritiqueHandler, scope=Scope.UOW)
    record_decision_handler = provide(RecordDecisionHandler, scope=Scope.UOW)
    capture_gap_handler = provide(CaptureGapHandler, scope=Scope.UOW)
    close_handler = provide(CloseConsultationHandler, scope=Scope.UOW)

    get_consultation_handler = provide(GetConsultationHandler, scope=Scope.UOW)
    recall_project_handler = provide(RecallProjectHandler, scope=Scope.UOW)
