from typing import Literal

from benchside.domain.shared.event import Event
from benchside.domain.shared.model.ids import ConsultationId, ProjectId


class ConsultationClosed(Event):
    """The sitting ended. `detail` is the outcome or the abandonment reason."""

    project_id: ProjectId
    consultation_id: ConsultationId
    state: Literal["converged", "abandoned"]
    detail: str
