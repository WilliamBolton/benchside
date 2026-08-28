"""Base class for all benchside DI providers.

A single import point, so provider modules never import dishka directly and
cross-cutting metadata can be added here later without touching every domain.
"""

from dishka import Provider as DishkaProvider


class Provider(DishkaProvider):
    """Base for every provider in benchside.

    Domain providers live in `benchside/domain/<name>/util/di/provider.py` and
    bind that domain's services and handlers. Adapter providers live in
    `benchside/adapters/<tech>/di.py` and bind ports to implementations.
    """
