# RESULT P1-CLEAN — session 1: PARTIAL (P1 transfer done, READY_FOR_FULL_CI; case5 OPEN)

Task `TASK-PONECLEAN.md`. Baseline **`6f3a2629615cc7184b840d3c21aaea54b129267e`** (SPECFIX StageA+A2,
library tree `31997f7781`); cap 88.96 inherited, history unchanged. Pin Kani `9461e07af7`,
nightly-2026-10-12; tools/workflows/flags untouched; no local cargo/rustc/Kani.
Library commit `9456baadf9` (library tree **`73e902bec8`**, identical in G1/G2/G3); review packet
`poneclean/PREBUILD.md` (GO for `72a2a67f7c`). Why PARTIAL: G1 gate false only on the three case5
diagnostic rows (expected SUCCESS); every P1-CLEAN gate row met its expectation.
## Builds (k1-standard4, 3 of 3 shared with session 2; own $1.2825 ≤ $4, reserved 0)

| Build | UUID / request / head | Result | Own cost |
|---|---|---|---|
| G1 | `c8105152-b311-42e8-8809-a4451615932f` / `poneclean-g1-20261031` / `72a2a67f7c` | 11/14 as expected; case5 ×3 FAILED | $0.2430 |
| G2 | `850af95c-d099-4504-b3d0-49d08639a9ad` / `…-g2-inventory-ordinary-…` / `37270fd462` | exact 197 = frozen P1 | $0.5670 |
| G3 | `de37c6d8-d4aa-42e2-87c8-df4d03013a63` / `…-g3-inventory-controls-…` / `8c08b9bebe` | exact 377 = source cfg-on | $0.4725 |

Project used $71.4795 / $88.96. check-tooling vs `30f77e8599` ok ×3; head/pin/request sha match.
## Snapped clauses (generic helper → checked profile; table in `poneclean/PREBUILD.md`)

- `smallsort.rs`: all requires/modifies/ensures of `swap_if_less`, `sort4_stable`, `insert_tail`,
  `bidirectional_merge` removed with their comments and the unused `use crate::kani`; bodies and
  signatures byte-identical (gate projection). No generic clause, no F call in any spec.
- Removed: swap pre-state `F` decision + post-state order via raw `F`; insert/merge `F`-sorted
  prefix/halves requires; sort4/insert/merge `F`-sorted ensures; byte-probe count ensures;
  element-only modifies. Callback-calling spec helpers (`call_comparator`, `is_sorted*`,
  `valid_*`, `merge_inputs_are_sorted`, `tail_region_*`) deleted from `verify/merge.rs`.
- Profiles (`verify/merge/specfix.rs`, ordinary module): same geometry (sort4 source readable
  instead of writable; insert `1<=d<32`), canonical fn-pointer guard, same modifies, model
  sortedness, full-value model counts / model transfer + pair order.
## 32 P1 PFC → profile/tag, 4 stubs (`poneclean/PFC-MAP.tsv`)

merge ×11 + scratch48 u8 N9 → `merge_profile` LtU64/LtU8; sort4 u64/bytes16 → `sort4_profile`
Sort4ReadU64/Sort4ReadB16 (old reading closure as a named fn, same math/reads); insert u8 prefix
→ LtU8, START1 ×3 → LtU64; swap: four_positions LtU8/LtI32/LtU64, u8/u64 n2/n9/n13/indices17
StrictU8/StrictU64, bytes16/17 KeyB16/KeyB17, Cell CellI32 (model `get()`), Drop DropU8
(private, owner module). Names/domains/N/offsets/covers/harness frame asserts unchanged; each is a
new instance (F = fn pointer, typed model probe). `general_stable_sorted_permutation_{u8,u64}_n{0,1}`:
`stub_verified` removed, real body, same asserts. No ordinary harness uses a verified stub.
## DEACTIVATED (`poneclean/DEACTIVATED.tsv`, 140 rows)

132 `#[cfg(any())]` on concrete instantiations (72 raw PFC, 57 raw `stub_verified`, 3 SPECDIAG
predicate diagnostics) + 8 StageA profile PFCs removed as duplicates of migrated names; 69 rows
were in legacy P2-343. Each row: legacy kind/target/location at the baseline, INTEG2
`a847dcf80b` + tree + p2 manifest sha, published Part 2 `028040f941` + tree (separate refs),
reason, previous status. Kept: real-body `sort4_arbitrary_comparator_bytes85_n4`; START1
prefix/suffix frame controls retargeted to `insert_tail_profile` (NOT_RUN).
## G1 rows (controls on, jobs 1, uninit off; all 14 compiled and ran; cbmc peak 2.85 GiB)

