# TRAITPFC G3 — exact pre-build packet

Worktree `/root/verify-rust-std-kani-traitpfc`; branch `experiment/kani-k1-traitpfc-20261110`.
Stable owner `k1-merge`; slug `traitpfc`; stage `traitpfc-g3`; request `traitpfc-g3-20261110-01`.
PRE-BUILD review pending. No dispatch, no T0, no proof or native inventory yet.
The final `PRE-BUILD REVIEW <sha>` marker binds the exact pushed packet, including this request.
Library commit `aa0859448612246d0c52e1c59f844e777c8ad3b6`, library tree
`b6f050a21d2781fcc95a8f7e02bf9154affa560a`; other identities and SHA256: `identities.json`.
G2 baseline `3a16a173b0`; tooling base `9b1758ab817af005e96fd52a5fc940d4b6acf984`.
Kani `f046b70644e113be0df9c22c2e6ea44a65a57566`, nightly-2026-10-23, unchanged.

## Model and literal contract

One cfg(kani) model, compiled with controls off. No `PairModel` remains in the library.
Exact model declarations (the fully initialized snapshot is Copy):

```rust
pub(crate) type U64Cmp = fn(&u64, &u64) -> bool;
pub(crate) fn canonical_less_u64(a: &u64, b: &u64) -> bool;
pub(crate) enum SortEntry { Stable, Unstable, Freeze }
pub(crate) struct SortSnapshot { len: usize, valid: bool, vals: [u64; 3] }
pub(crate) trait SortModel<T, F> {
    fn enabled(entry: SortEntry, cmp: &F, len: usize) -> bool;
    fn snapshot(base: *const T, len: usize) -> SortSnapshot;
    fn sort_postcondition(pre: SortSnapshot, base: *const T, len: usize) -> bool;
}
```

Blanket default: enabled=false, snapshot={len:0, valid:false, vals:[0;3]}, checker=true;
no dereference and no invocation of F. Specialization only `SortModel<u64, U64Cmp> for ()`.
Each entry separately whitelists lengths 2 and 3, AND the exact canonical comparator address.
A canonical function item does not select the fn-pointer specialization; reverse pointer is disabled.
All six proposed entry/length pairs have ordinary PFCs in this packet; none is credited before PASS.
A5/A6 require successful matching A3/A4 real-body leaves, respectively, including covers and frame.

Native old captures the pre-call enabled Boolean and Copy snapshot. No ghost fallback, new requires,
old reference, nondeterminism in old/ensures, callback execution, or scratch read. Unsupported length
returns invalid without reading any element; no truncation. The specialized checker obtains one
post-snapshot; it requires valid snapshots and equal length in 2..=3, and uses pure u64 `<=` order.
N2 uses the exact pair permutation disjunction; N3 counts every live pre-value in both live prefixes.
Padding never participates. Equal-length count equality preserves all multiplicities of full u64s.
`contracts.json` holds the complete exact attribute strings and preserved G1 requires/modifies.
The T1 attribute below is literal; T2/T3 differ only by entry `Unstable`/`Freeze`:

```rust
    #[cfg_attr(kani, crate::kani::ensures(|_|
        !old(<() as verify::trait_model::SortModel<T, F>>::enabled(
            verify::trait_model::SortEntry::Stable, is_less, v.len(),
        )) || <() as verify::trait_model::SortModel<T, F>>::sort_postcondition(
            old(<() as verify::trait_model::SortModel<T, F>>::snapshot(v.as_ptr(), v.len())),
            v.as_ptr(), v.len(),
        )
    ))]
```

Only these three ensures change in smallsort.rs versus G2; G1 requires/modifies stay byte-identical.
Runtime bodies, signatures, bounds, inline/default, feature gates and SmallSort impls stay unchanged.
Callback write sets remain restricted: no arbitrary external writes, and no generic F proof claim.
Native old Copy-struct acceptance and Rust/Kani resolution remain build hypotheses.

## Exact rows and expected evidence

`expected-rows.json`: full names, types, layouts, unwind, dependency edges, expected covers,
and designated assertion/message coordinates and file hashes. All 14 rows currently NOT_RUN.

