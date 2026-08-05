"""The compiled artifact.

A SkillDocument is what lands in skills/ and what Claude Code loads. It is
always generated: editing one by hand is a bug the freshness check catches.
"""

from benchside.domain.shared.model.value import ValueObject


class SkillDocument(ValueObject):
    """A rendered SKILL.md: frontmatter plus body, addressed by persona."""

    persona_id: str
    filename: str
    frontmatter: str
    body: str

    def render(self) -> str:
        return f"---\n{self.frontmatter}\n---\n\n{self.body}"


class CompileReport(ValueObject):
    """The outcome of a compile run, for `bench compile` and CI to print."""

    written: tuple[str, ...] = ()
    unchanged: tuple[str, ...] = ()
    stale: tuple[str, ...] = ()

    @property
    def is_fresh(self) -> bool:
        """True when no generated file differs from what the sources produce."""
        return not self.stale