| # | Harness | Status | VT s | Covers | Failure location |
|---|---|---|---|---|---|
| 1 | network::swap_contract_u8_n9 (StrictU8) | SUCCESS | 31.7 | 7/7 | — |
| 2 | merge::sort4_contract_u64_n4 (Sort4ReadU64) | SUCCESS | 76.1 | 1/1 | — |
| 3 | network::swap_contract_bytes17_n2 (KeyB17) | SUCCESS | 21.5 | 5/5 | — |
| 4 | network::swap_contract_cell_i32_n2 (CellI32) | SUCCESS | 14.8 | 5/5 | — |
| 5 | network::swap_contract_drop_u8_n2 (DropU8) | SUCCESS | 14.4 | 5/5 | — |
| 6 | network::insert_tail_contract_u64_start1_tail2_to8 | SUCCESS | 292.4 | 9/9 | — |
| 7 | merge::merge_contract_u8_n8 (LtU8) | SUCCESS | 110.5 | 1/1 | — |
| 8 | specfix_wrong_f_swap_rejected_u8 | FAILED = exp. | 0.1 | 1/1 | specfix.rs:218 guard only |
| 9 | specfix_wrong_f_sort4_rejected_u64 | FAILED = exp. | 0.3 | 1/1 | specfix.rs:243 guard only |
| 10 | specfix_wrong_f_insert_rejected_u8 | FAILED = exp. | 0.8 | 1/1 | specfix.rs:279 guard only |
| 11 | specfix_wrong_f_merge_rejected_u8 | FAILED = exp. | 0.7 | 1/1 | specfix.rs:317 guard only |
| 12–14 | specfix_case5_typed_swap_bytes{17,128,129} | FAILED (exp. SUCCESS) | 1.6/10.3/10.0 | 1/2 | component oracle pos 0+1 |

Rows 8–11: exactly 1 failed check, `specfix_canonical_comparator::<P>(cmp)` via `Verified stub`:
the guard rejects an always-true pointer before the ordered summary. cbmc RSS: 1 0.30, 2 0.87,
3 0.33, 4 0.26, 6 2.85, 7 1.17 GiB, others not sampled (`g1.peaks.txt`).
## Case5 conclusion (A2 row 9 case 5)

Real `swap_if_less`, closure `a[0] < b[0]`, arbitrary `[u8; M]`, no probe. At M = 17, 128, 129
both component checks fail; the array `==` check is not among the failed checks; 2/99 failed,
6 unreachable; exactly one branch cover (swap taken / not taken) unsatisfied, which one is not
printed. This matches neither planned branch (component pass + `==` fail; both fail). Size-
independent, so not the 128-byte probe bound. Likely, but unverified on the pin: a failed
`kani::assert` also assumes its condition, so no path reaches `==` after a component failure, and
one branch disagrees with the expected move on every path. Cause **UNKNOWN** (terse output, no
trace/playback in the schema). Not a negative control, not a claimed library or Kani defect.
Impact on P1: the migrated byte-array swap PFCs use the profile (fn pointer, model `==`);
`swap_contract_bytes17_n2` passed. The anomaly is confined to the raw closure-comparator
diagnostic and stays OPEN; bytes16 swap is NOT_RUN here.
## Inventories

- G2: 197/197, names SHA-256 `5e86596c…df8b` = frozen P1, exact `ordinary-expected.txt`.
- G3: 377, SHA-256 `04e300ae…69cd`, exact `cfg-on-expected.txt` = 510 − 140 + 7 new.
  Both cfg compile on `73e902bec8`; composition only, not proof acceptance (B1 ≠ B2).
## OPEN / NOT_RUN / next

- NOT_RUN on this tree: 25 of 32 P1 PFCs, 4 former stub consumers (real body), all other P1
  real-body rows (unchanged sources), positive regression, payload/probe/frame controls. All 32
  PFCs need the coordinator's full CI on exact tree `73e902bec8` (both OS); old PASS (incl. full
  CI 38933b2354, macOS 197 dfc2698f62, GEOM16) does not transfer.
- Case5 cause (needs a trace or a coordinator-approved diagnostic build; no slot left here).
- Legacy P2 frozen on INTEG2 / Part 2; adapter path not attempted. F06 (whole-route count only
  N<9), F08 (panic cut = normal-return scope, no unwind safety), F09 (uninit/invalid-value
  detection, stock `is_initialized`), padding and general `FnMut` effects: OPEN, not claimed.
- Session 2 list: none of the P1 transfer remains; only case5 diagnosis and the full CI.

Artifacts: `poneclean/` (packet, manifests, gate scripts/results, per-build request/summary/
tooling/cost/wait files, G1 extracts, inventories, budgets). No full/raw logs.
