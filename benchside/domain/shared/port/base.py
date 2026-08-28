from typing import Protocol


class Port(Protocol):
    """Marker for a domain-owned interface.

    Ports are Protocols with abstract methods. Implementations live in
    benchside/adapters/, never in the domain.
    """
