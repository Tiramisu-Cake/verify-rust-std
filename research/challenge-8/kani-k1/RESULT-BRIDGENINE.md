# RESULT BRIDGENINE — B2 SUCCESS (exact Stable u8 N9 instance)

G1 `b457683e-137b-485b-96a2-6d6fcf54e217`, request `bridgenine-g1-20261101`.
GO/source `b5448315bd55a3c8019f4df3cee5c3c4be54c912`; library `77cb4c97733d24c1f03f11dc803a2a7676bfc4d5`,
unchanged library tree `b903aba7c37e6956dc7b2643b4da79695d54fe4c`; branch `experiment/kani-k1-bridgenine-20261101`.
Kani `9461e07af7ec929f050aa4192f29363c9be07779`, nightly-2026-10-12, cap $88.96.
Cloud Build SUCCESS; summary COMPLETE, expectation/gate/measurement true; Kani exit1 from control.
Own 1 build, spent **$0.2025**, reserved $0, task cap $1.50; no compile error/leaf mismatch, no G2.

A/B share actual `<u8 as StableSmallSortTypeImpl>::small_sort` N9 and caller-owned scratch48.
Gate A2 **satisfied**: one explicit local F=`fn(&u8,&u8)->bool`, value LtU8::CMP unchanged through
real sort4/insertion -> raw merge -> B1 adapter -> verified merge_profile<LtU8> (B only).
One independent LtU8 probe set before input, unchanged; pure key(x>>1)/full-u8-count oracle, no F calls.
No panic-cut or caller sortedness assume. A has no stubs; leaf executes real profile/raw body.
Caller/leaf M03 match: `[MaybeUninit<u8>;48]`, src+0 prefix9 initialized/tail39 uninit, split4+5;
separate initialized `[u8;9]` dst+0; same F/probe/model, destination9-only merge frame.
Real sort4 writes [0..4)/[4..8), insertion extends second run to [4..9); B proves merge premises.
Leaf `merge_scratch48_contract_u8_n9` checks stable M03 and general M04 with both covers;
its full cost is charged to B. No transfer from M02/exact N3 or verified self replacement.

| Row (verify:: suffix) | Status | VT s | CBMC peak KiB | Failed/total; unreachable | Covers |
|---|---|---|---|---|---|
| bridge::bridgenine_direct_u8_n9 (A) | SUCCESS | 217.599270 | 426800 | 0/569;53 | 2/2 |
| bridge::bridgenine_caller_u8_n9 (B) | SUCCESS | 25.559757 | 347688 | 0/743;59 | 3/3 |
| merge::merge_scratch48_contract_u8_n9 | SUCCESS | 154.855620 | 1323280 | 0/571;57 | 2/2 |
| bridge::bridgenine_payload_flip_u8_n9 | FAILED expected | 19.980770 | 350956 | 1/743;58 | 3/3 |

Control [p;9], probe=p; caller v[0]^=1 after return (:171), same keys, count9->8.
Sole failure: `bridgenine output preserves full-value probe count`, bridge.rs:176 (literal kani::assert).
Sortedness passes; no requires/assigns/UB/unsupported/unwind/other failure. All covers satisfied.
VT(B)+VT(leaf)=**180.415377s**, vs A217.599270s: 37.183893s / **17.09% less**, 1.206x in this run.
Checks B+leaf=1314 vs A569. CBMC memory max(B,leaf)=1323280KiB (1.262GiB), vs A426800KiB
(0.407GiB): **3.10x higher**, not a memory improvement. 2s-sampled peaks have unique direct per-harness attribution.
Compiler VmHWM=1838980KiB (1.754GiB); verify command including compile wall8:11.80, time-v max1839220KiB.
Whole Cloud Build start->finish14:37.572, ledger15min/$0.2025; machine16GB, swap off, uninit off.
Static17/17, ordinary exact200 preserved, cfg-on388->391; rustfmt/request/source checks pass.
check-tooling against `30f77e859903df14b442ff9294d4fbbd44827f20` passes; source/request/pin identities match.
Bridge applies to this actual Stable Freeze/u8/N9 composition, with a modest VT win including leaf.
W1 full scope remains OPEN. N16 needs matching merge8/final16 leaves and actual caller proofs;
N16/macOS performance is a separate hypothesis. One run establishes no broader speedup; old v4 F-item is not A.
Artifacts: `bridgenine/g1.{summary.md,summary.json,acceptance.json,peaks.txt,verification.txt,tooling.txt}`,
status/cost/extracted/dispatch/watch/budgets; `bridgenine/PREBUILD.md` preserves the historical review.
REVIEW REQUEST `b5448315bd55a3c8019f4df3cee5c3c4be54c912` — accepted by coordinator before G1.
**BRIDGENINE ЗАВЕРШЁН**
