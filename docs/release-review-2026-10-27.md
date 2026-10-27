# Review preparation — 27 October 2026

This is a review build, version 0.1.2. Neither repository is merged or deployed by
this preparation. All endpoint tests use synthetic records and isolated storage.
The paper, workshop evaluation and graph output directories are outside the PR.

## Review map

The Benchside PR includes the existing session-stamping commit from Rory's PR #4,
preserving its authorship. Coordinate that dependency before merging. The new
client and receiver changes are reviewed together against the same JSON contracts.

Draft PRs: [Benchside #5](https://github.com/science-works/benchside/pull/5)
and [receiver #1](https://github.com/science-works/benchside-ingest/pull/1).

| Area examined | Checks and boundary |
| --- | --- |
| Consent and exact submission | Off by default; separate grants; draft digest and destination checked at send time; withdrawal/regrant invalidates approvals; verified receipt required; retries retain approved bytes. |
| Data separation | Original workflow-observation format preserved. Feedback and activity omit installation/project/session IDs. Usage has its own random installation ID and optional categorical demographics. Reports combine aggregates without joining participants across channels. Free text still requires human review. |
| Native memory | Allowlisted files, bounded decompression, checksums, stable project identity, atomic private batches, operation replay, project isolation and guarded host writes/readback. No network actions or approval steps in batches. |
| Metascience | Separate invitation/analysis/sharing choices, selected accessible sources, fixed bounded weekly sample, categorical outputs and evidence labels, no inferred scientific outcomes, empty public study catalog. |
| Receiver and deployment | Strict per-route validation, capped UTF-8 bodies, separate storage bindings, outcome-only logging, unchanged original gaps contract, separate staging buckets and rate-limit namespace. No public collected-data read route. |
| Packaging | Version 0.1.2 across wheel and manifests; bundled hashed dependencies; offline bootstrap; all seven compiled role definitions; no journal or credentials in the package. |

This records code review and executable checks performed in this working session;
it is not a human reviewer approval or a scientific validation study.

## Independent review and fixes

Three Codex review agents examined memory/consent, metascience/reporting and
packaging/onboarding. A separate Claude Opus review read client commit `4992880`
against base `eb9c039`; its environment blocked running PR code, so its findings
were static analysis. Local executable regressions substantiate the fixes below.
Claude could not fetch the private receiver source; do not count that as a
completed receiver review.

- Native memory bounds cached response bodies while retaining operation IDs and
  request hashes; submissions check capacity before networking, and ordinary
  writes leave room for consent withdrawal. Emergency control-history compaction
  preserves scientific records and submitted receipts. A physically full legacy
  notebook can still need larger storage; no guarantee of infinite memory is made.
- Runtime caches require trusted ownership, private directories, safe locks and
  verified contents before importing code. Cold install, reuse, tamper rejection
  and interrupted-install recovery have executable coverage.
- Reopening the same journal from another app reuses its project. Scientific
  events record the app that actually wrote them, including when a sitting is
  resumed elsewhere. Global consent/collection ledgers omit that provenance.
- Generated role instructions use the real adapter actions. Missing sessions fail
  with a resume instruction. Source installs have a durable launcher; default
  Claude setup uses the shared app entry, with legacy CLI skills explicit-only.
- Analysis withdrawal clears old selected sources. Invalid optional destinations
  do not block private work. Empty observations cannot produce an empty draft.
  Optional usage tolerates legacy/custom metadata, standardises failure counts
  and omits research text. Aggregate observations deduplicate stable IDs and
  exclude conflicting duplicates.
- Newer native records produce update guidance. **Update every app writing a
  shared notebook to 0.1.2 before continuing:** older 0.1.1 readers cannot read
  newly added provenance fields or compacted replay entries. Keep the notebook;
  do not create a replacement or discard unfamiliar records.

## Verification

- All 296 Python tests passed on Python 3.11 and Python 3.14.
- Lint, all seven compiled-role checks, Codex/portable manifest, Claude manifest
  and shared skill validation passed.
- All three rebuilt 0.1.2 archives passed extracted-runtime checks: all seven roles across
  fresh processes, native restore, batches, remembered choices, replay and
  rejection of a damaged dependency even with an existing cache.
- All 38 receiver tests passed, including a Unicode boundary check matching the
  Python client's existing UTF-16 feedback limit. Type checking passed.
- The local integration check passed all five channels: stored and duplicate
  receipts, a synthetic study invitation, three sampled activity records, rejected
  transcript content and consent withdrawal before networking. Production requests: 0.
- The staging deployment dry run built successfully and listed only the five
  separate `-staging` EU buckets. It did not create those buckets or deploy a Worker.
- The CI action tags were checked against their upstream GitHub repositories.
- Previous GitHub CI passed for both Python versions, including all three archive checks,
  on [client commit 4992880](https://github.com/WilliamBolton/benchside/actions/runs/40492728446).
  This run is on the contributor fork; the upstream PR currently has no check run.
  [Receiver CI](https://github.com/science-works/benchside-ingest/actions/runs/40492736532)
  also passed for commit 8aad0f5. These historical runs do not certify later edits.

## Installed-app Google storage check

ChatGPT's installed 0.1.0 plugin restored the existing private synthetic Google
notebook in a fresh conversation, continued the same project and methods sitting,
and saved a new decision in one guarded batch. The notebook advanced from revision
8 to 9. The readable journal was updated and read back. An independent connector
read and runtime restore verified the digest, decision, project identity and
remembered participation deferral. No submission endpoints were called.

The earlier Claude check exercised **Google Drive only**, with specific-file
access. It did not test the separate Google Docs connector and must not be used
to claim that Claude cannot edit Google Docs. Anthropic documents the separate
connector for document edits. On 27 October the user explicitly approved its
broader Google Docs scope. The installed Claude 0.1.1 plugin then read both complete
documents, restored the same project and methods sitting, and saved the requested
synthetic decision. The notebook advanced from revision 9 to 10. `update_doc`
used the exact old state text plus Google's required revision; the journal used
its own revision guard. Full readback and `native.confirm` succeeded. A deliberately
invalid revision was rejected; this test did not separately exercise a stale
revision of the same document.

An independent Google connector read and local runtime restore confirmed revision
10, the checksum, the new decision and its readable-journal entry. Earlier
decisions and deferred participation remain. Independent metadata showed both
documents `shared:false`, with only owner permission. Claude's Docs connector
itself did not expose sharing metadata. No unrelated documents, sharing settings
or collection endpoints were used. This establishes cross-app continuity for
these accounts and connectors, not every Google integration. The connector's
literal-text update requires the model to carry the state payload; checksum and
readback validation remain essential.

Sources: [Anthropic Workspace connectors](https://support.claude.com/en/articles/10166901-use-google-workspace-connectors),
[Google Docs scope](https://developers.google.com/workspace/docs/api/auth).

## Installed 0.1.1 update checks

Both app UIs showed version 0.1.1. Each test verified the loaded runtime and the
bundled wheel SHA-256 `0e774f9de94c81b26496ac83b8138f991ca0ffea991ece968838fdf46cfc117a`.
Claude restored BATCH-O3 in its existing sitting and advanced the notebook from
revision 11 to 12. ChatGPT restored GPT-O3 in its existing sitting and advanced
revision 8 to 9. Both guarded writes passed full readback and `native.confirm`.
Decisions, unresolved questions, other projects, deferred participation, empty
demographics and disabled sharing were preserved. Neither test called a collector.

Both response-only reproducibility checks distinguished the user's unsupplied
README claim from inspected evidence; neither claimed to have read or run it.
Claude also discovered a read-only false revision change. A local reproduction
confirmed that comparing recompressed bytes misidentifies a different valid zlib
representation as changed state. Version 0.1.2 compares decoded state and preserves
the original envelope for unchanged reads, replay and rollback.

These are installed **0.1.1** results; they do not establish installed 0.1.2 behavior.

## Host and release gates

The [23 October report](acceptance-2026-10-23.md) remains the evidence for the
broader seven-role installed tests. The new 0.1.2 ZIPs contain review fixes and need
a further installed update check. Package validation alone is not app installation.

Cloudflare access checks confirmed an active token and a successful signed HEAD
request to the existing EU `benchside-gaps` bucket. Bucket-management requests were
not authorized, and Worker-edit permission is unconfirmed. The signed-in dashboard
shows only Will's own new account, not the Science Works account. API-token access
does not establish dashboard membership. The original production gaps receiver
already exists; separate staging storage is still needed for synthetic testing of
the new routes. No production objects were read or written.

Before outreach:

1. Install the 0.1.2 review update and repeat native resumption in both apps.
2. Repeat shared Google memory after both installed apps are updated to 0.1.2;
   preserve the successful 0.1.1 continuity result as separate evidence.
3. Provision Science Works staging after access is granted, deploy the receiver
   there and obtain real receipts from Claude and ChatGPT. Diagnose any gateway
   or edge HTTP 403 without weakening unrelated network protections.
4. Exercise preview/approval, retry and withdrawal against staging; verify stored
   objects and produce a report from those synthetic exports.
5. Review the PRs with Will before merging and releasing. Public survey definitions
   and their data-handling commitments need review before activating any study.

Remaining limits: Claude setup latency, broader scientific quality evaluation,
host-dependent sharing metadata and eventual native-notebook archival. Nothing
here establishes cross-account automatic synchronization or background access to
all research conversations.
