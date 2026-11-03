# COVERCOST PRE-BUILD REVIEW — G1 (cover-free positive, diagnostic)

Status: WAITING FOR COORDINATOR GO (revision 2 after review dce6fab10d). No Build submitted; compile/run NOT_RUN. Diagnostic, no proof credit.
Runtime: Claude Code, executor alone (no subagents). Task: TASK-COVERCOST.md (commit 50eba374db).
Review SHA = the published research commit carrying this packet.
Branch experiment/kani-k1-covercost-20261103; base 5737fa738bac360f19dd0113b2b8640f16bea5f5 (terminal U64-TEN-CALLER).
Base library tree 514c6f841cf2af3b27f6d9aa8f27c86e24c562af (= U64-TEN-CALLER reviewed G1/G2 tree).
New library commit 8b986b9775c7de2fea81cdef6c29e7f15ea4c755, tree 67f41939ab06ef0391b241a376e1b8ef335b6433
(38225ba387 clone + review dce6fab10d fix: one `#[allow(unused_variables, unused_assignments)]` on the clone).
Stable owner k1-merge. Request covercost-g1-positive-nocover-u64-n10-20261103,
SHA256 d47b9fa263fec78dbf51f4d296b234bf5902ad2d480868b65c88f740145c51b6; RUN-REQUEST.json byte-equal g1.request.json.
Files: library.diff, root-clone.diff, static_check.py/static-check.json, g1.request.json, g1.args,
tooling-static.txt, rustfmt-check.txt, budget-prebuild.txt, runs.json, snapshot.json.
No competitor PR code/branches/diffs opened; ROUTESAB/k1-network/U64-TEN-CALLER ledgers untouched.

## Placement (least invasive)

Appended at the end of `verify/network/u64nine/tenleaves/caller.rs` (3 comment lines + the clone root).
static_check: the new caller.rs starts with the exact base bytes (SHA256 9f434dae…, = U64-TEN-CALLER
child), so the original root, the 3 controls, every helper/adapter and all line numbers (incl. G2
expect_check literals :111/:172/:339) are unchanged. A child file was rejected: it needs a `mod` line in
caller.rs plus re-pathed stub annotations, and its name would be `caller::<child>::…`, not the required
`caller::u64tencall_positive_nocover_u64_n10`. A shared-body helper was rejected: it would change the
original root. So the body is duplicated. Only library file changed: caller.rs (+40 lines).

## Byte diff original root -> clone (root-clone.diff, zero context)

Kani annotations byte-identical (6 lines: proof, stub swap_if_less->swap_adapter_u64ten, stub_verified
swap_u64_net9, stub insert_tail->insert_adapter_u64ten, stub_verified insert_tail_profile, unwind(25)).
Diff = one added lint attribute `#[allow(unused_variables, unused_assignments)]` (directly after
`#[kani::unwind(25)]`, before `fn`; the only `#[allow(` in caller.rs; not a kani attribute) + fn name
line (`u64tencall_positive_u64_n10` -> `u64tencall_positive_nocover_u64_n10`) + 9 removed
`kani::cover(...)` statements (1 after check_final + 8 after the predicate block; 15 source lines).
Everything else identical and in the same order: `v: [u64;10]=any`, `pre=v`, `probe: u64=any`,
`cmp=StrictU64::CMP`, `run_u64ten` (register, actual `<u64 as UnstableSmallSortTypeImpl>::small_sort`,
canonical cmp, check_context: 25 swaps/1 insert/frames), `check_final_u64ten` (sorted10, count10).
The root body itself has no kani::assert; all asserts are in the shared, unchanged helpers/adapters.
The cover-predicate locals (loop: descending/duplicate/tail_min; hits10, hits9, ctx) are kept
verbatim and are now unread (pure, side-effect-free; no assert depends on them). Review dce6fab10d:
their new unused_variables/unused_assignments warnings are silenced by the single allow attribute on
the clone only (no compile-repair margin in the cap). The 3-line header comment is unchanged
(its "nothing else differs" refers to the body; the allow line is the one annotation addition).

## Remaining reachable covers: 0

