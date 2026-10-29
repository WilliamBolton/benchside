# Benchside: investigate reliable Claude cloud memory

Update, 29 October: the latest review package is now 0.3.0. It adds optional
workflow context and a native v3 compatibility gate; it does not solve the
transport failure below. Use the latest PR #5 source when prototyping. The
observations below were made with 0.2.0 and remain useful reproduction evidence.

## Task

Investigate and test the smallest dependable way for the installed Benchside
plugin to save and restore private scientific records in Claude. Please inspect
your actual tools and capabilities rather than assuming that another agent's
description of Claude is complete. Prefer a working native integration if one
exists. Do not treat another successful tiny notebook as proof that the larger
failure has been fixed.

Produce a concrete diagnosis, a tested prototype where feasible, timings and an
implementation handoff. Do not merge PRs or publish a release. Test with synthetic
records only; leave optional sharing off and send nothing to Science Works.

## Current source and installed version

- Repository: https://github.com/science-works/benchside
- Main rollout PR: https://github.com/science-works/benchside/pull/5
- PR source: `WilliamBolton/benchside`, branch `codex/research-roles-rollout`.
- Last verified source commit before this brief: `46fddd4`.
- Installed Claude plugin and runtime: **0.2.0**.
- Local source, if available: `/Users/will/Code/science-works/benchside`.
- Storage logic: `benchside/application/native.py`.
- Launcher: `content/app/scripts/benchside_app.py`.
- Instructions: `content/app/references/native-memory.md`, `onboarding.md`,
  `app-api.md`, and `content/app/SKILL.md`.
- Source packaging: `benchside/application/packaging.py`, `scripts/build_release.py`.

The latest source instructions now warn about inline-copy transport and stop
unsafe recovery attempts. These instruction changes are not yet in the installed
0.2.0 package. They are guardrails, not a completed transport fix.

## Observed failure, 29 October 2026

Test conversation:
https://claude.ai/chat/2d14f553-0f5e-4856-b678-b1b31154e6b0

Existing synthetic notebook (read-only reference; do not change it):
https://claude.ai/artifact/YAqaPuj38DrHxihnRZxwQQ

- Title: **Benchside private notebook — ACCEPT-20261028-A (synthetic)**.
- Document ID: `fc6aeda3-6e4a-4af6-9243-23a7a43d16bd`.
- Observed Docs revision: **14**.
- Envelope reported snapshot revision **8**, workspace
  `379b4b2d707240f1ad9639536e68931b`, but was not validated by the runtime.
- `native.inspect` rejected the copied payload with `native_storage_invalid`
  / checksum failure. The model reported corruption after roughly 3,100 characters
  and a truncated/invented tail. The source notebook was not changed.
- Requested marker `DEMO-020-29` was **not saved**. Do not assume it exists.
- Total attempt about 5.8 minutes. Runtime startup was seconds, so the slow,
  unreliable portion was the host/LLM data transfer rather than Python execution.

A follow-up diagnostic reported:

| Route | Observed limitation in that session |
| --- | --- |
| Claude Docs read | State appeared only as inline tool text in model context |
| Claude Docs export | Inline base64, no directly usable execution file |
| Artifact files/read | Viewer files existed, but no notebook-content file |
| MCP resources | No Claude Docs resources listed |
| Programmatic tool invocation | No available execution tool could directly call Docs |
| Google Drive download | Inline base64; did not provide a bridge for this Claude Doc |

Treat these as observations to verify, not immutable platform facts. A previously
unnoticed export, tool-composition facility, file handle, asset route or supported
native API could change the diagnosis. Do not inspect hidden browser state,
extract session cookies or invent undocumented authenticated endpoints.

Earlier small Claude notebooks saved and resumed successfully, sometimes slowly.
A fresh small ChatGPT 0.2.0 demo also saved/read back successfully on 29 October.
Neither result establishes dependable transfer of growing Claude notebooks.

## How memory currently works

