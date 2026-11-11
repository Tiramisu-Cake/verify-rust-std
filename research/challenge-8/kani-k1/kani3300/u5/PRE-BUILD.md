# KANI3300 U5 — PRE-BUILD packet

PREPARED; Cloud NOT_RUN, proof credit NONE. Runtime Codex, one diagnostic stage.
Task: `research/challenge-8/kani-k1/TASK-KANI3300-U5.md`; planner answer points 3–5 read.
Worktree `/root/verify-rust-std-kani3300-u5`; branch `experiment/kani-k1-kani3300u5-20261111`.
Stage `kani3300-u5`, owner `k1-merge`; request `kani3300-u5-uninit-20261111-01`.
Baseline `e962c304c15664b23f17e834ce92ca3c5eb4ebef` includes coordinator U5 task, from U4B `6931d0d24ba232a0760d20d23c8b0a3331ec33de`.
Library-only commit `39f032ee6877fdcf7c9ba2b20ea2938ebc54976f`.

Only two proof roots and their strict `<` comparator/count helpers appended to `uninit_probe.rs`.
All existing 11 roots are byte-identical; every other library file unchanged.
Both new roots call `<u64 as StableSmallSortTypeImpl>::small_sort` directly, using a function item
`less_u64` (no fn-pointer coercion), N4, `[MaybeUninit::<u64>::uninit(); 20]`, unwind17 and the existing panic stub.
Both assert sortedness and equal counts for an arbitrary u64 probe before the post-sort slot observation.

Static route: `shared/mod.rs` implements `FreezeMarker` for `T: Freeze`; u64 has no interior mutability.
The Freeze specialization of Stable entry (`smallsort.rs:51–64`) calls `small_sort_general_with_scratch`.
N4 satisfies scratch length 4+16, skips the sort8/sort4 branches and sets presorted_len=1.
Copies seed scratch[0] and scratch[2]; the two insertion loops extend these to [0,2) and [2,4).
The merge reads those four initialized elements and writes back to v. On normal return scratch[4] is untouched.
This is source analysis; independent compiled MIR/call-site binding remains UNKNOWN until separately established.

All root names share `slice::sort::shared::smallsort::verify::uninit_probe::`:

| Row / root | Expected | Manual accounting after Build |
|---|---|---|
| B1 `stable_small_sort_scratch_written_slot_u64_n4` | SUCCESS | 0 failed checks, no uninit/Unsupported/other failures; sortedness/count, normal return and before/after scratch[3] covers (3) |
| B2 `stable_small_sort_scratch_unwritten_slot_only_u64_n4` | FAILED; `Reading from an uninitialized` | Only scratch[4] read; require uninit u64, record every failure type/location; classify any pointer failure separately; covers (4) |
| B3/U8 `small_sort_general_with_scratch_u8_n4` | SUCCESS | Unchanged sortedness/count and normal-return cover (1) |
| B4/U1 `pincheck_calibration_uninit_read_u8` | FAILED; `Reading from an uninitialized` | Unchanged calibration; all failures/locations and covers (3) |
| B5/U2 `pincheck_calibration_init_read_u8` | SUCCESS | Unchanged initialized-byte calibration; value assertion and covers (3) |

B6 omitted: the mandatory five-root package already includes a negative control for the new u64 width.
Do not prescribe an exact B2 failure count. The substring gate alone cannot establish target payload/type
or causality; inspect all Failed Checks and reject unrelated failures. Covers after intentional UB give no credit.
B1 must pass. Missing runtime detail remains UNKNOWN, without weakening expectations or retrying.

Root request equals its snapshot; SHA256 `5c21d21c3dc53a0d5d716d2ebf290287fa24c1fc8f9842b8187cf91abc23e6a3`.
Production CMP2 patch unchanged: `kani3300/u4/kani-uninit.patch`, SHA256
`46ad585f769143200634e2c2ddf3c16e4b5f33955985791c0962ac446cf354e4`.
Kani pin `f046b70644e113be0df9c22c2e6ea44a65a57566`, nightly-2026-10-23;
protected lane paths equal KT2 `3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`.
Expected production-only applied tree `d356238999ab436ddc1dd7ffa845b0db214aa53e` from U4/U4B metadata;
U5 observed applied tree, actual argv and all runtime checks remain NOT_RUN/UNKNOWN.

One attempt, no retries: diagnostic, standard4/jobs1, 3m per harness, controls/uninit on, inventory off.
Envelope `(5 × 3 + 30) = 45min`; planned reserve `$0.6075` <= stage cap `$0.80`.
U5 spend/reservation `$0`; no phase registration, dispatch or watcher during preparation.
Read-only project ledger snapshot: 283 builds, used `$114.9900`, unfinished reserve `$0`, cap `$118.96`;
this package fits the observed remaining `$3.9700`. Snapshot is not a reservation; recheck slots/budget at dispatch.
Stop after publishing the exact final packet SHA. Dispatch requires coordinator exact-packet PRE-BUILD review/GO.
After GO only: `research/challenge-8/kani-k1/tools/k1g.sh dispatch experiment/kani-k1-kani3300u5-20261111`,
then task-mandated `k1g.sh watch BUILD` and end turn. Current thread cwd `/root`; no generic session watcher armed.

After terminal Build: Brief first, bounded `k1g.sh summary BUILD` and `summary BUILD 0 5`, status,
budget and `check-tooling BUILD 3bb5445d2ac46b4ae6dedf30e835a81b3a44f44c`.
Check exact Build head/request/patch/pin/tooling/tree, all five rows, failed/total and covers.
Preserve every failure type/location and all evidence limitations; no raw logs/archives/credentials.
Update `RESULT-KANI3300-U5.md` (<=25 lines) with actual statuses, failures, covers, scope/caveats and cost.
Report only source-reported bounded diagnostics, normal returns with this panic stub, type/length/comparator/patch.
Pointer cause and independent MIR binding stay open unless established; no general compound/native acceptance,
Challenge 8 completion, or independent B1/B2 proof credit from these harnesses or the summary gate.

Static checks PASS (`static-check.json`): prior roots preserved, exact selectors/settings, unchanged tooling/patch,
generated args and controls. Existing validator accepted five roots; rustfmt wrapper applied; whitespace clean.
No runner changes requiring new service tests. No local cargo/rustc/Kani/CBMC execution.
Independent review receipt follows separately; packet validation and review do not authorize dispatch.

Independent Luna HIGH review PASS, no blocking findings: `INDEPENDENT-REVIEW.md`.
Reviewed semantic candidate `be8bd0d11d75d6bc3898bb1d3429b7d03fe8f61b`;
post-review delta contains only canonical review spec, review receipt and packet/checkpoint review metadata.
No runtime results or proof credit; no dispatch authorization. Coordinator reviews exact final published SHA.
