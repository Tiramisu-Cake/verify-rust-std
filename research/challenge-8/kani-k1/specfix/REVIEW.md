# SPECFIX PRE-BUILD REVIEW packet (StageA)

T0 2026-10-31T16:22Z (session start), deadline 21:22Z, closing from 20:52Z.
Base `d8f97fb2df`, cap `30f77e8599` (unchanged). Library commit `0b5cbd2a3b`, library tree
`4865c40287c87a629a9503f8f19a614e3f58af0d` (base library tree `9000a3c7a0`).
Pin Kani `9461e07af7`, nightly-2026-10-12; tools/workflows/flags untouched.

## Decision: StageA (PARTIAL, F03 OPEN)

Full atomic transfer is not done here (reasons and the complete next-step schema:
`STAGEB-PLAN.md`). Ordinary generic annotations, callers and smallsort.rs are unchanged; old
F03-flawed clauses still stand for all 197/343 names and are not hidden.

## Patch (3 library files, `git diff d8f97fb2df 0b5cbd2a3b -- library`)

- `verify/merge/specfix.rs` (new, `#[cfg(kani_smallsort_controls)] pub(super) mod specfix;`,
  separate lines after `mod specdiag;`): closed `Profile` trait (u8, u64, [u8;16] via audited
  macro; Cell<i32> by `get()`), canonical reading comparators, pure `model_sorted` /
  `model_count` (typed shared probe, scalar `old` count), four profiles
  `swap_profile`/`sort4_profile`/`insert_tail_profile`/`merge_profile` that forward exactly
  `cmp` to the real raw helper, `merge_adapter` (stub for `bidirectional_merge`), 8 profile
  PFCs, 1 positive regression, 3 negative controls.
- `verify/network.rs`: opt-in DropValue profile (model = full u8 payload) and
  `swap_profile_drop_u8_n2`; additions only.
- `verify/merge.rs` (ordinary, F05): `matches_value_probe` asserts `size_of::<T>() <= 128`
  and returns before the first read otherwise. No effect for instantiated T (<= 86 bytes) but
  every probe-using proof gains one constant check: old PASS is a source-equivalence argument.

## Profile semantics (F03/F04/F05)

- Specs never call the callback (static check: 20 clauses, 0 calls). Order and value claims
  come from `P::model`/`P::model_less`; `P::CMP` is literally the model order plus volatile
  reads. Guard `specfix_canonical_comparator`: `cmp as *const () == P::CMP as *const ()`
  (what `fn_addr_eq` does). Effectful/arbitrary `FnMut` is outside every profile.
- swap: decision `model_less(pre_b, pre_a)` on pre-state models; transfer of full models per
  branch + model pair order; frame = two positions; snapshot is `Copy` models (no Drop).
- insert: size > 0, same allocation, both ends `can_dereference` before `offset_from`,
  `1 <= d < 32`, whole `[begin,tail]` `can_dereference` and `can_write`, then model-sorted
  prefix (one `&&` clause: no read on false geometry, also in replace mode).
- sort4: source `can_dereference` (readonly allowed), destination `can_write`, disjoint.
- merge: `2 <= N <= 32` before any length use, source `can_dereference`, destination
  writable/disjoint, then model-sorted halves.
- Init: these are declared premises. Stock `is_initialized` is true, so they detect nothing;
  SPECDIAG 7–10/15–18 stay OPEN as profile/model limitations (`manifest.json`).

## Gates

`check_specfix.py` → `static-check-prebuild.json` ok: smallsort.rs byte-identical; library
changes only the 3 files; merge.rs projection byte-identical; guard before first read;
network additions cfg-gated; specs callback-free; harnesses = manifest; expect_checks
unique/located; requests validate; lines <= 100. rustfmt `--check` clean for merge.rs (with
submodules); network.rs shows only the pre-existing base import diff (also at base).
`TRANSFER.tsv`: 342 callers rows + 16 manifest omissions (incl. ordinary
`contract_insert_tail_u8_prefix`), StageB target/evidence per row.

## Requests and budget

| Build | File | Kind / flags | Entries | Reserve |
|---|---|---|---|---|
| G1 | `g1.request.json` (`specfix-g1-20261031`) | measurement, 10 min, controls, jobs 1, uninit off | 12 | 150 min / $2.025 |
| G2 | `g2.request.json` | inventory, controls false, 20 min | [] | 50 min / $0.675 |
| G3 | `g3.request.json` | inventory, controls true, 30 min | [] | 60 min / $0.810 |

Sum $3.510 <= $4; project before: used $68.7525, reserved $0, cap $88.96. Source tree is the
same for all three; each needs its own RUN-REQUEST commit. Proposal: dispatch G1 on GO, then
G2 and G3 immediately (same tree, research-only commits) so all end before 20:52Z.

G1 expectations: rows 1–9 SUCCESS (all covers expected satisfiable); row 10 FAILED only at
`merge_profile` requires `specfix_canonical_comparator` (merge/specfix.rs:295); row 11
FAILED only at merge/specfix.rs:611; row 12 FAILED only at merge.rs:46 (no OOB). A compile
error in row 10's stub chain would fail the whole G1 compile: that risk is explicit.
