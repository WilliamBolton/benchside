"""Binds every port to an in-memory implementation.

This is the port seam: `provides=` names the interface, the class is the
implementation. Swapping to the file-backed store means swapping this provider
and nothing else.
"""

from dishka import provide

from benchside.domain.authoring.port.renderer import TemplateRenderer
from benchside.domain.authoring.port.repository import PersonaRepository, TemplateRepository
from benchside.domain.authoring.port.skill_writer import SkillWriter
from benchside.domain.consultation.port.repository import (
    ConsultationRepository,
    ProjectRepository,
)
from benchside.domain.export.port.redactor import Redactor
from benchside.domain.export.port.repository import ConsentRepository, ObservationReader
from benchside.domain.export.port.sink import ExportSink
from benchside.domain.shared.port.journal import Journal
from benchside.infrastructure.memory.store import (
    EchoTemplateRenderer,
    InMemoryConsentRepository,
    InMemoryConsultationRepository,
    InMemoryJournal,
    InMemoryObservationReader,
    InMemoryPersonaRepository,
    InMemoryProjectRepository,
    InMemorySkillWriter,
    InMemoryTemplateRepository,
    PassthroughRedactor,
    RefusingExportSink,
)
from benchside.util.di import Provider, Scope


class MemoryProvider(Provider):
    journal = provide(InMemoryJournal, scope=Scope.APP, provides=Journal)

    projects = provide(InMemoryProjectRepository, scope=Scope.APP, provides=ProjectRepository)
    consultations = provide(
        InMemoryConsultationRepository, scope=Scope.APP, provides=ConsultationRepository
    )

    personas = provide(InMemoryPersonaRepository, scope=Scope.APP, provides=PersonaRepository)
    templates = provide(InMemoryTemplateRepository, scope=Scope.APP, provides=TemplateRepository)
    renderer = provide(EchoTemplateRenderer, scope=Scope.APP, provides=TemplateRenderer)
    skill_writer = provide(InMemorySkillWriter, scope=Scope.APP, provides=SkillWriter)

    consent = provide(InMemoryConsentRepository, scope=Scope.APP, provides=ConsentRepository)
    observations = provide(
        InMemoryObservationReader, scope=Scope.APP, provides=ObservationReader
    )
    redactor = provide(PassthroughRedactor, scope=Scope.APP, provides=Redactor)
    sink = provide(RefusingExportSink, scope=Scope.APP, provides=ExportSink)
