from benchside.domain.consultation.service.consultation import ConsultationService
from benchside.domain.shared.command import Command, CommandHandler, Result
from benchside.domain.shared.model.ids import ConsultationId, PersonaId, ProjectId


class OpenConsultation(Command):
    consultation_id: ConsultationId
    project_id: ProjectId
    persona_id: PersonaId


class ConsultationOpened(Result):
    consultation_id: ConsultationId
    state: str


class OpenConsultationHandler(CommandHandler[OpenConsultation, ConsultationOpened]):
    consultation_service: ConsultationService

    def run(self, cmd: OpenConsultation) -> ConsultationOpened:
        consultation = self.consultation_service.open(
            consultation_id=cmd.consultation_id,
            project_id=cmd.project_id,
            persona_id=cmd.persona_id,
        )
        return ConsultationOpened(
            consultation_id=consultation.id,
            state=consultation.state.kind,
        )
