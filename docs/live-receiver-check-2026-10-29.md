# Live receiver check — 29 October 2026

The production receiver now runs source commit
`e21bedecb93b7506ea5ca688329d4cb0bf2009c6` from
[receiver PR #1](https://github.com/science-works/benchside-ingest/pull/1).
No PR was merged. Cloudflare's active deployment is `2df7e827`.

The existing domain, five EU bucket bindings and rate limits were retained.
This enables the 0.2.0 linked gap, feedback, survey and activity formats,
including researcher-entered survey text. The live catalog is empty again;
no research study is currently offered.

## Results

- Receiver tests: 63 passed; TypeScript check passed.
- Live HTTPS checks: 26 passed. Each of the five channels accepted one synthetic
  record and returned a matching SHA-256 receipt. The actual 0.2.0 Python client
  retried every payload and verified the original receipt with duplicate status.
- All five collection routes refused public reads.
- Invalid contributor IDs, raw transcript fields, changed study definitions,
  overlong answers, malformed JSON, invalid UTF-8, wrong content types and
  oversized requests were rejected.
- A temporary synthetic survey offered one choice question and one text question.
  Its answer was: “TEST ONLY: Fiji channel labels need manual restoration.
  Synthetic example, not a participant report.”
- After removing the temporary catalog, the actual client fetched zero invitations
  and further submissions to that synthetic study were rejected (HTTP 422).
- Reporting tests: 19 passed after adding the five new payload hashes to the
  exclusion manifest in [reporting PR #1](https://github.com/LauraRyanSW/tools-science-works/pull/1).
  Twelve registered synthetic payloads are now excluded. No stored object was deleted.

Successful verified receipts establish that the receiver accepted and acknowledged
storage of the exact submitted bytes. Independent R2 readback through the new
reporting connection remains pending the read-only credential approval; it is not
claimed as completed by these HTTP tests.

## Deployment evidence

The compiled source was copied into the Cloudflare editor and compared with the
prepared bundle before deployment. The temporary test deployment was `7071025e`;
the final deployment removes only the synthetic catalog.

- Final bundle SHA-256:
  `9cf85e73dbe784c7a7d3330a4f1f6208d3de50b6cbddc87e36ebd2c921d89170`
- Test bundle SHA-256:
  `c1c9619ffcb47758a6908d8749b84fa1c67981a77e69bc6dc71b7c3c4cbd72c0`
- Local evidence: `/private/tmp/benchside-live-020-20261029/test-register.json`
  contains every accepted payload hash, receipt, object key and check result.
  The synthetic sent bodies and compiled bundles are in the same directory.

## Remaining before wider use

1. Complete the Claude 0.2.0 upload and installed-app upgrade check. The upload
   page is open for the user; it still shows no selected file.
2. Approve a dedicated read-only key for the five Benchside buckets, save it as
   encrypted Actions secrets in the private reporting repository, and test the
   live import/readback. No new key was created in this pass.
3. Review and approve the outstanding PRs before merging/releasing. Reporting
   automation remains disabled, and the Vercel display is still future work.

An internal demonstration can use synthetic projects with sharing off. Claude
native notebook saving has previously taken about twelve minutes; this pass did
not establish an improvement. The OpenAI package remains private, not a public
Science Works directory listing.
