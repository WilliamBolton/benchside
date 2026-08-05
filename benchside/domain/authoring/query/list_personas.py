from pydantic import Field

from benchside.domain.authoring.service.authoring import AuthoringService
from benchside.domain.shared.command import Result
from benchside.domain.shared.model.ids import PersonaId
from benchside.domain.shared.query import Query, QueryHandler


class ListPersonas(Query):
    pass


class PersonaList(Result):
    persona_ids: list[PersonaId] = Field(default_factory=list)


class ListPersonasHandler(QueryHandler[ListPersonas, PersonaList]):
    authoring_service: AuthoringService

    def run(self, query: ListPersonas) -> PersonaList:
        return PersonaList(persona_ids=[p.id for p in self.authoring_service.list_all()])