The authoritative private notebook holds a single JSON state block containing
compressed/base64 state and a SHA-256 checksum. Compression is not encryption.
It includes project records, decisions, questions, preferences, consent and
submission/replay state. Project journals are readable derived views.

The host reads the complete block and retains its document revision/block hash.
The bundled Python runtime restores it in a disposable directory, executes a
request or batch and returns a candidate snapshot. The host conditionally writes
that exact candidate, reads it back, and calls `native.confirm`. A runtime result
alone does not establish persistence. The source supports native.v1 and v2,
bounded replay receipts and operation generations, guarded conflict retries and
capacity reserves. Preserve these semantics.

`--response-file` writes the complete runtime response to a private local file.
It only helps when the host can transfer that file's contents directly to a
document tool. Passing the filename to a literal-text field does not read it.
`native.batch` reduces save count, but does not solve byte transfer.

## Investigation priorities

1. Inspect available tools for an **exact bidirectional bridge**. Can document
   content reach execution as bytes without model transcription, and can a saved
   candidate reach a conditional document update the same way? Show the actual
   documented capability and receipts. A downloadable export alone solves only
   half the problem.
2. If a native route exists, prototype it with a new, clearly labelled synthetic
   notebook. Inspect privacy before creation. Keep the existing notebook intact.
3. If there is no exact bridge, compare a minimal connector-based implementation
   with bounded/chunked document transport. Do not presume chunking is sufficient:
   describe how a complete candidate becomes authoritative atomically, how partial
   writes are discarded, and how the last good version remains recoverable.
   Avoid a new multi-document protocol merely to make a single demo pass.
4. Consider durable local storage through Claude Desktop/Code as an immediate
   alternative where actual host filesystem access exists. An ephemeral cloud
   execution directory does not qualify. Do not silently relocate an existing
   user's research records or treat it as a browser-cloud fix.

Do not route private research memory through Science Works' metascience collector.
That endpoint receives optional approved contributions, not private notebooks.
If a proposed connector needs new account access or OAuth scopes, describe the
required permission and stop at that boundary; do not obtain credentials by
scraping another connector. Keep the user's chosen storage and permissions unless
they explicitly choose a change.

## Acceptance evidence

Use synthetic fixtures of increasing, measured size: small (~5 KiB), comparable
to the failing notebook, then ~50 KiB and ~150 KiB if the route supports them.
Sizes refer to the saved encoded envelope; record actual values. Do not fill
the user's existing notebook for this test.

- Exact save/readback and checksum match, including Unicode text.
- Fresh-conversation discovery and restoration using the stable notebook ID.
- A real decision/open question retained after another write and fresh restore.
- Project A/B separation and unchanged optional-sharing settings.
- Deliberately stale revision rejected, followed by safe reconciliation.
- Truncated/corrupted transfer rejected without replacing the last good notebook.
- Interrupted write/retry does not duplicate a decision or submission.
- Time spent reading, transferring, executing, saving and verifying separately.
- No claims based only on chat history or a readable derived journal.

If proposing a code change, add meaningful regression tests for the confirmed
defect and run the affected native tests. Work in an isolated branch/check-out
for experimental code; do not overwrite ongoing PR work. Report host acceptance
results separately from unit-test results. Never weaken consent, source privacy,
checksum checks, conditional writes or replay protections to pass a test.

## Handoff to return

1. The root cause and exact capabilities inspected, including any route that
   worked that the earlier diagnostic missed.
2. A test table with host/version, notebook sizes, timings, outcomes and evidence
   links. Clearly mark untested or failed cases.
3. The smallest proposed patch or prototype, its location/diff, and migration
   implications for existing 0.2.0 notebooks.
4. What works today, what still requires engineering or account permissions,
   and whether Claude web, Claude desktop and other hosts differ.

If a reliable fix is not available, say so plainly and give the best supported
fallback. Do not claim that prompt wording alone resolves exact data transfer.
