"""Export business logic -- the disclosure chokepoint.

The only path from a local observation to anywhere else. Order matters and is
not negotiable: ask consent, filter to what the grant covers, redact, then
send the exact bytes that were previewed.
"""

import hashlib
import logging

from benchside.domain.export.model.value import ExportPreview, ExportRecord, Observation
from benchside.domain.export.port.redactor import Redactor
from benchside.domain.export.port.repository import ConsentRepository, ObservationReader
from benchside.domain.export.port.sink import ExportSink
from benchside.domain.export.service.consent import ConsentService
from benchside.domain.shared.error import ConsentRequiredError
from benchside.domain.shared.service import Service

logger = logging.getLogger(__name__)


class ExportService(Service):
    observations: ObservationReader
    consent: ConsentService
    redactor: Redactor
    sink: ExportSink
    ledger: ConsentRepository

    def preview(self) -> ExportPreview:
        """Render exactly what an export would send.

        Safe to call without a grant: it shows the scientist what sharing would
        mean before they decide. Nothing leaves the machine here.
        """
        raise NotImplementedError

    def export(self) -> ExportRecord:
        grant = self.consent.active_grant()
        if grant is None:
            raise ConsentRequiredError("No active consent grant; nothing was shared")
        raise NotImplementedError

    def _covered(self, grant_kinds: frozenset[str]) -> list[Observation]:
        return [o for o in self.observations.list_unshared() if o.gap.kind in grant_kinds]

    @staticmethod
    def _digest(payload: str) -> str:
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