Child: kani::cover only in root bodies — positive 9, swap ctl 1, insert ctl 1, count ctl 2, clone 0
(13 total, none in helpers/adapters). Name-level closure from the clone over caller.rs, tenleaves.rs,
u64nine.rs, network.rs, merge.rs, specfix.rs incl. contract attributes: 39 reachable helper fns
(static-check.json `reachable_helpers`: run/register/check_* /adapters/closed impls, swap_u64_net9 +
region9_u64/canonical/count9_u64, insert_tail_profile + tail_len/tail_region/model_*/swap_*/pair_models/
specfix_canonical_comparator, sorted10_u64, count_matching_values, Profile methods), 0 covers; plus
strict_less (identity_profile! arg) 0 covers, identity_profile! macro 0, smallsort.rs and ub_checks.rs 0.
The 38 cover-carrying non-root fns (listed, incl. the same-name one) are not reached; the same-name case
`u64nine.rs::exchange` (SwapBridgeU64Nine, via adapter_u64nine, not reached) is excluded since the
clone's `T::exchange`/`T::insert` resolve to the closed U64Ten impls in caller.rs.
stub_verified replaces both targets by contracts; their bodies (raw helpers) do not run in this root.

## Invariance, inventory, identities

All dependencies byte-identical to U64-TEN-CALLER (static-check.json dependency_sha256 vs
u64tencall/static-check.json): smallsort.rs, network.rs, u64nine.rs, tenleaves.rs, merge.rs, specfix.rs,
ub_checks.rs, run-kani.sh, kani-version.toml, rust-toolchain.toml. Lane paths equal 30f77e85;
tooling-static.txt 6 bound hashes equal U64-TEN-CALLER. Kani 9461e07af7ec929f050aa4192f29363c9be07779 /
nightly-2026-10-12. Static source inventory (this branch): ordinary exact 200 = ordinary-expected.txt
(unchanged; the root is under the inherited kani_smallsort_controls gate), cfg-on 405 -> 406, exact
delta = `…::tenleaves::caller::u64tencall_positive_nocover_u64_n10`; pfc_order ordinary 21 bad 0
(unchanged); proof_for_contract occurrences 33 at base and head; no contract/requires/assume added.
The task's ordinary 202 / PFC 36 are the Part1-v6 figures, not computable on this branch; they are
untouched because no ordinary or PFC item changes. Static forecast, not native inventory.
rustfmt wrapper --check and git diff --check PASS.

## Package G1 (one Build)

| Row (…::verify::network::u64nine::tenleaves::caller::) | Kind | Expect | Covers |
|---|---|---|---|
| u64tencall_positive_nocover_u64_n10 | diagnostic | SUCCESS | 0 |

agent k1-merge, gcb-e2-standard-4 -> k1-standard4 (4 vCPU/16 GiB, swap off, $0.0135/min), kani_jobs 1,
uninit_checks false, controls true, harness_timeout_minutes 10. Validator (frozen kani_k1.py) accepted
1 row; args `--harness <row> --exact --harness-timeout 10m --jobs=1 --output-format=terse`, RUSTFLAGS
`--cfg kani_smallsort_controls`, runner gcb-e2-standard-4. Diagnostic kind check vs 30f77e85
kani_k1.py: diagnostic+controls is allowed on standard4 (controls only gated by runner); the ≥1-cover
rule applies only to `measurement` with controls (kani_k1.py:1455-1465); diagnostic gate =
COMPLETE + expectation_met (gate_ok). Diagnostic uses the same `selected` run path (time -v + 2 s
sampler, peaks.txt) as measurement (gcb-k1.sh:154-194). Same flags as U64-TEN-CALLER G1 except kind.
Gate (diagnostic): row SUCCESS, Kani exit 0. Measured: status/VT, driver/CBMC/process-sum peaks, wall,
driver growth vs time, dmesg OOM. OOM/TIMEOUT is a valid diagnostic outcome (no retry).

## Budget and slots

Ledger 2026-11-03T10:20:37Z: builds186, used$83.0895, unfinished reserve$2.0250, cap$88.96.
G1 reserve (10+30)*$0.0135 = $0.540 <= own cap $0.60; +project = $85.6545 <= $88.96.
k1-merge currently busy with PERMPROBE (Build 87487311…): dispatch only after it is terminal and
accounted (<=1 unfinished on k1-merge, <=2 project). Compile-error repair only with new review/GO and
own spent + reserve <= $0.60. Own spent0/reserved0, no UUIDs. Refresh ledger/slots after GO.
No local cargo/rustc/Kani/CBMC, Actions dispatch or deployment before GO.
