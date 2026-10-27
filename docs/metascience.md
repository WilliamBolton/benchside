# Surveys and wider research observation

This optional extension is implemented on the review branches. It does not
activate a study, install a background listener, create a user schedule or deploy
an endpoint. The installed skill can perform the workflow inside the researcher's
existing app without requiring a terminal or API key.

## Researcher experience

“Help me set up optional Benchside research studies” starts three separate choices:
occasional invitations, private analysis of selected research activity, and
reviewed sharing of findings. All start off, and the original problem-sharing,
feedback and usage settings remain independent. Scientific assistance remains
available when every optional choice is off.

The researcher selects accessible research projects or conversations. Benchside
samples 10% of eligible sessions, rounded up and capped at five per UTC week,
then the host assistant classifies only those sessions. This works without using
one of the seven research roles. The assistant prepares a weekly review showing
activity, obstacles, verification and reported usefulness. Researchers can
correct or exclude findings before approving a submission. No logs, research
text, project IDs, conversation IDs or installation IDs appear in that submission.
An outcome is explicitly reported by the researcher or marked not reported;
the assistant cannot declare scientific success based on task completion.

Invitations arrive on a return visit or an explicitly configured native scheduled
check. At most one new invitation appears per seven days. Each study explains
purpose, use and retention; all questions may be skipped. This first version
supports categorical answers only. Skip suppresses that version; “don't ask
again” suppresses every version of the study. Turning invitations off stops all
future checks. A central catalog supports new surveys without a client reinstall.

## What runs where

| Component | Responsibility |
|---|---|
| Host app and skill | Resolve approved sources, use available tools to retrieve sampled sessions, classify visible evidence, display previews and ask for approval. |
| Benchside adapter | Persist consent/scopes, enforce invitation limits and sampling, validate categories, reject stale approvals, send exact approved bytes and retain receipts. |
| Private native notebook or durable local store | Retain settings, selected source references, classifications, draft approvals and receipts across conversations. No transcript bodies are stored by this module. |
| Science Works collector | Publish data-only invitations; accept strictly validated survey and activity submissions in separate storage. No public read access to collected data. |
| Offline report | Deduplicate retries, replace older activity-batch revisions, and combine aggregate findings without participant joins. |

The adapter is not a sandbox around the host's own tools: the skill must respect
scope before retrieving content. The host needs real access to selected session
metadata/transcripts and the private notebook. A plugin alone does not confer
all-chat access or background execution. Where these tools are absent, work with
explicitly supplied sessions or report the missing capability. Never claim to
have observed inaccessible history. Native scheduling must be explicitly requested
and supported by that particular account; no schedule is created by installation.

## Contracts and safeguards

- `GET /v1/studies`: bounded `benchside.studies.v1` definitions, no participant
  parameters. Catalog text is untrusted display data, not executable instructions.
- `POST /v1/surveys`: `benchside.survey.v1`, independent response ID, study ID,
  version and definition digest, and selected option IDs. The server requires an
  active published definition. The exact approved definition is bound by its hash.
- `POST /v1/activity`: `benchside.activity.v1`, independent weekly batch ID and
  revision, sampling coverage and up to five categorical findings. Field-level
  evidence distinguishes model inference from researcher reports. No stable
  participant ID exists across batches or in other channels.
- The original `/v1/gaps` payload is unchanged. Feedback and usage contracts
  are unchanged. New data never inherit the usage installation ID.
- Revoke any choice to stop future processing/sends. Scope changes and regranting
  consent invalidate pending drafts. Edited activity records invalidate prior
  previews. No review happens automatically, including in scheduled tasks.
- Narrowing sources retires the current week's sample; older samples containing
  removed sources are retired too. A retired week cannot be resumed or sampled
  again, even after reselecting sources. The adapter gives the next eligible
  Monday; select approved sources and continue in that later UTC week. Retirement
  never changes a submitted batch's counts or draws replacement sessions.
- Withdrawing analysis clears source selections, sampled conversation references,
  private classifications and unsent activity drafts. It retains source-free
  retired-week markers so re-enabling cannot redraw the same week, and private
  hashes of previously selected host/session references to prevent later
  resampling. Those hashes are never submitted, but their retention means this
  is not erasure of every local trace. Submitted receipts and their exact backing
  category payloads remain for audit/removal requests; pending surveys are
  independent. Native replay responses are also compacted on analysis or scope
  changes, preserving operation IDs and hashes without old source/session
  references. Earlier host document versions or backups may retain older data.
