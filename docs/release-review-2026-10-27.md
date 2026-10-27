# Review preparation — 27 October 2026

This is a review build, version 0.1.1. Neither repository is merged or deployed by
this preparation. All endpoint tests use synthetic records and isolated storage.
The paper, workshop evaluation and graph output directories are outside the PR.

## Review map

The Benchside PR includes the existing session-stamping commit from Rory's PR #4,
preserving its authorship. Coordinate that dependency before merging. The new
client and receiver changes are reviewed together against the same JSON contracts.

| Area examined | Checks and boundary |
| --- | --- |
| Consent and exact submission | Off by default; separate grants; draft digest and destination checked at send time; withdrawal/regrant invalidates approvals; verified receipt required; retries retain approved bytes. |
| Data separation | Original workflow-observation format preserved. Feedback and activity omit installation/project/session IDs. Usage has its own random installation ID and optional categorical demographics. Reports combine aggregates without joining participants across channels. Free text still requires human review. |
| Native memory | Allowlisted files, bounded decompression, checksums, stable project identity, atomic private batches, operation replay, project isolation and guarded host writes/readback. No network actions or approval steps in batches. |
| Metascience | Separate invitation/analysis/sharing choices, selected accessible sources, fixed bounded weekly sample, categorical outputs and evidence labels, no inferred scientific outcomes, empty public study catalog. |
| Receiver and deployment | Strict per-route validation, capped UTF-8 bodies, separate storage bindings, outcome-only logging, unchanged original gaps contract, separate staging buckets and rate-limit namespace. No public collected-data read route. |
| Packaging | Version 0.1.1 across wheel and manifests; bundled hashed dependencies; offline bootstrap; all seven compiled role definitions; no journal or credentials in the package. |

This records code review and executable checks performed in this working session;
it is not an independent reviewer approval or a scientific validation study.

## Verification

- All 215 Python tests passed on Python 3.11 and Python 3.14.
- Lint, all seven compiled-role checks, Codex/portable manifest, Claude manifest
  and shared skill validation passed.
- All three 0.1.1 archives passed extracted-runtime checks: all seven roles across
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

## Host and release gates

The [23 October report](acceptance-2026-10-23.md) remains the evidence for installed
native memory and scientific-role tests. Both installed apps still need the
0.1.1 upload; automated Chrome uploads report unavailable file-URL access.
The versioned ZIPs are in `dist/` and will also be produced by the PR's build job.

Claude's Google connector is now connected with the user's approved specific-file
scope only. Account-wide Drive read access was left off. The installed-app Google
capability/continuity checks are recorded separately when they finish; connector
connection alone is not proof of a safe shared notebook.

Before outreach:

1. Complete installation and the final reproducibility wording retest in both apps.
2. Verify the exact Google route offered to users, including file selection,
   complete reads, private access, conditional writes, readback and resumption.
   Keep unsupported routes out of the supported-path claim.
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
