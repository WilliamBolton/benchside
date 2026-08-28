from abc import abstractmethod
from typing import Protocol

from benchside.domain.export.model.ledger import ConsentLedger
from benchside.domain.export.model.value import Observation
from benchside.domain.shared.port.base import Port


class ConsentRepository(Port, Protocol):
    @abstractmethod
    def load(self) -> ConsentLedger: ...


class ObservationReader(Port, Protocol):
    """Read-only cross-domain port.

    Gaps are recorded by consultation; this folds GapObserved events out of the
    journal so export never reaches into consultation's aggregates.
    """

    @abstractmethod
    def list_all(self) -> list[Observation]: ...

    @abstractmethod
    def list_unshared(self) -> list[Observation]: ...
