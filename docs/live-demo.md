# Live Benchside demonstration

The presenter starts a new conversation and responds naturally. This is a
synthetic research consultation, not a replay of the acceptance-test chat.
Use the installed Benchside plugin in ChatGPT for the first rehearsal; the
existing larger Claude notebook currently fails the exact-transfer check.
The evidence and limitations are in [the live test report](live-receiver-check-2026-10-29.md).

## Starting prompt

Paste this into a new chat with Benchside selected, then send it during the demo:

> I'd like to use Benchside to plan an imaging study. This is a fictional demo;
> none of the details are real research. Start a new private project called
> “Paired imaging — live demo” in a separate demo notebook. Explain the available
> storage and optional sharing choices briefly, and let me answer them. If this
> app cannot reliably save records, tell me rather than claiming it has saved.
>
> I have six donors, with control and treatment samples from each donor. Each
> donor-condition has two wells and each well has three images, so my spreadsheet
> has 72 rows. I was going to treat those as 72 independent measurements. Does
> that make sense? Ask a useful follow-up question and take this one step at a
> time; don't complete the whole demonstration for me.

## Possible next turns

These are presenter cues, not instructions to run all steps automatically.

1. Choose a separate private demo store after its limitations are explained.
   For an initial rehearsal, leave sharing off. For the supervised send demo,
   opt into workflow-problem sharing only after its explanation; each exact
   problem still needs review. Skip demographics if desired.
2. Discuss pairing and nested measurements. A useful scientific response should
   distinguish six independent donors from 72 rows without prescribing an
   analysis before checking the design and assumptions.
3. Introduce a workflow obstacle: “In this fictional export, channel labels
   sometimes disappear. I spend about 20 minutes putting them back each week.”
   Do not attribute the invented defect to an actual product.
4. Say: “Let's check donor, condition and channel mapping before analysis.
   Record that decision. Keep open whether to aggregate the wells and images
   or model them hierarchically.” Wait for an actual save confirmation.
5. Optionally start a fresh chat, select the same demo store/project, and ask
   what was decided. A read from saved storage demonstrates continuity;
   repeating the decision from the previous chat does not.
6. Ask to review a workflow-problem report. The candidate should describe the
   export/relabeling friction and frequency, omit donor counts, conditions and
   research questions, and retain an explicit “SYNTHETIC DEMO — not a research
   submission” marker in allowed descriptive text.
7. Inspect the exact preview. Only then approve the synthetic submission if the
   operator has prepared the test handling below. Show the receiver receipt and
   corresponding private R2 object; a successful chat response alone is not proof.

Do not pre-authorize an unseen payload, invent a submission receipt, or set a
new `test:true` field: the live receiver enforces a strict schema.

## Showing the data flow honestly

The intended full demonstration is:

Research conversation → private saved record → reviewed problem report → HTTPS
receiver → private R2 object → analysis → reviewed report → Vercel preview.

The receiver, R2 readback and local importer have passed synthetic checks. The
GitHub-hosted import is still unmerged and intentionally limited to the default
branch. Bugbear has no Benchside report view yet. Therefore the final displayed
Vercel step is **not ready**, and should not be presented as already connected.
Keep the user's no-merge instruction in force. A later display implementation
can first be demonstrated on a Vercel preview branch without changing production.

Before a real demo send, the operator must arrange receipt registration and
test exclusion. Schedules currently remain off. Record every returned payload
hash in the test-object manifest before any research import; the existing code
does not automatically exclude arbitrary future records just because their text
says “demo”. Keep a separate, clearly labelled synthetic report for the showcase.
Never disable test exclusion in the real research report to make a demo count rise.
If this handling is not ready, stop at the approved preview and use the earlier
receipt-matched fixtures to explain the receiving/reporting components.

## Reporting structure for the first rollout

Keep raw submissions in private Cloudflare R2. Run validation and aggregation in
the private GitHub repository using its scoped read-only key. Keep the internal
analysis in short-lived private job artifacts. Commit only reviewed public-safe
report snapshots; Vercel deploys the approved code/data together. GitHub is not
the raw participant database, and no receiving or storage credential is shipped
to users or to the browser.

This fits the existing static Bugbear site and the already prepared reporting
PR. Vercel does not require data in GitHub: if frequent updates later justify it,
store approved report snapshots in Cloudflare and fetch those through a Vercel
server route. Retain an explicit review/publish step in either design.

Current analysis groups identical structured gap text; it does not perform LLM
theme discovery or map problems into Bugbear tool tiles. Those are later analysis
and display tasks. A problem report is not automatically a vote to rebuild a
tool. Keep source-specific report counts and participating-store counts distinct
from Bugbear's existing hackathon scientist/demand counts.

Useful optional problem context includes the public tool/dataset name, relevant
version, generic task, frequency, practical impact, workaround and desired
improvement. Most can already be described in permitted fields. Dedicated new
fields require coordinated schema changes, not extra keys in a current payload.
Do not collect unpublished findings, detailed protocols or sample identifiers
to fill the Bugbear page. Its tool mapping and hardware alternatives can be
curated after collection.
