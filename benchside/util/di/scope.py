"""Dependency-injection scopes.

benchside is a CLI, not a server: there is no request. One `bench` invocation
is one unit of work.
"""

from dishka import BaseScope, new_scope


class Scope(BaseScope):  # type: ignore[misc]  # BaseScope is designed to be subclassed
    """Hierarchy: APP -> UOW

    - APP: process lifetime (config, path resolution, template registry)
    - UOW: one command or query execution (journal handle, services, handlers)
    """

    APP = new_scope("APP")
    UOW = new_scope("UOW")
