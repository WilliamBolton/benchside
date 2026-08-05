"""Persistence interfaces.

Implementations fold the journal's event stream into aggregates; these ports
hide that, so the domain never knows the store is event-sourced.
"""

from abc import abstractmethod
from typing import Protocol

from benchside.domain.consultation.model.consultation import Consultation
from benchside.domain.consultation.model.project import Project
from benchside.domain.shared.model.ids import ConsultationId, ProjectId
from benchside.domain.shared.port.base import Port


class ProjectRepository(Port, Protocol):
    @abstractmethod
    def get(self, project_id: ProjectId) -> Project | None: ...

    @abstractmethod
    def list_all(self) -> list[Project]: ...


class ConsultationRepository(Port, Protocol):
    @abstractmethod
    def get(self, consultation_id: ConsultationId) -> Consultation | None: ...

    @abstractmethod
    def list_for_project(self, project_id: ProjectId) -> list[Consultation]: ...

    @abstractmethod
    def latest_for_project(self, project_id: ProjectId) -> Consultation | None: ...
