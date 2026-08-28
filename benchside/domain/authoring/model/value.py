"""Authoring value objects.

A persona is authored as data in content/personas/. One record generates three
artifacts: the skill prose, the eval judge rubric, and the event vocabulary the
rendered skill may emit. That is what keeps prompt and rubric from drifting.
"""

from benchside.domain.shared.model.value import ValueObject


class ForcingQuestion(ValueObject):
    """A question the persona presses on until it gets a real answer."""

    ask: str
    push_until: str
    red_flags: tuple[str, ...] = ()


class FailureMode(ValueObject):
    """A way this persona goes wrong.

    Doubles as a judge-rubric criterion: the eval asks whether the rendered
    skill exhibited this, using the same text that generated the prompt.
    """

    name: str
    description: str


class RubricCriterion(ValueObject):
    """One scored line in a generated judge rubric."""

    name: str
    question: str
    derived_from: str


class Rubric(ValueObject):
    """The judge rubric for a persona, derived from its failure modes."""

    persona_id: str
    criteria: tuple[RubricCriterion, ...]
