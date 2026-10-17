# ADMIN-AUDIT-REQUEST — 57ea65a3-475e-4370-810c-19ad36803174

Status: request prepared; **no administrative raw-audit authorization is implied**.
Owner: select-sort4. Previous checkpoint:874932e8. No new Build/compiler/verifier,
IAM changes, account reopening, historical pin/verdict/ledger or proof-credit edits.

## Exact subject and integrity anchors

- BUILD_UUID: `57ea65a3-475e-4370-810c-19ad36803174`.
- Project/region: `smallsort-ci` / `global`.
- Infra/proof: `9678ddf631902765d7013f5ed1b9fd05159463a6`.
- Submitted config SHA256: `8e604a149bd62249b83c1a71dc625cbe4fc04a955a34d4cb0602d32b2e237715`.
- Archive URI: `gs://smallsort-ci-evidence-504462351565/cloud-build/57ea65a3-475e-4370-810c-19ad36803174/evidence.tar.gz`.
- Expected archive SHA256: `02901f734338f175e9969c47fe59c35d369e75e2150308b06495ba6acc2e6c0f`.
- Processing receipt: processor0.3.0 / VERIFIED_ARCHIVE_AND_INVENTORY;
  report bucket `smallsort-agent-reports-504462351565`.
- Index: `derived/v1/57ea65a3-475e-4370-810c-19ad36803174/evidence-index.json`,
  SHA256 `30fd8b8b7885e34fc446040be8c1b0bb0c4f2934ebb5f18c8db0be4aa5ee854b`.
- Brief: same derived directory, `agent-brief.md`,
  SHA256 `54b9f0abcdd981e950c63656cf7d61d21db1b4a3f95d3aee4b11107c938bf153`.
- Reader-delivered report copies and their hashes: [diagnostic.json](diagnostic.json),
  [index](evidence-index.json), [receipt](processing-receipt.json).

## Known facts; do not assume the merge defect

Cloud API: execute SUCCESS, package-upload SUCCESS, verdict FAILURE/exit1.
Index source claims: run_exit0, evidence_complete=true, missing_mandatory=[],
verification_accepted=false, diagnostic_complete=false. Derived cases=[] and
aggregates={} do not establish absence in original archived records. Index names
`proof-audit.json`. Source's generic `tool_profile.scope="no proof tools executed"`
is a static packaging label for this lane, not an execution observation.
Pinned provider.py SHA256 is `771970340f4fa928063cfa25db451535eb60ee1b246ef63c3cda4689842be616`;
there is no established stale-provider-pin failure for this Build.

## Requested extraction only

Return **one UTF-8 administrative diagnostic, at most16384 bytes total**, including
all text, references and hashes. No attachments, full logs, raw archives, full MIR,
ASTs or case evidence to the ordinary agent. Quote **at most30 raw context lines
total**, across all sources, around the first relevant error. Do not return
credentials or tokens. This request does not authorize new execution.

1. Identify the **first causally linked error that prevented mandatory A1
   completion**, separating observed error, source-classifier claim and your
   causal inference. An intended synthetic/negative failure or the final
   `verdict` exit1 is not by itself the upstream cause. If the causal chain is
   insufficient, say UNKNOWN and identify the missing datum; do not guess.
2. Give the failed command's recorded argv/cwd, stage/case ID and actual exit
   status, or explicitly state that the failure is an in-process exception /
   classifier refusal with no subprocess exit. Trace the command/status to its
   stage record/exit file; do not reconstruct or rerun it. Include no more than
   the30 context lines above.
3. State the last **directly confirmed** stage and its observation/status, plus
   the next stage's started/not-started/unknown state. Distinguish terminal
   wrapper success from body/conformance completion, receipt issuance and caller
   execution. For P1 and false31, name only stage markers actually present.
4. Give presence/count/schema/key-name/provenance information for original cases,
   aggregates and stage markers. In particular, determine whether A1's own
   `case_status`/`observed_rows` records exist but are absent from the derived
   index. Do not infer absence from empty index arrays. Report missing original
   records as such; do not manufacture a26-row verdict or formal credit.
5. For every returned factual finding include a verifiable source reference:
   bucket/object URI and generation when available, archive member path,
   JSON pointer or line range, and **full source/member SHA256** checked against
   the archived inventory. Include the administrative result's SHA256 as an
   out-of-band checksum if feasible, without exceeding16KiB of result content.
   Preserve the expected archive/config/proof/infra identity chain above.

Prioritize these exact archive members, reading only what is necessary under a
separate administrative authorization:

- `proof-audit.json` (index-reported actual audit path): extract only the error /
  first_blocker / first_causal_stage / run_error fields relevant to items1–4.
- `allprooflogs/cases/sort4-c1-current-recovery/diagnostic-audit.json` and
  `allprooflogs/cases/sort4-c1-current-recovery/a1-lifecycle-progress.json`:
  relevant execution_events, case_status/observed_rows **presence/provenance**,
  and last confirmed marker; avoid dumping observations or all row payloads.
- The same case prefix's `a1-tool/reconstruction-receipt.json`,
  `a1-tool/R-only-native-reference-receipt.json`, `a1-tool/*-stage.json`,
  `stage-progress.json`, and relevant nested `*-stage.json`: establish the
  actual failed/reached stage and command/exit, not mere file existence.
- `allprooflogs/sort4-c1-current-recovery-exit-code.txt` and the relevant nested
  stage exit files; only the implicated stage log's bounded context if needed.
- `manifest.json`/`files-sha256.json`: integrity and original member presence;
  compare `manifest.proof_audit` with the indexed audit to locate projection loss.

Expected A1 flow for orientation only, not execution evidence: base lane setup →
A1 tool reconstruction/R-only+C builds → own source/export/refinement/focused
observations and P1 → matrix classifiers/admission. N-false31 separately requires
its own default+Freeze threshold body/conformance → own receipt → caller and
len32/threshold32 boundary observation. Do not substitute positive-pair receipts.

## Purpose of the bounded result

Choose the smallest justified source fix and targeted checks for a future,
separately authorized Build. Do not relax gates, update pins to observed bytes
without explaining provenance, reinterpret synthetic PASS as proof, or change
historical verdicts/ledger/proof credit. Stop when the requested causal diagnosis
is established or demonstrably unavailable within this bounded result.
