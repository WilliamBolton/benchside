from pydantic import BaseModel, ConfigDict, RootModel


class ValueObject(BaseModel):
    """Defined by its attributes, not identity. Frozen."""

    model_config = ConfigDict(frozen=True)


class RootValueObject[T](RootModel[T]):
    """A validated wrapper over a single primitive (an id, a slug, a version)."""

    model_config = ConfigDict(frozen=True)
