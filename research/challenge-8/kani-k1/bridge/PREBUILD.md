# BRIDGE B1 — PRE-BUILD REVIEW

State: **WAITING_FOR_COORDINATOR_GO**. No build submitted; all six rows NOT_RUN.
Base `2dde801cf428de600e3786ebcc2b4c16a3f03be6` (task additions over `7f558e061a`).
Library commit `b07dc219a27af35e9832335c129bb8759926b7ca`, tree
`f3bf04b5ccf83592e98c1d536d21713e7c01363a`. Branch `experiment/kani-k1-bridge-20261101`.
Pin `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12; cap $88.96.

## Patch and composition

Only new `verify/bridge.rs` and one `mod bridge;` registration after existing modules.
The file has inner `#![cfg(kani_smallsort_controls)]`; its entire content is opt-in.
`merge` precedes `bridge`, so the profile target precedes the new leaf PFC in crate order.
`frame_target` precedes both A3 PFCs. Production bodies/signatures, profiles and tools unchanged.

`bidirectional_merge<T,F>` -> `adapter<T: FreezeMarker + MergeBridge<F>,F: FnMut>` ->
sole impl `MergeBridge<fn(&u8,&u8)->bool> for u8` -> `merge_profile::<LtU8>(v,dst,*is_less)`.
No transmute, blanket impl, specialization, alternate comparator, or unsupported-F proof row.
Every actual raw call in caller uses an explicitly typed local fn pointer. Function items coerce
at the caller boundary. The adapter cover is before its trait forwarding call.
The standalone leaf PFC executes `merge_length_body::<LtU8,3>` with no substitutions.
Caller harnesses have raw->adapter and verified-profile substitutions; leaf/A3 have neither.

## Caller <-> leaf domain

| Field | Exact-N3 leaf and positive caller |
|---|---|
| T / F type | u8 / `fn(&u8,&u8)->bool` (higher-ranked shared input references) |
| F value / model | `LtU8::CMP` = `lt_u8`; key `x >> 1`, model = full u8 |
| N / halves | 3 / 1+2; right pair sorted by model; leaf requires, caller assume |
| Source | separate initialized exact `[u8;3]`, offset 0, all values arbitrary |
| Destination | separate `MaybeUninit<[u8;3]>`, offset 0, exact writable 3-byte region |
| Frame | profile modifies dst[0..3) only; caller also asserts unchanged source and probe |
| Probe | `LtU8::set_probe(kani::any())` independent of source, before raw/target call |
| Properties | key sortedness, full-value count for the same probe; no comparator in oracle |

Thus there is no caller/leaf backing/init difference. Canonical/sortedness negative rows preserve
regions/type: wrong-F keeps sorted arbitrary input; unsorted uses `[any,2,0]`, right keys [1,0],
without a sortedness assume. The latter two rows must establish requires rejection at the
verified call under organizer `--no-assert-contracts`; this remains NOT_RUN until their results.

A3 is a distinct geometry: separate initialized source `[u8;3]`, right pair sorted by construction;
initialized arbitrary backing `[u8;4]`, dst offsets [0,3), sentinel offset 3 (same allocation).
Target takes sentinel raw pointer and corrupt flag; requires permit sentinel access, but modifies
only `slice(dst,3)`. It calls real raw merge with canonical fn pointer, without any substitutions.
Probe is set before target invocation. Positive flag=false; negative flag=true flips sentinel
inside target at bridge.rs:122 after the cover at :119. No out-of-bounds/invalid pointer is intended.
This pair measures enforcement on this target; it does not establish all profile frames or extend leaf.

## G1 rows and strict acceptance

Full names have prefix `slice::sort::shared::smallsort::verify::bridge::`.

