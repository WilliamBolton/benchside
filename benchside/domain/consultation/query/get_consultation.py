from benchside.domain.consultation.service.consultation import ConsultationService
from benchside.domain.shared.command import Result
from benchside.domain.shared.model.ids import ConsultationId, PersonaId, ProjectId
from benchside.domain.shared.query import Query, QueryHandler


class GetConsultation(Query):
    consultation_id: ConsultationId


class ConsultationDetail(Result):
    consultation_id: ConsultationId
    project_id: ProjectId
    persona_id: PersonaId
    state: str


class GetConsultationHandler(QueryHandler[GetConsultation, ConsultationDetail]):
    consultation_service: ConsultationService

    def run(self, query: GetConsultation) -> ConsultationDetail:
        consultation = self.consultation_service.get(query.consultation_id)
        return ConsultationDetail(
            consultation_id=consultation.id,
            project_id=consultation.project_id,
            persona_id=consultation.persona_id,
            state=consultation.state.kind,
        )
