"""Persona and template loading.

Implemented against content/ on disk. An open set: registering a new
specialist means adding a file, never touching orchestration code.
"""

from abc import abstractmethod
from typing import Protocol

from benchside.domain.authoring.model.persona import Persona
from benchside.domain.shared.model.ids import PersonaId
from benchside.domain.shared.port.base import Port


class PersonaRepository(Port, Protocol):
    @abstractmethod
    def get(self, persona_id: PersonaId) -> Persona | None: ...

    @abstractmethod
    def list_all(self) -> list[Persona]: ...


class TemplateRepository(Port, Protocol):
    @abstractmethod
    def skill_template(self) -> str: ...

    @abstractmethod
    def block(self, name: str) -> str | None: ...
