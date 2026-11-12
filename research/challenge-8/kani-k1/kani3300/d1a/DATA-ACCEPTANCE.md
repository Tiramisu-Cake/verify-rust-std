# KANI3300 D1-A — bounded data acceptance

**Scope:** offline acceptance of the two supplied D1-P bundles for run `43314208878`, attempt 1. The task file labels itself DRAFT/NOT ISSUED; this work proceeded because the coordinator explicitly issued D1-A in the active assignment. No CI, network, build, compiler, Kani, CBMC, or solver operation was performed.

## Accepted identities and artifact integrity

- **R1+skip:** source `56cbc5c4a479bc3fb25310b14fcf279d90581a02` / tree `a97ec3d06efd827829f550f1e7a98f29538758fe`; CI commit `1d0f1d30bfcf8ce64d63716a31a0a9bd3e06c7a0` / tree `702a150836245d35b257665d4c91e73314cd4511`.
- **R6-02b:** source `405c1f059264d8f7cedeeaa01c6d4ad6867a419e` / tree `162e8ad1e76e842b18c24a4ac2986335902834d7`; CI commit `86f9b171513de7a11eec7587bead1edc6877d950` / tree `6b030412a13f240cd52ceaabc97b6987be613be5`.
- Per-bundle `identity.json` matches the expected pins and job labels. Each 10-file allowlist and overlay SHA/byte map matches the D1-P `DIAGNOSTIC-MANIFEST.json`; that manifest records byte-identical overlay copies and unchanged production trees. Both fixtures match pinned SHA256: legal `fe05e646b2ccc9188d073b78b30abecd59eb877b6298abfcdfc8a27aeb3a260b`, hole `61fc369a6830c6ff185887b04db36139ca529e4de097c0025ce7b29c8323f759`.
- Every listed file in each local `ARTIFACT-MANIFEST.json` was checked for exact byte count and SHA256: **129/129 pass per bundle**, no missing or mismatched entries. `INPUTS.json` includes every manifest path/hash, all receipt hashes, snapshot hashes, argv, tool identities, and bounded coverage fields.

## What was captured

For both P1 legal-root bundles, records include actual Kani argv with `--program-only`, actual CBMC argv, resolved CBMC and `goto-instrument` paths/version/SHA256 (CBMC 6.11.0), and separate pre-DFCC, post-DFCC, and actual-CBMC GOTO snapshots. Actual CBMC input is explicitly SHA-bound separately from post-DFCC; the receipt says intervening driver transformations occurred, so equality is not presumed. Four `goto-instrument` invocations are recorded per root, including exactly one `--dfcc` invocation; all invocation boundaries are complete. Pre/post/actual stock views and their bounded receipts are available.

Per-root status says setup, artifact capture, DFCC, stock views, and symex-only completed; last completed phase is symex-only. The top-level `workflow-status.json` separately marks the overall capture stage `failure` and upload `PENDING`, consistent with incomplete diagnostic completion; do not treat per-root snapshot presence as end-to-end capture success. The Kani frontend process returned **101**, with `ERROR_OR_DIAGNOSTIC_PARSER_INCOMPATIBILITY`; parser and diagnostic completion are INCOMPLETE. This is a diagnostic-path/parser outcome, not a CBMC semantic verdict. Failure inventory is `NOT_RUN/UNKNOWN` (zero parsed records does not imply no failures). Normal verification is **NOT_RUN** and proof credit is **0**.

Symex-only CBMC receipts (separate from Kani frontend rc 101):

| Field | R1+skip | R6-02b |
|---|---:|---:|
| CBMC original rc / signal / limiter | 0 / none / none | 0 / none / none |
| elapsed seconds | 0.930163 | 0.886106 |
| sampled descendant-sum RSS KiB | 36,556 | 39,076 |
| same sample / 1,048,576, GiB | 0.0348625 | 0.0372658 |
| wait4 maxrss KiB | 36,556 | 39,364 |
| stdout bytes / dropped | 1,656,636 / 0 | 1,886,396 / 0 |

Both have 60-second / 2,097,152-KiB limits, 0.05-second sampling, owned process-group cleanup, complete stdout/stderr, and no truncation at the 8-MiB stream cap. `time_v_maxrss_kib` is null. These are completed symex-only measurements; no Boolean conversion or completed proof peak is measured, and sampled descendant sums may double-count shared pages. They cannot replace historical interrupted-proof maxima or establish resource equivalence.

The initial per-root parser summaries were incomplete. The D1-A offline census (`analyze_offline.py`) covers the full bounded printed stream: R1+skip has 5,280 printed expression records (4,213 ignored, 1,067 retained, 2,039 guard lines, 96 ASSERT, 33 ASSUME); R6-02b has 5,865 (4,588 ignored, 1,277 retained, 1,961 guard lines, 115 ASSERT, 41 ASSUME). This census still covers only printed `--program-only` output, not full converter input/workload; it does not fill VCC/auxiliary category, exact widths, owner, or source binding gaps. The diagnostic stream also reports `saturating_add/sub: not enough arguments, inserting nondeterministic value` on both pins and `assume(false)` at R6-02b `load_argument`. Treat the printed stream as useful attributed diagnostic evidence while keeping semantic correctness/faithfulness UNKNOWN, especially for the R6 path. Counts are acceptance metadata, not proof or a substitute for the separate D1-A SSA analysis.

## Gaps and disposition

Local Git resolves research `cedd1a7b5fd99c27baf9d9c07180ecaea5b92b97` and trigger `8a4664fe1d3587c8ce17790ac2d818cdb169cd25`. The trigger tree has exactly one workflow, `kani3300-d1p.yml`, with a push event and explicit checkout refs for the two CI commits above; no workflow_dispatch input lookup remains. It is a trigger-only tree; its workflow deletions are not present in the checked-out model trees. Run→trigger association is accepted from the coordinator handoff, not independently checked via Actions API. These are Actions artifacts, not a Cloud Build UUID: the Cloud Evidence Brief interface does not bind this numeric run ID. The preserved `workflow-status.json` says upload `PENDING`; local manifests prove the supplied bundle integrity, not final remote upload state.

Data is sufficient for later bounded inspection of captured projections, but not for a complete semantic comparison or proof claim. No causal/source-to-GOTO binding, retained converter workload, complete failure inventory, actual solver outcome, or proof credit follows from these artifacts. Keep both roots separate; R6-02b is a frame-failure contrast, not a correct PFC baseline. Continue only with the already captured bounded data, and record unproven links as UNKNOWN.
