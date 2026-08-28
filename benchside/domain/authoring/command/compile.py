from pydantic import Field

from benchside.domain.authoring.service.authoring import AuthoringService
from benchside.domain.shared.command import Command, CommandHandler, Result


class CompileSkills(Command):
    dry_run: bool = False


class SkillsCompiled(Result):
    written: list[str] = Field(default_factory=list)
    unchanged: list[str] = Field(default_factory=list)
    stale: list[str] = Field(default_factory=list)
    is_fresh: bool = True


class CompileSkillsHandler(CommandHandler[CompileSkills, SkillsCompiled]):
    authoring_service: AuthoringService

    def run(self, cmd: CompileSkills) -> SkillsCompiled:
        report = self.authoring_service.compile(dry_run=cmd.dry_run)
        return SkillsCompiled(
            written=list(report.written),
            unchanged=list(report.unchanged),
            stale=list(report.stale),
            is_fresh=report.is_fresh,
        )
