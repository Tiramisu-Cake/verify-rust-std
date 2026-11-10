# TRAITPFC G3 — Build 2 exact pre-build packet

Coordinator-approved qualification repair, sole remaining Build 2. PRE-BUILD review pending;
NO dispatch authorization. The final PRE-BUILD REVIEW marker binds this exact pushed packet.
Branch `experiment/kani-k1-traitpfc-20261110`, owner `k1-merge`, slug `traitpfc`, stage `traitpfc-g3`.
Request `traitpfc-g3-20261110-02`, diagnostic, standard4/jobs1, controls=true, inventory=true.
Library `1aac64c50d69382c8ce90811880225d0a047525f`; tree
`6ea9d3425f6d0478cfc2517cbdd2fb7d7b32a53f`; request/patch hashes: identities.json/check-report.json.
Tooling base `9b1758ab817af005e96fd52a5fc940d4b6acf984`, Kani
`f046b70644e113be0df9c22c2e6ea44a65a57566`, nightly-2026-10-23, unchanged.

## Exact repair and scope

Build1 `9d94cb84-55e1-4cae-a55b-9597ddd81d87`, source
`55a7fd1c8ada1590ab571b040a6256219ef75e63`, library `aa0859448612246d0c52e1c59f844e777c8ad3b6`,
tree `b6f050a21d2781fcc95a8f7e02bf9154affa560a`: COMPILE_ERROR, all14 proof rows NOT_RUN.
Only K4/W1's `<() as SortModel<u64, _>>::enabled(...)` failed E0308, because `_` resolved to
fn-pointer F while the argument retained the canonical comparator's function-item F.
Native cfg-off inventory was exactly242 on that original tree. It is not Build2 proof evidence.
Build1 diagnostics/report are preserved in ../evidence/ and
[RESULT](../../../RESULT-TRAITPFC-G3.md).

Coordinator admitted the exact proposed helper as a harness type-inference qualification repair.
The only library delta from Build1 is this helper plus its two K4/W1 call sites:

```rust
#[cfg(kani_smallsort_controls)]
fn function_item_model_enabled<F>(cmp: &F, len: usize) -> bool {
    <() as SortModel<u64, F>>::enabled(SortEntry::Freeze, cmp, len)
}
```

Both sites use `let enabled = function_item_model_enabled(&cmp, v.len());`.
The comparator remains `let mut cmp = trait_less_u64;`, a function item, at both real/stub calls.
The helper fixes F from the reference before the explicit trait lookup. Its compiler acceptance
remains NOT_RUN: no local cargo/rustc/Kani/CBMC was invoked. REPAIR-AUTHORIZATION.json records scope.

Model, all three literal ensures, native old Copy capture, entry whitelist, positive harnesses,
assertions, covers, domains, types, geometry, unwind, runtime bodies/API/gates and tooling are unchanged.
The helper is cfg-only and used only by K4/W1. check_traitpfc_g3.py --build2 checks the entire
library delta against Build1 for the exact authorized transformation and no other change.
The broader preservation checks still freeze all235 ordinary plus13 inherited control closures.

## Exact rows and acceptance

All14 rows and expectations are identical to Build1; only designated source coordinates/file hashes
are refreshed after the five-line insertion. Full domains and coordinates: expected-rows.json.
All rows below are NOT_RUN on this candidate library tree.

| Row | Root suffix (trait_contracts unless qualified) | Expect | Covers |
|---|---|---|---:|
| A1 | stable_sorts_permutation_u64_len2 | SUCCESS | 5 |
| A2 | stable_sorts_permutation_u64_len3 | SUCCESS | 5 |
| A3 | freeze_sorts_permutation_u64_backing4 | SUCCESS | 5 |
| A4 | freeze_sorts_permutation_u64_backing5 | SUCCESS | 5 |
| A5 | unstable_sorts_permutation_u64_backing4; composed, matching real A3 required | SUCCESS | 5 |
| A6 | unstable_sorts_permutation_u64_backing5; composed, matching real A4 required | SUCCESS | 5 |
| C1 | verified_forwarding_sorts_permutation_u64_backing5; matching A4/compatible A6 | SUCCESS | 5 |
| K1 | rejects_high_bit_corruption_u64_len3 | FAILED exactly1 | 0 |
| K2 | rejects_changed_multiplicities_u64_len3 | FAILED exactly1 | 0 |
| K3 | rejects_reverse_pointer_sorted_u64_backing5 | FAILED exactly1, sortedness | 0 |
| K4 | rejects_function_item_sorted_u64_backing5; matching W1 frame leaf | FAILED exactly1, sortedness | 0 |
| W1 | freeze_frame_function_item_u64_backing5; matching function-item F/N3/backing5 | SUCCESS | 3 |
| R1 | scratch_geometry::stable_u64_min_scratch_n2, unchanged | SUCCESS | 2 |
| R2 | forwarding_contracts::unstable_byte_n2, unchanged | SUCCESS | 7 |

