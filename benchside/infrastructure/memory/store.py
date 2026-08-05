"""In-memory port implementations.

Placeholders until the file-backed adapters land, and the fakes tests build
against. Nothing here persists across a process.
"""

from collections.abc import Iterable

from benchside.domain.authoring.model.persona import Persona
from benchside.domain.authoring.model.skill import SkillDocument
from benchside.domain.consultation.model.consultation import Consultation
from benchside.domain.consultation.model.project import Project
from benchside.domain.export.model.ledger import ConsentLedger
from benchside.domain.export.model.value import Observation
from benchside.domain.export.port.redactor import Finding
from benchside.domain.shared.error import ConfigurationError
from benchside.domain.shared.event import Event
from benchside.domain.shared.model.ids import ConsultationId, PersonaId, ProjectId


class InMemoryJournal:
    def __init__(self) -> None:
        self._events: dict[str, list[Event]] = {}

    def append(self, project_id: ProjectId, event: Event) -> None:
        self._events.setdefault(project_id.root, []).append(event)

    def read(self, project_id: ProjectId) -> Iterable[Event]:
        return list(self._events.get(project_id.root, []))

    def projects(self) -> Iterable[ProjectId]:
        return [ProjectId(k) for k in self._events]


class InMemoryProjectRepository:
    def __init__(self) -> None:
        self.projects: dict[str, Project] = {}

    def get(self, project_id: ProjectId) -> Project | None:
        return self.projects.get(project_id.root)

    def list_all(self) -> list[Project]:
        return list(self.projects.values())


class InMemoryConsultationRepository:
    def __init__(self) -> None:
        self.consultations: dict[str, Consultation] = {}

    def get(self, consultation_id: ConsultationId) -> Consultation | None:
        return self.consultations.get(consultation_id)

    def list_for_project(self, project_id: ProjectId) -> list[Consultation]:
        return [c for c in self.consultations.values() if c.project_id == project_id]

    def latest_for_project(self, project_id: ProjectId) -> Consultation | None:
        found = self.list_for_project(project_id)
        return found[-1] if found else None


class InMemoryPersonaRepository:
    def __init__(self) -> None:
        self.personas: dict[str, Persona] = {}

    def get(self, persona_id: PersonaId) -> Persona | None:
        return self.personas.get(persona_id.root)

    def list_all(self) -> list[Persona]:
        return list(self.personas.values())


class InMemoryTemplateRepository:
    def __init__(self) -> None:
        self.template = ""
        self.blocks: dict[str, str] = {}

    def skill_template(self) -> str:
        return self.template

    def block(self, name: str) -> str | None:
        return self.blocks.get(name)


class EchoTemplateRenderer:
    """Returns the template unchanged. A placeholder, not a renderer."""

    def render(self, template: str, persona: Persona) -> str:
        return template


class InMemorySkillWriter:
    def __init__(self) -> None:
        self.written: dict[str, str] = {}

    def write(self, document: SkillDocument) -> None:
        self.written[document.filename] = document.render()

    def read_existing(self, filename: str) -> str | None:
        return self.written.get(filename)


class InMemoryConsentRepository:
    def __init__(self) -> None:
        self._ledger = ConsentLedger()

    def load(self) -> ConsentLedger:
        return self._ledger


class InMemoryObservationReader:
    def __init__(self) -> None:
        self.observations: list[Observation] = []
        self.shared: set[str] = set()

    def list_all(self) -> list[Observation]:
        return list(self.observations)

    def list_unshared(self) -> list[Observation]:
        return [o for o in self.observations if o.id not in self.shared]


class PassthroughRedactor:
    """Reports nothing. A placeholder, never a production binding."""

    def scan(self, payload: str) -> list[Finding]:
        return []

    def apply(self, payload: str) -> str:
        return payload


class RefusingExportSink:
    """The safe default: refuses to send anything.

    The default wiring must not be able to leak. A real sink is bound
    explicitly, or not at all.
    """

    def send(self, payload: str) -> None:
        raise ConfigurationError("No export sink is configured; nothing was sent")
