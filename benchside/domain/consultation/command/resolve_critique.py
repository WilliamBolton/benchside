from benchside.domain.consultation.model.value import Resolution
from benchside.domain.consultation.service.consultation import ConsultationService
from benchside.domain.shared.command import Command, CommandHandler, Result
from benchside.domain.shared.model.ids import ConsultationId, CritiqueId


class ResolveCritique(Command):
    consultation_id: ConsultationId
    critique_id: CritiqueId
    resolution: Resolution


class CritiqueSettled(Result):
    critique_id: CritiqueId
    resolution: Resolution
    open_critiques: int


class ResolveCritiqueHandler(CommandHandler[ResolveCritique, CritiqueSettled]):
    consultation_service: ConsultationService

    def run(self, cmd: ResolveCritique) -> CritiqueSettled:
        project = self.consultation_service.resolve_critique(
            consultation_id=cmd.consultation_id,
            critique_id=cmd.critique_id,
            resolution=cmd.resolution,
        )
        return CritiqueSettled(
            critique_id=cmd.critique_id,
            resolution=cmd.resolution,
            open_critiques=len(project.open_critiques),
        )
