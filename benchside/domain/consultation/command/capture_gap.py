from benchside.domain.consultation.service.consultation import ConsultationService
from benchside.domain.shared.command import Command, CommandHandler, Result
from benchside.domain.shared.model.gap import Gap
from benchside.domain.shared.model.ids import ConsultationId, ObservationId


class CaptureGap(Command):
    consultation_id: ConsultationId
    observation_id: ObservationId
    gap: Gap


class GapCaptured(Result):
    observation_id: ObservationId
    kind: str
    shared: bool = False


class CaptureGapHandler(CommandHandler[CaptureGap, GapCaptured]):
    consultation_service: ConsultationService

    def run(self, cmd: CaptureGap) -> GapCaptured:
        self.consultation_service.capture_gap(
            consultation_id=cmd.consultation_id,
            observation_id=cmd.observation_id,
            gap=cmd.gap,
        )
        return GapCaptured(observation_id=cmd.observation_id, kind=cmd.gap.kind)
