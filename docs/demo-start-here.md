# Benchside colleague demo — 29 October 2026

## Install

For a colleague with a paid Claude account, give them
`benchside-claude-plugin-0.3.0.zip`. In Claude: **Customize → Plugins → Upload a
plugin**, choose the ZIP, then Upload. Open Benchside and choose Try in chat.
They do not need a terminal or API key. The package is a review build, not yet a
public directory listing. A normal chat prompt cannot silently install a plugin
into someone's account; uploading the ZIP is the explicit installation step.

For Will's ChatGPT account, Benchside is already installed and the private plugin
has been updated to 0.3.0. Select Benchside in a new conversation. This private
plugin URL is not a public installation link for colleagues:
https://chatgpt.com/plugins/Plugin_a5f12a7a3860819195a9308479e22ad2

If using a filesystem-capable agent such as Codex or Claude Code, an alternative
is to ask it to get the review branch from
https://github.com/WilliamBolton/benchside/tree/codex/research-roles-rollout
and follow the README's agent setup. Let it ask where the private records should
live, outside Git. Do not direct colleagues to main for these unmerged features.
This source route depends on the host's filesystem and command tools; it is not
an installation method supported by every browser chat.

## Before presenting

For today's most dependable live walkthrough, use **Codex with a new local demo
folder outside Git**. Benchside 0.3.0 is already available in Will's Codex account;
invoke Benchside in a fresh conversation and use the prompts below. Codex handles
the runtime commands; the presenter does not need to type terminal commands.
Normal host permissions still apply when writing the chosen folder or sending.

Use only invented research and a separate demo store. Claude's larger cloud
notebooks still have an unresolved exact-transfer problem. Prefer a durable
local folder in a desktop agent if available, or Will's small ChatGPT notebook
route. Inline-copy cloud storage is experimental and must be explained. If a
save fails, call it unsaved; do not pretend a chat transcript proves persistence.

The host needs permission to reach `https://ingest.benchside.science.works` for
an approved send. If network access is disabled, leave the preview pending;
never claim that it reached Cloudflare or weaken host settings automatically.
This is separate from installing the plugin. No storage/admin credentials go
into a colleague's plugin.

Status checked at 13:44 UK time, 29 October: the Claude 0.3.0 runtime works, but
its network setting remains off and its live sending check is blocked. Its
larger cloud-memory transfer is unresolved. Do not present the full Claude
browser experience as verified. The standalone local client → receiver → GitHub
route has passed a synthetic rehearsal; a fresh installed-app walkthrough is
still a live demonstration, not a guarantee every host has the same permissions.

Open the waiting GitHub run in the presenter's account:
https://github.com/LauraRyanSW/tools-science-works/actions/runs/40906605042
It waits until **19:00 UK time today**, ends after the first matching submission,
and shows the result after refreshing the page. Colleagues need repository
access to open the private report themselves, but the presenter can show it.

## Paste this first

I'd like to use Benchside for a fictional imaging study. None of this is real
research. Help me set up a new separate private demo project, briefly explain
the available storage and optional sharing choices, and let me choose.

I have six donors, with control and treatment samples from each. Each condition
has two wells and each well has three images, giving 72 rows. I was planning to
treat those as 72 independent measurements. Does that make sense? Ask one useful
follow-up and take this a step at a time, rather than completing the demo for me.

## Introduce this problem later

Another fictional issue: DemoScope version 1.4 sometimes drops channel labels
when I export images. I spend about 20 minutes restoring them manually each week.
I'd like the export to preserve those labels. Please record the workflow problem.
When we review it for sharing, start its task description with this exact test
marker: SYNTHETIC-DEMO-d653ecd34c032c939fd2e8c8:
Only this invented problem should go into the demo submission.

## Natural next steps

- Discuss pairing/nesting and agree on a sensible next step.
- Say “Record our decision to check donor, condition and channel mapping before
  analysis; keep open whether to aggregate wells/images or model them.” Wait for
  a verified save, if the chosen storage supports one.
- Opt into problem sharing after its explanation. Leave other channels off for
  this short demo. Ask to see the proposed problem report.
- Check the marker, version, workaround and impact. The report should omit donor
  counts, scientific questions and sample details. Approve only after reading it.
- When the receipt arrives, refresh the waiting GitHub run. It should show the
  new problem within roughly 15–30 seconds, subject to network/runner availability.
  There is no receipt-copying step. If no matching report appears, check that the
  exact marker starts the primary gap text and that the send actually succeeded.

## What the audience is seeing

Research discussion → private records → reviewed workflow problem → receiving
API → private Cloudflare bucket → automatic GitHub summary and downloadable report.
The Vercel view is later work. The updated reporting PR computes summary counts
and retains each complete submitted problem separately, without summarising its
wording or combining matching descriptions. Related problems are not yet grouped
by an LLM. Optional context is retained privately; public-ready reporting remains
aggregate only. The already-running demo was started on the previous revision,
which displays exact-description groups; a fresh run after review uses individual
records. Both retain the full wording and context of the single demo problem.

[Successful automatic rehearsal](https://github.com/LauraRyanSW/tools-science-works/actions/runs/40877962796)
provides a fallback example, clearly labelled as an earlier synthetic test.