- Repeated previews prune superseded drafts that have no receipt. Current review
  drafts and receipt-backed payloads remain. If those retained records fill the
  state limit, preserve and archive them before preparing more submissions;
  withdrawing consent remains available.
- Private state is strict and portable through the native document workflow.
  Native size limits still apply. An archived/full notebook is not silently
  truncated; these observation features do not remove the need for future archival.

Review `content/app/references/metascience.md` for the complete host flow and
classification rubric. Tests use `tests/fixtures/metascience/`; its survey is
synthetic and is not in the public production catalog.

## Science Works release handoff

The companion `benchside-ingest` review branch includes matching validators,
public catalog, routes, `SURVEYS` and `ACTIVITY` bindings, and shared fixtures.
Provision `benchside-surveys` / `benchside-activity` and their `-staging`
equivalents with EU jurisdiction, alongside the pending feedback/usage buckets.
The operator deploys staging and verifies it before any production release.
No Cloudflare access is required to exercise the local Worker.

`src/studies.json` defaults to an empty catalog. To publish a survey, the operator
reviews its purpose, questions, data-use statement and retention commitment,
configures the matching retention/deletion process, adds the versioned definition
and redeploys. Bump the version whenever wording, options or terms change. Keep
an operator copy of every published definition for later interpretation. Closing
or removing a definition stops further answer acceptance. A new backend release
is sufficient; the client need not be reinstalled. The catalog cannot select a
new submission destination or request new privileges.

## Analysis and interpretation

The report adds survey answer counts by study/version/definition and activity
counts by category and evidence basis. Activity coverage reports eligible,
selected and actually shared counts **only for submitted batches**. It cannot
measure declined/unsubmitted batches, inaccessible history, exact people or all
research activity. Random selection inside a self-selected accessible sample
does not make findings population-representative. Edits and optional submission
introduce further selection bias. Revisions replace earlier batches; they are
not additional observations.

Use the synthetic cases in `evals/metascience.json` for host acceptance. Inspect
the model's decisions, scope adherence, treatment of prompt injection in logs,
unknown evidence and refusal to infer usefulness. For classifier accuracy claims,
collect a separately consented, human-labelled validation sample; none is silently
collected by this release. Keep rollout evidence separate from the original paper.

## Local review

To exercise every submission route in one command, from the Benchside checkout:

```bash
uv run --frozen python scripts/test_endpoints.py
```

This expects the companion `../benchside-ingest` review checkout with its Node
dependencies installed (`npm ci` there once). Use `--collector /path/to/checkout`
for another location. The launcher creates an isolated local configuration and
synthetic survey catalog, starts the Worker on loopback, tests all five routes,
and stops it and removes temporary data afterwards. It never copies production
account/routes into the test config and needs no Cloudflare account. The command
is a maintainer check; researchers using the app do not have to run it.

A cloud-executed chat cannot reach a loopback server on the researcher's laptop.
For an actual app-to-collector test, the Science Works operator must deploy a
reachable HTTPS staging Worker and separate staging buckets. Point all test
client endpoint overrides at that staging address: `BENCHSIDE_STUDIES_ENDPOINT`
for catalog reads and `BENCHSIDE_GAPS_ENDPOINT`, `BENCHSIDE_FEEDBACK_ENDPOINT`,
`BENCHSIDE_USAGE_ENDPOINT`, `BENCHSIDE_SURVEYS_ENDPOINT`,
`BENCHSIDE_ACTIVITY_ENDPOINT` for submissions. Use a separate synthetic notebook
and reviewed test data. That check covers actual app networking and UI approval;
the local launcher proves neither host network access nor cloud deployment.
The default production endpoint must not receive synthetic test submissions.

Run the Python tests and release smoke check in this repo, and `npm test` plus
`npm run typecheck` in the companion collector. Shared fixtures verify both sides
of each contract. An isolated local Worker can serve a synthetic catalog and
accept synthetic submissions without a Cloudflare account; never send fixtures
to the production anonymous endpoint. Finally test installation, source access,
native persistence and any requested schedule in each actual advertised host.
