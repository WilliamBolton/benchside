from benchside.domain.consultation.service.consultation import ConsultationService
from benchside.domain.shared.command import Command, CommandHandler, Result
from benchside.domain.shared.model.ids import ConsultationId


class CloseConsultation(Command):
    consultation_id: ConsultationId
    converged: bool
    detail: str


class ConsultationClosed(Result):
    consultation_id: ConsultationId
    state: str


class CloseConsultationHandler(CommandHandler[CloseConsultation, ConsultationClosed]):
    consultation_service: ConsultationService

    def run(self, cmd: CloseConsultation) -> ConsultationClosed:
        consultation = self.consultation_service.close(
            consultation_id=cmd.consultation_id,
            converged=cmd.converged,
            detail=cmd.detail,
        )
        return ConsultationClosed(
            consultation_id=consultation.id,
            state=consultation.state.kind,
        )
