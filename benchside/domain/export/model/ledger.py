"""The ConsentLedger aggregate.

Append-only. The active grant is computed by folding the history, never stored
as a mutable flag, so "is sharing on?" always has one answer derived from the
same events the audit trail shows.
"""

from pydantic import Field

from benchside.domain.export.model.value import ExportRecord, Grant
from benchside.domain.shared.error import InvalidStateError
from benchside.domain.shared.model.aggregate import Aggregate


class ConsentLedger(Aggregate):
    grants: list[Grant] = Field(default_factory=list)
    exports: list[ExportRecord] = Field(default_factory=list)

    @property
    def active_grant(self) -> Grant | None:
        for grant in reversed(self.grants):
            if grant.revoked_at is None:
                return grant
        return None

    def grant(self, grant: Grant) -> None:
        if self.active_grant is not None:
            raise InvalidStateError("A grant is already active; revoke it before granting again")
        self.grants.append(grant)

    def revoke(self, revoked_at: object) -> Grant:
        active = self.active_grant
        if active is None:
            raise InvalidStateError("There is no active grant to revoke")
        revoked = active.model_copy(update={"revoked_at": revoked_at})
        self.grants[self.grants.index(active)] = revoked
        return revoked

    def record_export(self, record: ExportRecord) -> None:
        self.exports.append(record)
