from benchside.domain.shared.event import Event
from benchside.domain.shared.model.ids import GrantId


class ConsentRevoked(Event):
    """Sharing was switched off. Prior exports remain in the ledger."""

    grant_id: GrantId
