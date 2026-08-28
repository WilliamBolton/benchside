from dishka import provide

from benchside.domain.authoring.command.compile import CompileSkillsHandler
from benchside.domain.authoring.query.get_persona import GetPersonaHandler
from benchside.domain.authoring.query.list_personas import ListPersonasHandler
from benchside.domain.authoring.service.authoring import AuthoringService
from benchside.util.di import Provider, Scope


class AuthoringProvider(Provider):
    service = provide(AuthoringService, scope=Scope.UOW)

    compile_handler = provide(CompileSkillsHandler, scope=Scope.UOW)
    get_persona_handler = provide(GetPersonaHandler, scope=Scope.UOW)
    list_personas_handler = provide(ListPersonasHandler, scope=Scope.UOW)
