"""Writing compiled skills to disk.

`read_existing` exists so compilation can report freshness without writing,
which is what CI needs.
"""

from abc import abstractmethod
from typing import Protocol

from benchside.domain.authoring.model.skill import SkillDocument
from benchside.domain.shared.port.base import Port


class SkillWriter(Port, Protocol):
    @abstractmethod
    def write(self, document: SkillDocument) -> None: ...

    @abstractmethod
    def read_existing(self, filename: str) -> str | None: ...
