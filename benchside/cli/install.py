"""Install shared agent instructions and optional legacy Claude Code project hooks."""

import json
import sys
from pathlib import Path

from benchside.application.di import create_container
from benchside.cli import runtime
from benchside.domain.authoring.port.renderer import TemplateRenderer
from benchside.domain.authoring.port.repository import PersonaRepository, TemplateRepository
from benchside.domain.authoring.service.authoring import AuthoringService
from benchside.infrastructure.content.writer import FileSkillWriter
from benchside.util.di import Scope

_TAG = "_benchside"
_HOOK_TIMEOUTS = {"SessionStart": 10, "SessionEnd": 15}


def _skill_directory(args, root: Path) -> Path:
    if args.skills_dir:
        return Path(args.skills_dir).expanduser().resolve()
    return root / (".claude" if args.agent == "claude" else ".agents") / "skills"


def _configure_storage(args):
    if args.storage:
        from benchside.config import configure_local_storage

        configure_local_storage(args.storage)


def _install_app_skill(target: Path):
    from benchside.application.packaging import build_agent_skill
    from benchside.config import resolve_content_root

    if (resolve_content_root() / "app").is_dir():
        build_agent_skill(target / "benchside")


def cmd_init(args) -> int:
    project_dir = Path.cwd()
    project_id = runtime.resolve_project(args.project)
    target = _skill_directory(args, project_dir)
    hooks = args.agent == "claude"
    details = " and register Claude Code session hooks" if hooks else ""
    if not args.yes and not _confirm(
        f"Create .bench/config.yaml, install Benchside into {target}{details}?"
    ):
        print("init cancelled; nothing written")
        return 1
    _configure_storage(args)
    config = project_dir / ".bench" / "config.yaml"
    config.parent.mkdir(parents=True, exist_ok=True)
    if not config.is_file():
        config.write_text(f"project: {project_id.root}\n", encoding="utf-8")
    if hooks:
        _register_hooks(project_dir / ".claude" / "settings.json")
        _compile_skills(target)
    _install_app_skill(target)
    print(f"initialized benchside project '{project_id.root}'")
    print(f"  skills: {target}")
    print(f"  local record directory: {runtime.current_paths().home}")
    print("Optional submissions require separate consent and an approved preview.")
    print(
        "Ask Benchside to choose storage and select or create a research project before recording."
    )
    return 0


def _confirm(prompt: str) -> bool:
    if not sys.stdin.isatty():
        print("non-interactive session: pass --yes to consent to init", file=sys.stderr)
        return False
    return input(f"{prompt} [y/N] ").strip().lower() in {"y", "yes"}


def _register_hooks(settings_path: Path) -> None:
    """Idempotent under the _benchside tag; never clobbers other hooks."""
    settings: dict = {}
    if settings_path.is_file():
        settings = json.loads(settings_path.read_text(encoding="utf-8") or "{}")
    hooks = settings.setdefault("hooks", {})
    for event, subcommand in (("SessionStart", "session-start"), ("SessionEnd", "session-end")):
        groups = hooks.setdefault(event, [])
        if any(group.get(_TAG) for group in groups):
            continue
        groups.append(
            {
                _TAG: "v1",
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": f"bench hook {subcommand}",
                        "timeout": _HOOK_TIMEOUTS[event],
                    }
                ],
            }
        )
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")


def _compile_skills(target_dir: Path) -> None:
    """Compile personas straight into the project's skill directory."""
    container = create_container()
    with container, container(scope=Scope.UOW) as uow:
        service = AuthoringService(
            personas=uow.get(PersonaRepository),
            templates=uow.get(TemplateRepository),
            renderer=uow.get(TemplateRenderer),
            writer=FileSkillWriter(target_dir),
        )
        service.compile()
    import shutil

    from benchside.config import resolve_content_root

    sharing_skill = resolve_content_root() / "claude" / "bench-share"
    if sharing_skill.is_dir():  # Custom authoring roots may contain only personas.
        shutil.copytree(sharing_skill, target_dir / "bench-share", dirs_exist_ok=True)


def cmd_setup(args) -> int:
    """Install agent instructions without assuming a particular model or storage provider."""
    from benchside.config import resolve_content_root

    _configure_storage(args)
    target = _skill_directory(args, Path.home())
    _install_app_skill(target)
    if args.agent == "claude":
        source = resolve_content_root() / "claude" / "bench-init" / "SKILL.md"
        destination = target / "bench-init" / "SKILL.md"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"installed /bench-init skill -> {destination}")
    print(f"Benchside instructions installed in {target}.")
    print("Ask your agent to set up Benchside; it will ask where to store your records.")
    print(
        "Other agents can read benchside/SKILL.md explicitly if they do not discover skills here."
    )
    return 0
