from pydantic import BaseModel


class Aggregate(BaseModel):
    """Consistency boundary. Mutable, and owns its own state transitions.

    An aggregate raises InvalidStateError rather than letting a caller put it
    into an illegal state.
    """
