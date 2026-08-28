from benchside.domain.authoring.service.authoring import AuthoringService
from benchside.domain.shared.command import Result
from benchside.domain.shared.model.ids import PersonaId
from benchside.domain.shared.query import Query, QueryHandler


class GetPersona(Query):
    persona_id: PersonaId


class PersonaDetail(Result):
    persona_id: PersonaId
    stance: str
    expertise: tuple[str, ...]
    forcing_questions: int
    failure_modes: int


class GetPersonaHandler(QueryHandler[GetPersona, PersonaDetail]):
    authoring_service: AuthoringService

    def run(self, query: GetPersona) -> PersonaDetail:
        persona = self.authoring_service.get(query.persona_id)
        return PersonaDetail(
            persona_id=persona.id,
            stance=persona.stance,
            expertise=persona.expertise,
            forcing_questions=len(persona.forcing_questions),
            failure_modes=len(persona.failure_modes),
        )
