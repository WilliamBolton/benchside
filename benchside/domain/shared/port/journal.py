"""The journal port.

Kernel rather than domain-owned: consultation appends, export reads. One
append-only stream per project.
"""

from abc import abstractmethod
from collections.abc import Iterable
from typing import Protocol

from benchside.domain.shared.event import Event
from benchside.domain.shared.model.ids import ProjectId
from benchside.domain.shared.port.base import Port


class Journal(Port, Protocol):
    """Append-only event stream, partitioned by project.

    Implementations must append atomically and must never rewrite history:
    corrections are new events that supersede old ones.
    """

    @abstractmethod
    def append(self, project_id: ProjectId, event: Event) -> None: ...

    @abstractmethod
    def read(self, project_id: ProjectId) -> Iterable[Event]: ...

    @abstractmethod
    def projects(self) -> Iterable[ProjectId]: ...
