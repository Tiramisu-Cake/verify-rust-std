# W7 candidate: actual sort9_optimal / sort13_optimal over the R4 helper

Status **PREPARED / UNVERIFIED** (network-bootstrap-2026-10-22-n1). No proof
tool, compile or Cloud run. Proof credit 0. Safety/ownership only — the
sorting theorem stays the separate mathematical N9/N13 component
([INTEGRATION](../../networks/INTEGRATION.md)); this candidate does not link them.

`network-body.py` builds, per network, one crate = the R4 crate
(`../r4/swap-if-less-body.py construct`, same std pin `40939f92`, same Select
layer blob) + two generated lemmas + the exact actual body with ghost text
only (`strip_ghost` restores it; checked). The crate header adds
`#![feature(core_intrinsics)]` + `use std::intrinsics;` (form of Select's
`a1-fixtures.py` blob `797e3d11`) for the body's `intrinsics::abort()`.
`test_network_body.py` (6 tests) checks strip, the 25/45 ordered pairs against
[SOURCE-MAP](../../networks/SOURCE-MAP.md), imports of every free path, lemma
presence/bodies, the control matrix, and a wrong-source refusal.

| Item | Value |
| --- | --- |
| sort9 span / calls | 420–461 / 25 |
| sort13 span / calls | 469–530 / 45 |
| Callee | actual `swap_if_less`, verified in the same crate (not an assumed summary); its contract requires `a_pos != b_pos`, satisfied by every literal pair |
| Lemmas | `split_owned_cellsN` / `join_owned_cellsN`: Select's checked `split_four_owned_cells`/`join_four_owned_cells` pattern unrolled for the first N cells of `base[..len]`; bodies are open/close/`points_to_limits`/`note` only, no `assume`. **Deliberate deviation:** cell 0 is written `*(base + 0)` (Select writes `*base`) so it matches the helper's `*(v_base + a_pos)` at `a_pos = 0`; this moves the `ptr_add_(p, 0)` question into the split lemma's postcondition. The join also notes the one-past limit `base + N` from the suffix chunk |

Contract: `(v as *T)[..v.len()]` with `foreach own` and `F` own on entry and on
normal exit; on unwind (any of the N-network calls) the N cells separately owned
plus the remaining suffix — no rejoin claim on the unwind edge (no ghost site
there). `v.len() < N` takes `intrinsics::abort()`.

## Gates and risks (first Cloud run decides)

* **R4 gates P1/P2** (`../r4/DESIGN.md`, `../r4/SELECT-REQUESTS.md`) — the helper must verify first.
* **`<[T]>::as_mut_ptr`**: not a stock translator built-in; Select's recipe carries
  `caller-entry/verifast-slice-as-mut-ptr.patch` (projection to `v as *T`). Consume
  it by exact pin in the Network profile; no Network copy.
* **`core::intrinsics::abort`**: no stock spec (only `std::process::abort`); Select's
  caller route handles it (`selected-branch-binding.patch` mentions it) — to confirm
  and pin, else a layer request.
* **Safe `fn` contracts**: `sort9_optimal`/`sort13_optimal` are safe functions; VeriFast
  may require the user spec to be implied by the type-derived spec (`&mut [T]` own),
  which this raw-ownership spec is not. If so, the remedy is a type-based
  contract plus a checked bridge from slice ownership to cells (open design
  item); disabling or bypassing that check is not an option (CORE boundary).
* **Index 0**: calls with literal 0 need `*(v_base + 0)`; stock shows no
  `ptr_add_(p, 0) == p` lemma. The split lemma's postcondition and the R4
  positive caller `(0, 1)` expose this as a precise frontier.

## Controls (`matrix()`; files `sortN-<label>.rs` + `meta.json`)

| Control | Mutation (ghost only) | Expected |
| --- | --- | --- |
| positive | — | PASS (helper + lemmas + body); evidence only with both reach controls failing |
| split-off | no `split_owned_cellsN` | missing cell chunk at the first call |
| join-off | no `join_owned_cellsN` | postcondition failure or leak at return |
| reach-before-first | `assert false` right after the split | assertion failure; PASS = inconsistent state after split |
| reach-after-last | `assert false` right before the join | assertion failure; PASS = inconsistent state after the calls |

The R4 matrix (helper controls) runs alongside; the W7 positive is not
reported as progress before the R4 helper and its controls are accepted.