| Row | Root suffix (trait_contracts unless qualified) | Expect | Covers |
|---|---|---|---:|
| A1 | stable_sorts_permutation_u64_len2; direct T1 N2, scratch18 | SUCCESS | 5 |
| A2 | stable_sorts_permutation_u64_len3; direct T1 N3, scratch19 | SUCCESS | 5 |
| A3 | freeze_sorts_permutation_u64_backing4; direct T3 N2 | SUCCESS | 5 |
| A4 | freeze_sorts_permutation_u64_backing5; direct T3 N3 | SUCCESS | 5 |
| A5 | unstable_sorts_permutation_u64_backing4; PFC T2 with T3 stub; needs A3 | SUCCESS | 5 |
| A6 | unstable_sorts_permutation_u64_backing5; PFC T2 with T3 stub; needs A4 | SUCCESS | 5 |
| C1 | verified_forwarding_sorts_permutation_u64_backing5; real T2, T3 stub; needs A4/A6 | SUCCESS | 5 |
| K1 | rejects_high_bit_corruption_u64_len3 | FAILED, exactly 1 | 0 |
| K2 | rejects_changed_multiplicities_u64_len3 | FAILED, exactly 1 | 0 |
| K3 | rejects_reverse_pointer_sorted_u64_backing5 | FAILED, exactly 1 | 0 |
| K4 | rejects_function_item_sorted_u64_backing5; needs W1 for frame branch | FAILED, exactly 1 | 0 |
| W1 | freeze_frame_function_item_u64_backing5; real T3, same function item as K4 | SUCCESS | 3 |
| R1 | scratch_geometry::stable_u64_min_scratch_n2, unchanged | SUCCESS | 2 |
| R2 | forwarding_contracts::unstable_byte_n2, unchanged | SUCCESS | 7 |

A1-A6/C1 use unconstrained `kani::any()` inputs, an explicit canonical `U64Cmp`, assert enabled
and cover enabled before the call. They save strict ascending, strict descending and any-duplicate
predicates before the call, and cover those plus normal return after it: five required covers each.
T1 has separate N+16 scratch; all T2/T3/C1 slices are backing[N+2][1..N+1], checking both exterior
values. C1 asserts enabled for both entries, saves independent typed pre/post arrays, and checks
order and per-pre-value multiplicities without using the model after the call.
New model/consumer loops have at most three live iterations. T1 uses two chunks of length at most
two plus a merge of at most three; T3 uses one network-region iteration and insertion at N2/N3.
Unwind32 is unchanged from the pilot; R1 unwind34 and R2 unwind16 remain unchanged.

K1 first sorts an arbitrary triple with three compare/swaps (no assumptions), snapshots it, and
asserts the unchanged snapshot passes. It XORs bit63 of one live value, then repeats the same checker.
Its sole failed check must be `high-bit corruption preserves sorted full values`.
K2 uses pre=[a,a,b], post=[a,b,b], with its only new assume a<b in this negative fixture.
Its sole failed check must be `same set preserves full multiplicities`.
K3 asserts reverse pointer disables the model; its sole failure is `reverse pointer output is sorted`.
K4 asserts the function-item model is disabled; its sole failure is `function item output is sorted`.
K3/K4 use T3 stub through real T2 and retain exterior checks. W1 is the exact F/N3/backing5 real-body
frame PFC for K4, not a U64Cmp proof. The common control comparator/cover helper bodies are preserved.
No previous G1/G2 research root is copied into the new ordinary or opt-in set.
Require full failed/total counts, full failed check messages/locations, all reachable covers and
verified T3 stub-binding diagnostics. An expected status/substr alone cannot establish acceptance.

## Manifests, static preservation, and PR applicability

Ordinary 235 -> 242 (exact seven A/C additions). cfg-on 260 -> 260:
old 235+13+12 pilot roots -> final 242+13+5 calibrations. Full sorted lists are regenerated.
`check_traitpfc_g3.py` reuses the RENAMEMODS lexer/expander and checks all inherited 248 root
closures, bodies, attributes and domains unchanged, including R1/R2 and the 13 prior controls.
It freezes all other verify files, enforces the four-file library allowlist and exact core
ensures-only delta against G2. Tooling/pin/gates equal 9b1758ab81; rustfmt --check has zero diff;
no new Rust line >100, three inherited smallsort comments preserved.
Static checks do not establish compiler resolution, native inventory or formal proof.

Library patch versus 9b1758ab81 is saved as `library.patch`. `apply-check.json` records successful
`git apply --check` on detached submitted head 872d5a4338 in the prescribed scratchpad worktree;
that temporary worktree was removed by its literal absolute path. No submitted branch was changed.
The library patch is separate from research artifacts and contains no stage names in new code/docs.