Every A/C input remains unconstrained, with explicit canonical U64Cmp, enabled assert/cover before
calling; all five covers required (enabled, ascending, descending, duplicate, return). T1 array N
plus separate scratch N+16; T2/T3/C1 backing N+2 active1..N+1 with both exterior checks.
C1 independent typed copies/checks do not call the model after the call. Canonical pointer is enabled;
reverse pointer and function item are disabled. New unwind32, R1 unwind34/R2 unwind16 unchanged.
K1 sole failure: `high-bit corruption preserves sorted full values`; unchanged snapshot must pass.
K2 sole failure: `same set preserves full multiplicities`; a<b is only a negative-fixture condition.
K3 sole failure: `reverse pointer output is sorted`; K4: `function item output is sorted`.
Require exact failed/total counts, full check locations/messages, all covers, and T3 stub binding.
No composed proof credit without successful matching real-body leaf; W1 must match K4's actual F.

Fresh native cfg-off inventory on THIS tree must exactly match all242 ordinary names. Source manifests
are unchanged (235→242 ordinary,260→260 cfg-on), with both full lists regenerated. Frozen runner
lists before exporting controls; list argv is not emitted, so attribute flags via source-bound
list-before-export configuration plus available diagnostics as in Build1/G2. Controls-on verification
uses organizer no-assert-contracts/object-bits12 and 5m/harness; uninit/value-validity remain off.
Do not transfer Build1 inventory acceptance to this tree or treat source checks as formal proof.

## Identities, static checks, and applicability

Run `python3 -B research/challenge-8/kani-k1/traitpfc/check_traitpfc_g3.py --build2`.
check-report.json binds the new library commit/tree, all four source hashes and request/manifests.
Manifests, contracts.json, inherited closures.json, runner/kani-args/rustflags are byte-identical to
Build1; request only changes its id to 02. Runtime/core bytes and G1 requires/modifies remain frozen;
no new Rust line>100; rustfmt --check zero diff. Native compiler/proof acceptance remains NOT_RUN.

library.patch is the entire library diff from 9b1758ab81, including original G1 contracts and G3 model.
Only empty context-line markers are omitted (raw diff and patch hashes recorded). apply-check.json
records successful plain `git apply --check` on submitted head872d5a4338; temporary scratchpad
worktree was removed by literal absolute path. No submission branch was changed.
Build1 package/evidence identities remain unchanged; root and local RUN-LEDGER describe the pending
Build2 without modifying the Build1 run's original source/library/request/outcome or cost.

## Time, budget, and hard stop

Unchanged runner: 14*5+30=100 paid minutes ($1.3500); verify cutoff14*5+24=94m after validation.
Planning: setup12 + inventory49=61m, leaving33m after inventory for compile/rows23 + slack10;
summary/upload6 =>100m paid. A60m inventory leaves22m after setup12. Inventory/setup consume this
same timeout, not an extra allocation; no70m row budget after inventory and no automatic120m.
Build1's total49 billed minutes is measured; its inventory/setup phase split was not measured here.
No duration guarantee: preserve compile/unsupported/TIMEOUT/ordinary FAILED classes and partial rows.

Own spent$0.6615 + Build2 reserve$1.3500=$2.0115 <= cap$3.50; own remaining after maximum$1.4885.
Project receipt: used$110.9400 + unfinished reserve$0.6750 + Build2$1.3500=$112.9650 <= cap$118.96;
remaining$5.9950. Budget receipt: prebuild-budget.txt; refresh before any dispatch.
No live Build2 reservation is claimed. Maximum two builds; one used, one remaining; repair branch
is locked. No later narrowing build, retry, third build, new lengths/types, new assumptions/panic
cuts, disabled unwind assertions, ghost protocol or tooling changes.

T0 unchanged: 2026-11-10T19:51:57Z; main deadline2026-11-11T01:51:57Z;
closeout deadline2026-11-11T02:21:57Z. No reset or extension. Current window receipt is in RUN-LEDGER.
Before dispatch require exact-packet coordinator GO, same SHA/library/request/tooling/window/budget.
Then `k1g.sh watch BUILD` and end turn. No status polling loop.
Evidence first smallsort-brief; on missing index/field record limitation, then bounded K-1 interfaces.
No raw/cache/archive/credential reads or direct GCS/logging commands. Final RESULT <=45 lines must
separate code-ready, bounded proof PASS and resource-open, with full identities/rows/covers/inventory,
spend, new-ordinary sumVT and limits. No B2, generic T/F, other types/lengths, extra UB, unwind theorem
or actual PR-CI on a pin including kani#5135 claim. Stop at final review/completion markers.
