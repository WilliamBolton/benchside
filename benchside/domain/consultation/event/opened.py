from benchside.domain.shared.event import Event
from benchside.domain.shared.model.ids import ConsultationId, PersonaId, ProjectId


class ConsultationOpened(Event):
    """A scientist started a sitting with a persona."""

    consultation_id: ConsultationId
    project_id: ProjectId
    persona_id: PersonaId