| # | Harness suffix | Expected | Required evidence |
|---|---|---|---|
| 1 | bridge_leaf_u8_n3 | SUCCESS | real profile/raw body, leaf return cover |
| 2 | bridge_caller_positive_u8_n3 | SUCCESS | caller-before, adapter-entered, caller-return covers |
| 3 | bridge_caller_wrong_f_u8_n3 | FAILED | canonical requires only, specfix.rs:317 |
| 4 | bridge_caller_unsorted_u8_n3 | FAILED | sorted-halves requires only, specfix.rs:318 |
| 5 | bridge_frame_positive_u8_n3 | SUCCESS | target-call and target-return covers |
| 6 | bridge_frame_negative_u8_n3 | FAILED | assigns check for sentinel write, bridge.rs:122; write cover |

`expect_check`: row3 `specfix_canonical_comparator`, row4 `merge_halves_sorted`, row6 `is assignable`.
Row6 uses the stable suffix of the pin's generated `Check that *var_6 is assignable` diagnostic;
generated variable numbers cannot be predicted. Match alone is insufficient: inspect class,
source location and all failures; sentinel write must be the only failing assignment check.
These checks are generated requires/assigns assertions, not added substitute harness assertions.
Compile error, unsupported, timeout, unwind or unrelated checks do not count as negative controls.
The request gate is only an initial matcher; source-bound acceptance and covers need manual review.

## Static validation

`check_bridge.py` / `static-check-prebuild.json`: 15/15 checks pass. Ordinary exact 200 names
match both base and `integwrapfix/ordinary-expected.txt`; all old module content is unchanged.
Sorted static ordinary names SHA-256 `1ea7bb6585d8cff99db84a6fcd99e61a5928537817b34c92c5c4579cd610b621`.
This serialization differs from native inventory ordering; no native inventory is claimed here.
Cfg-on static forecast 382 -> 388, exact delta six bridge names, no removed names.
Request validates with lane validator; `g1.args.txt` and `g1.runner.txt` record selection.
Changed Rust files pass the mandated rustfmt wrapper `--check`, edition 2024, supplied config.
`git diff --check` passes. No local cargo/rustc/Kani/CBMC or CI runs.

## Pin feasibility and unresolved risks

Read-only pin investigation used official files (no local pin source checkout available):
[pass ordering](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-compiler/src/kani_middle/transform/mod.rs#L82),
[monomorphized replacement](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/kani-compiler/src/kani_middle/transform/stubs.rs#L41),
[stub bounds](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/docs/src/reference/experimental/stubbing.md#L231),
[assigns regression](https://github.com/model-checking/kani/blob/9461e07af7ec929f050aa4192f29363c9be07779/tests/expected/function-contract/modifies/simple_fail.expected).
User stubs run before contract instrumentation; replacement resolves original generic args.
Bounds may differ if every replaced instantiation satisfies them. These facts support the design,
but do not prove successful compile, actual summary replacement, or absence of an indirect cycle.
Cover of adapter plus exact requires failures must establish that the chain was applied.
Potential raw->adapter->profile->raw recursion remains a feasibility risk until G1 succeeds.
Stock uninit instrumentation is off; matching uninitialized destination is not an init-detector claim.

## Request, budget, next action

`RUN-REQUEST.json` = `bridge/g1.request.json`, id `bridge-g1-20261101`: diagnostic,
controls=true, jobs=1, uninit=false, 6 rows x 3 min; gcb-e2-standard-4 only.
Work envelope 18 min + 30 min overhead = 48 min, full reserve **$0.6480**.
Own submitted UUIDs: none. Own fact_spent=$0, reserved=$0; task maximum $0.75 / <=2 builds.
Project budget observation: used $73.2480, reserved $0, cap $88.96 (`budget-prebuild.txt`).
G1 would bring used+reserved to at most $73.8960. Refresh budget before dispatch after GO.
G2 only on compile error, separate coordinator GO, fact_spent + full new reserve <= $0.75.
Do not alter timeout/kind to obtain acceptance. Semantic changes require a fresh source review.
After explicit GO: dispatch this branch using k1g.sh, record UUID, then `k1g.sh watch UUID`
(with CODEX_THREAD_ID) and end the turn. Bounded K-1 summary/locations after wakeup; no raw archives.
B1 smoke is not direct-proof replacement or N16 feasibility. B2 next: actual Stable u8 N9
A real body / B bridge, same fn-pointer/probe and matching leaves; not implemented here.
