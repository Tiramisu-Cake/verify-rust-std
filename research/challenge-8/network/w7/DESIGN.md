# W7 candidate: actual sort9_optimal / sort13_optimal over the R4 helper

Status **PREPARED / UNVERIFIED** (network-bootstrap-2026-10-22-n1). No proof
tool, compile or Cloud run. Proof credit 0. Safety/ownership only — the
sorting theorem stays the separate mathematical N9/N13 component
([INTEGRATION](../../networks/INTEGRATION.md)); this candidate does not link them.

`network-body.py` builds, per network, one crate = the R4 crate
(`../r4/swap-if-less-body.py construct`, same std pin `40939f92`, same Select
layer blob) + two generated lemmas + the exact actual body with ghost text
only (`strip_ghost` restores it; checked). `test_network_body.py` (4 tests)
checks strip, the 25/45 ordered pairs against [SOURCE-MAP](../../networks/SOURCE-MAP.md),
lemma presence/bodies, and a wrong-source refusal.

| Item | Value |
| --- | --- |
| sort9 span / calls | 420–461 / 25 |
| sort13 span / calls | 469–530 / 45 |
| Callee | actual `swap_if_less`, verified in the same crate (not an assumed summary); its contract requires `a_pos != b_pos`, satisfied by every literal pair |
| Lemmas | `split_owned_cellsN` / `join_owned_cellsN`: Select's checked `split_four_owned_cells`/`join_four_owned_cells` pattern unrolled for the first N cells of `base[..len]`; bodies are open/close/`points_to_limits` only, no `assume` |

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
  which this raw-ownership spec is not. If so, the contract needs the type-based
  form plus an internal bridge from slice ownership to cells — an open design item.
* **Index 0**: calls with literal 0 need `*(v_base + 0)`; stock shows no
  `ptr_add_(p, 0) == p` lemma. The split lemma's postcondition and the R4
  positive caller `(0, 1)` expose this as a precise frontier.
* Normal-path reachability controls (as in R4) are to be added with the first
  run's matrix; none are generated here yet.
