# Claude memory and sending: what was tested, 29 October 2026

All tests used fake (synthetic) notebooks and new test docs. The ACCEPT-20261028-A
notebook was not touched. No reports were sent. No settings were changed.

## 1. Saving the notebook to a Claude Doc

**Problem.** Claude saved the notebook by copying its encoded text through the
chat by hand. On 29 October this corrupted a ~5 KB notebook, and the save failed.

**Fix.** Claude Docs can move the notebook as a file, so Claude never copies it:

- **Read:** export the doc tab to a file attached to the doc, then download it.
- **Write:** upload the new notebook file, then replace the doc's notebook block
  from that upload. The usual "only if unchanged since my read" guard still applies.

| Where | Size | Result | Time |
| --- | --- | --- | --- |
| Claude Code (desktop) | 5.5 KB | Exact; saved and read back correctly | — |
| Claude Code (desktop) | 50 KB | Exact; three saves in a row | 7.9 s per full save and check |
| claude.ai in the browser (cloud) | 0.3 KB and 52 KB | Exact; saved and read back correctly | about 50 s; most of it was gaps between steps |
| Either | 150 KB | **Refused by Claude Docs: 65,536 characters max per block** | — |

Also checked in Claude Code:

- a stale save was refused;
- a retry did not duplicate records;
- a corrupted copy was rejected and the last good version restored;
- a fresh agent found and restored the notebook from its ID;
- projects A and B stayed separate.

Caveat: the "replace from an upload" step works but is not in Anthropic's Docs
guide. If it ever stops working, the save is refused and nothing is lost.

## 2. Sending reports

- claude.ai has no "approve this one connection" option. Code network access is
  one switch: Settings → Capabilities → **Allow network egress**. It is off on
  this account (Max plan).
- While it is off, the page shows only the on/off switch, so a single-domain
  option could not be checked. Anthropic only documents a domain allowlist for
  Team/Enterprise owners.
- Claude Code can reach Science Works directly (read-only check: 200 OK).
- When the network is blocked, Benchside already kept the report unsent and
  pending. Its message said "retry", which does not help.

## Changes on this branch (`claude/egress-denial-guidance`)

1. **Blocked-network message** (`http_sink.py`, all apps): now says nothing was
   sent, the report is still pending, and network access to
   `ingest.benchside.science.works` must be allowed first. The wording stays
   general because the cause may be an app setting or a university firewall.
   Error codes are unchanged.
2. **Claude instructions** (`native-memory.md`, `sharing.md`, `app-api.md`):
   - use the file route for Claude Docs;
   - pass Claude's size limit;
   - if sending is blocked, explain the Claude network switch.

   The ChatGPT sections are unchanged.
3. **Optional size limit** (`native.py`): requests can include
   `document_limit_bytes`, and the Claude instructions pass 65,536. Without it,
   behaviour is identical (ChatGPT and others keep 190,000). With it, a Claude
   notebook holds about 48 KB of normal records. The last 16 KB is kept free so
   sharing choices can always be switched off. Past that, the notebook is kept
   and the researcher is told to archive it or use local storage.

Tests: 5 new; the full suite passes (481). The committed plugin copy
(`plugins/benchside/.../references`) was regenerated to match.

## Still open

- The plugin in Claude Code is still 0.2.0. It updates when the Claude desktop
  app restarts. claude.ai already has 0.3.0.
- Notebooks larger than ~48 KB in Claude Docs need local storage or archiving.
- Four synthetic test docs can be deleted.
