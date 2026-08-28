from benchside.domain.consultation.model.value import Resolution
from benchside.domain.shared.event import Event
from benchside.domain.shared.model.ids import ConsultationId, CritiqueId, ProjectId


class CritiqueResolved(Event):
    """An open critique was settled -- by revision, rebuttal, or acceptance."""

    project_id: ProjectId
    consultation_id: ConsultationId
    critique_id: CritiqueId
    resolution: Resolution
