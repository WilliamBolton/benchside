from benchside.domain.shared.event import Event
from benchside.domain.shared.model.ids import ConsultationId, HypothesisId, ProjectId


class HypothesisStated(Event):
    """A hypothesis was put on the table, possibly replacing an earlier one."""

    project_id: ProjectId
    consultation_id: ConsultationId
    hypothesis_id: HypothesisId
    statement: str
    supersedes: HypothesisId | None = None
