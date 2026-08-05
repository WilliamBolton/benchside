"""The gap taxonomy.

Kernel rather than domain-owned: consultation records gaps as they occur,
export reads them. A gap is the *shape* of a workflow breakdown, captured as a
closed sum at the moment it happens rather than distilled from prose later.

Free text describes tooling and process only -- never a hypothesis, a result,
or data. Redaction and consent are enforced by the export domain.
"""

from typing import Literal

from benchside.domain.shared.model.value import ValueObject


class MissingTool(ValueObject):
    task: str
    reached_for: str
    why_failed: str
    kind: Literal["missing_tool"] = "missing_tool"


class UnfindableData(ValueObject):
    sought: str
    where_searched: tuple[str, ...]
    kind: Literal["unfindable_data"] = "unfindable_data"


class ManualToil(ValueObject):
    task: str
    frequency: str
    kind: Literal["manual_toil"] = "manual_toil"


class DeadEnd(ValueObject):
    approach: str
    cost: str
    kind: Literal["dead_end"] = "dead_end"


class MissingIndex(ValueObject):
    question: str
    kind: Literal["missing_index"] = "missing_index"


Gap = MissingTool | UnfindableData | ManualToil | DeadEnd | MissingIndex

GAP_KINDS: frozenset[str] = frozenset(
    {"missing_tool", "unfindable_data", "manual_toil", "dead_end", "missing_index"}
)
