"""Port implementations.

One subpackage per technology, each with a `di.py` exposing a
`<Tech>Provider` that binds ports to concrete classes via `provides=`.
Planned: `journal/` (JSONL append-only store), `content/` (persona and
template loading from content/), `redact/` (the redaction engine).

Nothing here may be imported from benchside/domain/.
"""
