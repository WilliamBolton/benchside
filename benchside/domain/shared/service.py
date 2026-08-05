"""Service base.

Subclasses declare their dependencies as annotated fields; the metaclass makes
them dataclasses so Dishka can construct them by keyword.
"""

from dataclasses import dataclass
from typing import Any, dataclass_transform


@dataclass_transform()
class _ServiceMeta(type):
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


class Service(metaclass=_ServiceMeta):
    """Base for domain services. Subclasses are automatically dataclasses.

    Services hold the business logic. They depend on their own domain's ports,
    on the journal, and on other domains' services -- never on another domain's
    repository directly.
    """
