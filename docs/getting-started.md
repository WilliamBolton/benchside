# Getting started with Benchside

Benchside offers seven research colleagues: a supervisor, study-design consultant,
methods troubleshooter, results discussant, reproducibility auditor, journal-club
discussant and scientific peer reviewer.

## Choose an installation route

Benchside is one research toolkit with several delivery methods. “App package”
means the installable bundle, not a separate Benchside chat app or a replacement
for the Git/terminal route. A plugin packages skills and their supporting runtime.

| Route | Current implementation |
|---|---|
| Clone GitHub and ask an agent to set it up | Install source dependencies and run guided setup. The installed skill remembers the runtime so later chats work outside the checkout. No model-specific backend is needed. |
| Codex or another local agent | `bench setup --agent codex` or `--agent generic --skills-dir <host directory>` installs the shared seven-role skill. The agent runs setup for the researcher. |
| Terminal / Claude Code | Shared skill through `bench setup --agent claude` or `bench init`; explicit `bench init --legacy-cli` provides legacy role commands and local session hooks. |
| OpenAI plugin | `benchside-plugin-0.1.2.zip` includes the portable manifest, Codex compatibility manifest, setup entry and bundled skill/runtime. |
| Claude plugin | `benchside-claude-plugin-0.1.2.zip` includes `.claude-plugin/plugin.json`, the shared skill, role references and runtime. The manifest passes Claude's validator. |
| Claude standalone skill | `benchside-claude-0.1.2.zip` remains available for custom-skill installation. |

