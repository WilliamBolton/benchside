"""Template rendering.

Expands {{PLACEHOLDER}} tokens against a persona. Implementations must fail
loudly on an unknown placeholder and on any token left unresolved -- silent
empties are how generated prompts rot.
"""

from abc import abstractmethod
from typing import Protocol

from benchside.domain.authoring.model.persona import Persona
from benchside.domain.shared.port.base import Port


class TemplateRenderer(Port, Protocol):
    @abstractmethod
    def render(self, template: str, persona: Persona) -> str: ...
