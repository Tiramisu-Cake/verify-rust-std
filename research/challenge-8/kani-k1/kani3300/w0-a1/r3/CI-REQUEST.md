# A1-R3 — last reserve, coordinator-only request

**Preparation only.** This package authorizes no publication, trigger, CI execution,
slot or ledger update. A1 has used 2/3 dispatches per coordinator; R3 is the last reserve.
Coordinator must check the current ledger, availability, budget and review before action.
No worker push, CI, local Cargo/rustc/Kani/CBMC or raw-log reading occurred.

CI package `e3e9f138b77d81ae7f75d3a6ec910e9c27eb3a8e`, tree
`483b25c43c2a4c44f8107b33cdd764b027cc6d1f`, parent
`bf81a1f14f9468c5b25d3ee33f7dafbf2bca131e`; local branch/worktree in PACKAGE.json.
Std fix `312ff625b9b3338281d899cca47d72c24d5a2539`, tree
`44bf49c77a2f5157bc051002dfd8b162f36bc649`, library
`54c4873f693f1d420a5ac505660ab460c8aa1f96`. Runtime std base stays
`70ba5befc617627073738e26cb1466bd4fb76e41`; the embedded combined test-only patch
has the corrected trait import. No P′ rebase, compiler change or checker weakening.

Executable CI-REQUEST.json here is byte-identical to the committed control copy.
After review, only the coordinator may publish exact local packages and create a
same-tree non-skip child of the skip-CI package on `uninit-ci/ch8-w0-a1-r3-*`.
No trigger was created. Push is the mechanism; workflow_dispatch and retries are absent.

| Job | Proposed execution | Maximum envelope |
| --- | --- | --- |
| r1 | Frozen SEL1; eight std rows serially in one job, N32 stable/general/network first | 130 runner-min: ≤39min setup, 8×600s invocations, ≥10min upload reserve |
| r2 baseline | Only #5151 original then initialized companion, native standalone | 50 runner-min: ≤19min setup, 2×600s, ≥10min upload reserve |
| r2 SEL1 | Same two fixtures and edition2021 environment on frozen SEL1 | Same 50 runner-min |

Total proposed upper envelope **230 runner-min**, one R3 workflow dispatch, no retries.
The two native jobs retain max-parallel1. Job names r1/r2 identify adapters within
this single R3 workflow; they are not new R1/R2 dispatch requests. The six original
R2 row definitions remain bound in JSON, but `r3.native_row_ids` executes only #5151.
No OFF companion, pin sweep, #4854 reset change or rerun is included.

All std row argv/environment specifications equal the old R1 request, including
uninit ON, exact selection, jobs1, object-bits12, no-assert-contracts and unwind34.
Per invocation group cap remains600s; stdout/stderr each32MiB; metadata16MiB/job;
upload256MiB/job; RSS reserve2GiB frozen before setup; TERM→5s→KILL unchanged.
The longer single std job replaces eight matrix jobs to share fail-fast state.

On confirmed nonzero core(lib) compilation failure, later std rows get explicit
NOT_RUN receipts referring to the predecessor. Timeout, missing/incomplete results,
source drift and resource/runner failures stop separately with UNKNOWN evidence.
A missing export alone is never called a compile failure. Original exits, signals,
exception records and snapshot evidence survive aggregation. Complete noncompile
failures keep their failure code while independent rows can finish; no retry occurs.

Four protected diagnostics per invocation: stdout/stderr head/tail, each≤64KiB,
captured before metadata bounding. Excerpt hashes/counts are recorded by execute.
Target directories are excluded from evidence accounting/upload and removed before
upload; the upload path also excludes `**/target/**`. Missing evidence remains
incomplete even when excerpts survive. Receipts, bounded excerpts, fallback and
upload retain always() handling and seven-day retention.

After future CI, inspect bounded first diagnostics and exact identities before
attributing the original8652 errors or accepting any row. #5151 candidate SUCCESS
on the negative remains MISSED_CHECK/STOP; its legal companion must succeed.
Empty Drop/source bytes are preserved. Compile success and exit0 do not grant
SmallSort body/caller/control acceptance or independently established B1/B2 credit.