The expanded implementation is in [draft PR #5](https://github.com/science-works/benchside/pull/5).
Published main does not yet contain these changes. No public plugin listing has been published.
Package validation does not replace installation, discovery and fresh-chat memory
checks in the intended app/account.

Install the Benchside package supplied for your app, then say:

> Set up Benchside for this research project.

Benchside guides you through choosing a project and checking that its records
will remain available. Then describe the scientific work you want help with:

> My extraction yield has fallen. Help me work out what to check next.

> Help me decide what these results actually support.

> Review the scientific claims and methods in this draft.

When you return to the same project, ask Benchside to continue. It recalls
recorded decisions, unresolved questions and open discussions. You can switch
roles as the work changes.

Setup asks where you want your records stored and shows accessible choices:

- A durable folder on this computer, outside Git. The choice is remembered for
  other agents on the same OS account. Claude and Codex can select the same project.
- A private Benchside Space/collection in your app. The notebook is restored on
  each conversation; the execution sandbox is disposable.
- A private location in an installed cloud connector, if its tools support
  complete reads, conditional updates and readback. Google Drive and Google Cloud
  Storage are different services; setup checks the connector actually available.

For existing records, setup lists projects and reuses the one you choose. It never
merges projects by title, copies records elsewhere, or changes their sharing settings.
Choosing an existing project restores its decisions and open discussions; choosing
new starts a separate project journal. All roles remain available in either case. Setup
reuses the current project when it is already clear.
Two apps can use the same cloud notebook if both can access that location and
safely update it. Separate Claude/OpenAI accounts are not automatically connected.
A folder synchronized between two computers is not a substitute for coordinated
cloud writes; filesystem locks work on one machine, not across sync clients.

Decisions come from that chosen private store, never from the metascience receiver.
For local storage, events are in `<chosen folder>/projects/<project ID>/journal.jsonl`.
For native/connected storage, the private Benchside memory document contains the
validated records, and each project has a readable journal document. A single
private memory document can hold several isolated projects.

ChatGPT Pages and the connected Google Drive/Docs tools have passed synthetic
save/read/restore checks. Claude Docs has also passed private-document creation,
readback, guarded update and discovery by title in a fresh conversation. Google
Docs and Claude Docs rejected stale writes. The installed Claude review plugin
also passed a synthetic methods discussion, guarded saves, fresh-chat discovery
and resumption, and separation from a second project on 23 October. All sharing
stayed off. The updated runtime batches private recording to reduce repeated saves,
remembers participation deferral and displays friendly project names. It passed
live Google Docs and ChatGPT Pages save/readback checks for all seven roles. Both
installed plugins also passed batched setup and fresh-chat resumption. Claude
setup took about 7½ minutes and ChatGPT's 2m 21s in individual, non-comparable runs.
Three scientific overclaims did not recur after the installed role corrections;
the final reproducibility wording check passed in both installed 0.1.1 plugins.
Both apps passed submission-failure recovery and consent withdrawal, but HTTP 403
blocked delivery before the temporary Worker. On 27 October, ChatGPT restored and
updated the shared Google notebook. After the user approved the separate Google
Docs connector, Claude resumed that same project and saved a synthetic decision
using a guarded update. Independent readback verified both the state and journal;
Google metadata showed both documents unshared. The earlier Drive-only check did
not test this editing connector. The rebuilt 0.1.2 fixes still need installed
update acceptance; update all apps sharing a notebook together.
Claude's native Docs tools do not expose sharing permissions, so a private sharing
state must be verified in the UI. Other accounts/connectors still need acceptance.
See the [27 October release review](release-review-2026-10-27.md) and
[earlier installed-app tests](acceptance-2026-10-23.md).
If a connector only searches or reads files, setup explains why it cannot keep a
journal there and offers another available location. No Google connector or
storage credentials are bundled into Benchside.

Memory depends on the agent's tools, not its model. The runtime needs Python 3.11+
and a POSIX execution environment, plus access to the chosen storage. Ordinary
chat without execution/storage tools cannot automatically record or submit data.

For Claude plugin review, upload the Claude **plugin** ZIP in Customize → Plugins,
using the custom-plugin upload option available to your account. The standalone
**skill** ZIP goes through Customize → Skills instead. For a local Claude Code
review, the agent can load `plugins/benchside` with `--plugin-dir` after building
the package. These routes do not publish a listing or deploy any backend.
See [Claude's installation guidance](https://support.claude.com/en/articles/13837440-use-plugins-in-claude)
and [manifest reference](https://code.claude.com/docs/en/plugins-reference).

For updates, use your app's plugin replacement flow. An agent handling a manual
installation should stage the new release in a clean directory and preserve any
customizations before replacing the managed installation. Do not unzip a package
over an earlier source installation: old runtime settings and removed files can
remain active. Keep research records in their existing storage and reopen the
same project after updating.

## Optional sharing

During first setup, Benchside asks whether you would like to contribute to
Science Works' metascience research. You can choose what to contribute, keep
everything private, or decide later. The choices cover workflow observations,
usability feedback, usage counts, optional surveys and selected-conversation
analysis. For analysis, you choose the sources and separately decide whether its
workflow categories stay in your private notebook or are prepared for reviewed
sharing. Examples include "coding", "tool failure" and "checked sources".
Scientific findings and research-specific details are never eligible for
metascience submission. Free-text workflow observations and feedback must also
be generalised to remove those details before preview.

These preferences apply to the chosen Benchside store, including other apps using
it. Existing choices are kept when you return. Nothing is preselected, and setup
consent does not authorize automatic submissions.

You can independently choose to share workflow problems, usability feedback,
and usage counts with Science Works. The assistant shows the proposed content
and recipient before sending it, and you can edit or exclude items. Scientific
notes and source documents stay in your project record.

Usage reporting uses a random installation ID to estimate returning use. That
ID is absent from workflow observations and feedback. You can stop any reporting
choice at any time and ask to see previous submission receipts.

Setup also offers optional broad discipline and career-stage categories. Skip
either, keep them private, or separately choose to include them in reviewed usage
reports. They help describe participating installations; they do not change
which roles you can use. No name, institution or free-text demographic answer is
requested. These fields are absent from individual workflow observations,
feedback, survey responses and activity reports.

## Optional research studies

Ask: “Help me set up optional Benchside research studies.” You can receive
occasional surveys, privately analyse selected research conversations, or review
and share reviewed workflow categories. Each choice starts off. Wider analysis can cover
work without any Benchside role, provided your app can access the sources you
choose. You review a small batch before anything is shared; raw logs stay out of
submissions. No schedule is installed automatically. See [the details](metascience.md).

The current review build has no active survey and its new endpoints have not
been deployed. Local synthetic tests are available for developers; real use
requires the Science Works deployment and host checks described in the rollout guide.

## Developer packaging

For maintainers, build the distribution from the current source:

```bash
uv sync --frozen
uv run bench compile
uv build --wheel
uv run --with pip python scripts/build_release.py
```

This produces:

- `dist/benchside-claude-0.1.2.zip`: standalone Claude skill, with all roles.
- `dist/benchside-claude-plugin-0.1.2.zip`: Claude plugin upload, with manifest at the archive root.
- `dist/benchside-plugin-0.1.2.zip`: portable/OpenAI plugin with Codex compatibility metadata.

All packages are generated from the same code and role definitions. Claude packaging
adds its manifest and upload layout; it does not fork the implementation or create
a new endpoint. The OpenAI manifest declares the packaged onboarding skill using
[OpenAI's supported setup entry](https://developers.openai.com/plugins/build/plugins).

## One central receiving service

Every production installation—Git, terminal, Claude or OpenAI—uses the same
Science Works HTTPS API at `https://ingest.benchside.science.works`. An HTTPS API
is a secure web address that software sends requests to. Its paths separate the
kinds of approved submission: `/v1/gaps`, `/v1/feedback`, `/v1/usage`, `/v1/surveys`
and `/v1/activity`; `/v1/studies` provides the optional survey catalog.

The Cloudflare Worker is the program running behind that address. Its storage
buckets hold received submissions. The operator updates that central program once;
researchers do not deploy a backend or need a Cloudflare account. The companion
collector code implements the new routes, but its production update remains pending.

Staging means a separate testing copy of the service and storage, so synthetic
submissions cannot mix with real study data. Only development/test runs point at
staging. Normal packages retain the production address. Your chosen private
journal location is independent of this service and is never uploaded wholesale.

To test without cloud access, the agent/developer can run:

```bash
uv run --frozen python scripts/test_endpoints.py
```

This starts an isolated local copy of the receiving program, sends synthetic data
to all five submission routes, checks receipts/duplicate handling and rejected
requests, then removes the test storage. It requires the companion collector
checkout and its installed Node dependencies. No deployment or Cloudflare login
is needed. Testing the real public service additionally needs its central update
and a reachable test address; local success does not prove that deployment.

See [endpoint testing and access](endpoint-testing.md) for the temporary HTTPS
option, exact submission examples, and the permissions to request from Ben.
