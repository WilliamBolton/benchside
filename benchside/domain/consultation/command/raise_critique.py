from benchside.domain.consultation.model.value import Target
from benchside.domain.consultation.service.consultation import ConsultationService
from benchside.domain.shared.command import Command, CommandHandler, Result
from benchside.domain.shared.model.ids import ConsultationId, CritiqueId


class RaiseCritique(Command):
    consultation_id: ConsultationId
    critique_id: CritiqueId
    target: Target


class CritiqueRecorded(Result):
    critique_id: CritiqueId
    open_critiques: int


class RaiseCritiqueHandler(CommandHandler[RaiseCritique, CritiqueRecorded]):
    consultation_service: ConsultationService

    def run(self, cmd: RaiseCritique) -> CritiqueRecorded:
        project = self.consultation_service.raise_critique(
            consultation_id=cmd.consultation_id,
            critique_id=cmd.critique_id,
            target=cmd.target,
        )
        return CritiqueRecorded(
            critique_id=cmd.critique_id,
            open_critiques=len(project.open_critiques),
        )