Native cfg-off inventory is required in this SAME build: exact 242 names and same library tree.
Frozen runner gcb-k1.sh:128-138 runs list before exporting controls at line166. The cloudbuild yaml
has no RUSTFLAGS environment. List uses function-contracts, mem-predicates, float-lib, c-ffi,
loop-contracts, quantifiers and stubbing; list has no no-assert-contracts option. Verification runs
controls-on with organizer no-assert-contracts and object-bits12, jobs1/standard4, timeout5m;
uninit/value-validity checks remain off. Attribute actual flags as in G2: runtime diagnostics
when emitted plus source-bound runner configuration, explicitly noting un-emitted list argv.
Do not mistake a source manifest for compiler evidence; missing/controls-on inventory blocks PASS.

## Timing, money, and execution boundary

Frozen dispatch formula: 14*5+30 = 100 paid minutes ($1.3500), not 120.
Frozen runner verification cutoff: 14*5+24 = 94 minutes after validation.
Planning allocation: setup/pinned build12 + cfg-off inventory49 =61; available after inventory33.
Within those 33m: controls-on compile plus rows23, remaining slack10; summary/upload6 =>100 paid.
This uses the unchanged runner's observed inventory estimate and short N2 evidence; it does NOT
provide seventy full row-minutes after inventory. A 60m inventory would leave22m after setup12.
Compilation, inventory and solver durations are uncertain: preserve partial/TIMEOUT/OOM results,
never retry to obtain a pass or change frozen tooling. New loop bounds do not imply runtime bounds.

Own cap $3.50; spent $0; Build1 reserve $1.3500; maximum Build2 reserve $1.3500;
two-build maximum $2.7000, leaving $0.8000. Build2 has at most these same 14 rows.
Project observed used $110.1570, unfinished reserve $0; cap $118.96; headroom $8.8030.
With both worst-case builds: used+reserved $112.8570, headroom $6.1030. See prebuild-budget.txt.
This is planning/accounting, not a live reservation or dispatch permission; refresh before dispatch.
Window main360 + closeout30 minutes; T0 begins only at exact-packet coordinator GO.
Two paid timeouts total200 minutes fit inside main360, leaving160 for review/analysis/dispatch.

Before EACH build: exact-packet PRE-BUILD review/GO and bound SHA/library/request/tooling/budget.
After Build1 recompute actual spent/project residual and freeze a concrete Build2 plan:
(1) syntax/attribute qualification/native old Copy-form repair on identical rows, OR
(2) final narrowing only for TIMEOUT/OOM, never both. At most two builds, no retry/third build,
new domain/type, ghost protocol, new assumption/panic cut, or disabling unwind assertions.
Unexpected ordinary FAILED requires classification (counterexample/spec/model-trust/unsupported)
and a coordinator decision; it cannot silently become a resource-open length exception.
Composed SUCCESS without a successful matching real-body leaf never receives proof credit.
Narrowing removes unconfirmed entry lengths and their positive roots from the final library;
this published research SHA preserves the attempted package. C1/K3/K4/W1 must match the accepted
T3/T2 domain. K1/K2 remain N3 oracle calibrations independently of the entry whitelist.
Final-tree Build2 checks inventory + remaining positives/C1 + regressions + all calibrations;
no full inherited 235/242 verification matrix. Full Build1 PASS needs no Build2.

After authorized dispatch run `k1g.sh watch BUILD`, then END TURN. No status polling loop.
Evidence first `smallsort-brief BUILD`; only on missing index/field record limitation and use bounded
K-1 summary/rows/peaks/log-grep/check-tooling/budget. No raw/cache/archive/credential access.
Preserve frontend/resolution/specialization error, unsupported, TIMEOUT and ordinary FAILED classes.
RESULT-TRAITPFC-G3.md <=45 lines only after evidence: identities/literal ensures and model signatures,
old capture, all row times/counts/covers/full failed checks, inventory, separate code-ready/bounded
proof/resource-open, domains, sum verification time of new ordinary rows, manifests, spend and limits.
No generic T/F, other lengths/types, extra UB classes, unwind theorem, B2/full-proof or actual PR-CI
claim. Actual PR-CI needs the repository pin to include kani#5135. Stop after final review markers.
