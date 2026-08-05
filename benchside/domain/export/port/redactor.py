"""Redaction, applied to everything before it can leave the machine.

Scan the exact bytes that will be sent. Never scan a string and then re-render
it: that reopens a scan-versus-send gap.
"""

from abc import abstractmethod
from typing import Protocol

from benchside.domain.shared.model.value import ValueObject
from benchside.domain.shared.port.base import Port


class Finding(ValueObject):
    """Something the redactor objects to, and where."""

    tier: str
    category: str
    field: str


class Redactor(Port, Protocol):
    @abstractmethod
    def scan(self, payload: str) -> list[Finding]: ...

    @abstractmethod
    def apply(self, payload: str) -> str: ...
