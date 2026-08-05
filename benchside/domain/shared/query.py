"""Query side: the read half of CQRS.

Same shape as command.py -- Query DTO, Result DTO, Handler per file -- but
handlers must not mutate state.
"""

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Any, dataclass_transform

from pydantic import BaseModel

from benchside.domain.shared.command import Result


class Query(BaseModel):
    """A request for state. Also the CLI argument shape."""


@dataclass_transform()
class _QueryHandlerMeta(ABCMeta):
    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> type:
        cls = super().__new__(mcs, name, bases, namespace)
        if any(isinstance(b, mcs) for b in bases):
            return dataclass(cls)
        return cls


class QueryHandler[Q: Query, R: Result](metaclass=_QueryHandlerMeta):
    """Entry point for a read. Delegates to a service; never mutates."""

    @abstractmethod
    def run(self, query: Q) -> R: ...
