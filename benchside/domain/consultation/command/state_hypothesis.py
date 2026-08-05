from benchside.domain.consultation.service.consultation import ConsultationService
from benchside.domain.shared.command import Command, CommandHandler, Result
from benchside.domain.shared.model.ids import ConsultationId, HypothesisId


class StateHypothesis(Command):
    consultation_id: ConsultationId
    hypothesis_id: HypothesisId
    statement: str
    supersedes: HypothesisId | None = None


class HypothesisRecorded(Result):
    hypothesis_id: HypothesisId
    supersedes: HypothesisId | None = None


class StateHypothesisHandler(CommandHandler[StateHypothesis, HypothesisRecorded]):
    consultation_service: ConsultationService

    def run(self, cmd: StateHypothesis) -> HypothesisRecorded:
        self.consultation_service.state_hypothesis(
            consultation_id=cmd.consultation_id,
            hypothesis_id=cmd.hypothesis_id,
            statement=cmd.statement,
            supersedes=cmd.supersedes,
        )
        return HypothesisRecorded(hypothesis_id=cmd.hypothesis_id, supersedes=cmd.supersedes)
