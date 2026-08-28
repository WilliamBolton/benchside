from benchside.domain.consultation.service.consultation import ConsultationService
from benchside.domain.shared.command import Command, CommandHandler, Result
from benchside.domain.shared.model.ids import ConsultationId, DecisionId


class RecordDecision(Command):
    consultation_id: ConsultationId
    decision_id: DecisionId
    decision: str
    rationale: str
    supersedes: DecisionId | None = None


class DecisionStored(Result):
    decision_id: DecisionId
    total_decisions: int


class RecordDecisionHandler(CommandHandler[RecordDecision, DecisionStored]):
    consultation_service: ConsultationService

    def run(self, cmd: RecordDecision) -> DecisionStored:
        project = self.consultation_service.record_decision(
            consultation_id=cmd.consultation_id,
            decision_id=cmd.decision_id,
            decision=cmd.decision,
            rationale=cmd.rationale,
            supersedes=cmd.supersedes,
        )
        return DecisionStored(decision_id=cmd.decision_id, total_decisions=len(project.decisions))
