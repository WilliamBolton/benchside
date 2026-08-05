from benchside.domain.shared.event import Event
from benchside.domain.shared.model.ids import GrantId


class ConsentGranted(Event):
    """The scientist authorised sharing for the listed gap kinds."""

    grant_id: GrantId
    gap_kinds: frozenset[str]
