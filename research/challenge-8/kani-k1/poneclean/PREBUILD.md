# P1-CLEAN PRE-BUILD REVIEW packet (session 1)

Task `TASK-PONECLEAN.md` (5bf73502e5). Baseline `6f3a2629615cc7184b840d3c21aaea54b129267e`
(SPECFIX StageA + A2, library tree `31997f7781`); cap 88.96 inherited, history unchanged.
Pin Kani `9461e07af7`, nightly-2026-10-12; tools/workflows/flags/toolchain untouched.
No local cargo/rustc/Kani: compile of both cfg settings is first established by G1/G2/G3.

## Patch (library commit `9456baadf9`, library tree `73e902bec8`, 7 files)

- `smallsort.rs`: all generic contracts removed from `swap_if_less`, `sort4_stable`,
  `insert_tail`, `bidirectional_merge` (requires/modifies/ensures + their `// Contract:` comments)
  and the then-unused `#[cfg(kani)] use crate::kani`. Runtime bodies/signatures byte-identical
  (gate: base minus annotation blocks == current; only added line = tail comment).
- `verify/merge/specfix.rs` (now an ordinary module, every harness in it `cfg(controls)`):
  `Profile { type Elem; type Model; const CMP; model; model_less; probe; set_probe }` on
  zero-sized tags keyed by (T, comparator); four profiles `swap/sort4/insert_tail/merge_profile`
  forwarding exactly `cmp` to the real helper; canonical fn-pointer guard; specs use only pure
  models (0 callback calls). Tags here: `LtU8`, `LtI32`, `LtU64` (key `x>>1`), `Sort4ReadU64`,
  `Sort4ReadB16` (old sort4 closure = volatile reads + `lt_*`, now a named fn, same math/reads).
  In `network.rs` (comparator owner): `StrictU8`, `StrictU64`, `KeyB16`, `KeyB17` (array key
  byte 0), `CellI32` (model `get()`), private `DropU8` (model = whole payload).
- `merge.rs`, `network.rs`, `correct.rs`: 32 P1 PFC retargeted (names, domains, N/offsets,
  covers, harness frame asserts unchanged; probe = typed model, arbitrary) — `PFC-MAP.tsv`.
  4 P1 stub consumers `general_stable_sorted_permutation_{u8,u64}_n{0,1}`: `stub_verified`
  dropped from the macro, real body, same asserts. Old callback-calling spec helpers
  (`call_comparator`, `is_sorted*`, `valid_*`, `merge_inputs_are_sorted`, `tail_region_*`) deleted.
- Retire: 132 cfg-on items `#[cfg(any())]` on concrete instantiations (P1-producing macros
  untouched in cfg), 8 StageA profile PFCs removed as duplicates of the migrated names —
  `DEACTIVATED.tsv` (legacy kind/target/location, INTEG2 `a847dcf80b`/tree/p2 manifest sha and
  published Part 2 `028040f941` as separate columns, reason, previous status; 69 rows were in
  legacy P2-343). The real-body half of the bytes85 sort4 pair is kept as a standalone control.
- Controls: 2 START1 frame controls retargeted to `insert_tail_profile` (same expected frame
  failure); new 4 wrong-F (`stub_verified(<profile>)`, always-true fn pointer, all other requires
  true) and case5 ×3; positive regression keeps cases 0–4, 6 (case 5 moved out).
- `verify.rs`: doc comments only; module order unchanged.

## Clauses: before → after (generic helper → checked profile)

| Helper | Removed generic clauses | Profile clauses |
|---|---|---|
| swap | `a!=b`+geometry; modifies 2 cells; byte transfer by pre-state `F` call; post-state order via raw `F` | geometry; guard; same modifies; model transfer by pure pre-model decision; model pair order |
| sort4 | src+dst `can_write`, disjoint; modifies dst4; `F`-sorted; byte-probe count | size>0, src `can_dereference`, dst `can_write`, disjoint; guard; same modifies; model-sorted; model count |
| insert | writable region + `F`-sorted prefix; modifies `[begin,tail]`; `F`-sorted; `old` probe count | guard; size>0, same alloc, ends readable, `1<=d<32`, region readable+writable, model-sorted prefix; same modifies; model-sorted; `old` model count |
| merge | `2<=N<=32`; dst writable/disjoint; `F`-sorted halves; modifies dst; `F`-sorted; probe count | guard; size>0, `2<=N<=32`, src readable, dst writable/disjoint, model-sorted halves; same modifies; model-sorted; model count |

Each migrated PFC is a new instance (F = fn pointer, typed model probe): old PASS does not transfer.
Real-body harnesses calling the helpers are unchanged under organizer flags
(`--no-assert-contracts`).

## Static gate (`check_poneclean.py` → `static-check-prebuild.json`, ok 29/29)

smallsort.rs projection/signatures; library files limited; module order; 0 callback calls in
spec attributes; no active raw PFC/stub; no ordinary `stub_verified`; static ordinary = frozen
P1 197 (exact names, `ordinary-expected.txt`); cfg-on 377 = base 510 − 140 + 7 new
(`cfg-on-expected.txt`); 32 PFC → profile+tag; 4 former stubs real body; guard requires located
once per profile; requests validate; lines ≤ 100. rustfmt `--check` clean for all changed files.

## Requests and budget

| Build | File | Kind / flags | Entries | Reserve |
|---|---|---|---|---|
| G1 | `g1.request.json` = `RUN-REQUEST.json` | measurement, controls, jobs 1, uninit off, 10 min | 14 | 170 min / $2.295 |
| G2 | `g2.request.json` | inventory, controls false, 20 min | [] | 50 min / $0.675 |
| G3 | `g3.request.json` | inventory, controls true, 30 min | [] | 60 min / $0.810 |

Sum $3.780 ≤ $4, 3 builds shared with session 2. Budget now: used $69.9135, reserved $1.08 by
other builds, cap $88.96 (`budget-before-g1.txt`).
G1 rows (full names under `verify::`), positives SUCCESS: 1 `network::swap_contract_u8_n9`
(swap×StrictU8, other-cell frame); 2 `merge::sort4_contract_u64_n4` (sort4×Sort4ReadU64, `>>1`);
3 `network::swap_contract_bytes17_n2` (KeyB17 payload); 4 `network::swap_contract_cell_i32_n2`;
5 `network::swap_contract_drop_u8_n2`; 6 `network::insert_tail_contract_u64_start1_tail2_to8`
(shifted frame); 7 `merge::merge_contract_u8_n8`. Wrong-F FAILED, `expect_check`
`specfix_canonical_comparator` (one requires line per profile): 8 swap, 9 sort4, 10 insert,
11 merge. Case5 12/13/14 `specfix_case5_typed_swap_bytes{17,128,129}`: expect SUCCESS; a FAILED
is diagnostic only (component oracle vs array `==` messages separate), not a control.
Not in G1: 25 other P1 PFCs (full CI), positive regression, payload/probe/frame controls.

## Risks

- First compile of tags/`identity_profile` re-export, relative `proof_for_contract(specfix::…)`
  in merge.rs, `stub_verified` of a generic profile. A compile error = all G1 rows NOT_RUN.
- case5@17 failing would also put byte-array swap ensures (`[u8;17]` model `==`) under suspicion.
- G2/G3 only after G1 on this exact library tree; any semantic fix = new tree, delta review.
