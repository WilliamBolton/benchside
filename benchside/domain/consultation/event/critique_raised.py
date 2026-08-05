from benchside.domain.consultation.model.value import Target
from benchside.domain.shared.event import Event
from benchside.domain.shared.model.ids import ConsultationId, CritiqueId, ProjectId


class CritiqueRaised(Event):
    """The persona challenged a claim, a method step, or an interpretation."""

    project_id: ProjectId
    consultation_id: ConsultationId
    critique_id: CritiqueId
    target: Target
