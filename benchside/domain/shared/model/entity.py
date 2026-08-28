from pydantic import BaseModel


class Entity(BaseModel):
    """Has identity and a lifecycle, but is not a consistency boundary."""
