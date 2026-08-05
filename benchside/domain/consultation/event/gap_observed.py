from benchside.domain.shared.event import Event
from benchside.domain.shared.model.gap import Gap
from benchside.domain.shared.model.ids import ConsultationId, ObservationId, ProjectId


class GapObserved(Event):
    """The scientific workflow broke down. Local until export is consented to.

    Recorded here because gaps surface during meetings; read by the export
    domain, which governs whether they ever leave the machine.
    """

    project_id: ProjectId
    consultation_id: ConsultationId
    observation_id: ObservationId
    gap: Gap
