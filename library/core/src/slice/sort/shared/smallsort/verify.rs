//! Bounded SmallSort checks for selected input domains and properties (Part 1).
//!
//! The three `small_sort` trait methods have no contracts. On the current Kani pin, contracts
//! on specialization `default fn` and PFC on trait methods with their own generic `F` are not
//! accepted ([model-checking/kani#5116](https://github.com/model-checking/kani/issues/5116) and
//! [#4908](https://github.com/model-checking/kani/issues/4908); reproduced on the pinned
//! `cd355b0b`).
//! Helper contracts here use closed profiles that each fix one comparator.
//!
//! `merge` checks stable primitives, merge, general/stable routes and normal-return Drop counts
//! and tags. `network` checks exchange, real networks, insertion, dispatch and mutating
//! comparators, same-position exchange and the Freeze non-Copy large-value fallback.
//! `assembly` checks fixed-size original witnesses and stable unit ZST N1/2/7/8/16/17/31/32.
//! `comparators` supplies their reading comparator; `smoke` checks the efficient-swap predicate.
//! `types` checks logical sortedness and multisets for Cell and Freeze non-Copy trait inputs.
//!
//! The real helpers `swap_if_less`, `insertion_sort_shift_left`, `insert_tail`, `sort4_stable`
//! and `bidirectional_merge` carry safety/modifies contracts. `realcontracts` proves bounded
//! type/comparator domains with a stateless comparator that reads both arguments and returns
//! a fresh arbitrary bool: swap u8/u64/[u8; 17] backing4, u8 backing9/13, insert_tail u64
//! backing5 tail1..4, sort4 u64 source4/disjoint dst4, and merge u64 N2/4 with disjoint dst.
//! These are not universal callback frame proofs. Ordinary N9/N13 u8 network consumers use
//! verified swap stubs paired with the same type, backing and comparator PFC domains. Their
//! return cover is retained. The ordinary consumers omit `realcontracts comparator true` and
//! `realcontracts comparator false`: the verified swap stub cuts the callback. A coverage-only
//! hook is stubbed to a no-op, preserving the comparator function-item type and PFC domain.
//! Original consumers with both covers remain opt-in as `_with_callback_covers`.
//! The separate closed profiles in `merge::specfix` fix the comparator and full-value model;
//! a guard rejects any other comparator value. Ordinary profile proofs cover selected swap
//! types/orders, sort4 u64/[u8; 16], merge u64 N2..8/u8 N2..9 (u8 N9 also from scratch48),
//! u8 prefix and u64 start-1 insertion. General/stable N0/N1 run real bodies.
//! Network/insertion safety checks otherwise execute real bodies. Network sortedness is checked
//! at the listed lengths; the ordinary network asserts the probe count only for N < 9.
//! `permtags` checks identity-tag permutation through the real u8 network at N9/N13 and
//! checks source-type dispatch predicates. Transfer to arbitrary payloads assumes the same
//! type-selected route moves whole elements and branches only on answers/positions/lengths/type
//! properties, not payloads. This source-level assumption is not a generic refinement theorem;
//! payload-mutating comparators, sortedness and stability are excluded. The normal-return cover
//! is retained. Ordinary N9/N13 omit `permtags: order violation panic is reachable` because
//! the network cannot reach that boundary; its assume(false) cutoff is unchanged. Original
//! `_with_panic_cover` variants, larger tag domains and the duplicate-tag mutant require
//! `cfg(kani_smallsort_controls)`. All ordinary covers must be reachable.
//! `scratchgeom` checks Stable Freeze u64 N2 with a separate minimal scratch allocation of
//! 18 elements: real bodies, arbitrary reading comparator, geometry and full-value preservation
//! on normal return. Larger and shared-allocation geometries require the controls cfg.
//! `wrap` checks N2 forwarding contracts that run them for Cell<u8>, u8 and a Freeze non-Copy u8.
//!
//! Manual stubs cut only `panic_on_ord_violation`; the paired realcontracts consumers also use
//! verified swap stubs. Covers and opt-in negative controls support nonvacuity. The original
//! eight controls require `cfg(kani_smallsort_controls)` and must fail their named check:
//! `assembly::reject_mutant_swap_u8_n2` (the negated exchange in `mutations`),
//! `wrap::rejects_payload_corruption`, `wrap::rejects_always_true`, and in `merge::specfix`
//! `specfix_full_value_checker_rejects_payload_change_u8`, `specfix_wrong_f_swap_rejected_u8`,
//! `specfix_wrong_f_sort4_rejected_u64`, `specfix_wrong_f_insert_rejected_u8` and
//! `specfix_wrong_f_merge_rejected_u8`. Additional realcontracts negative controls, real network
//! consumers, insertion PFCs and sort4 [u8; 16] also require that cfg; CI never sets it.
//! `run-kani.sh` does not fail on unreachable covers; historical covers were inspected separately.
//! Region predicates describe pointer geometry, not initialization or permissions; constructed
//! fixtures supply initialized inputs and exclusive mutable storage.
//! Limits: `run-kani.sh` enables no uninitialized-memory or value-validity checks; the measured
//! Kani profile does not report writes to immutable bytes (no permission check); unwinding is not
//! checked. Aliasing, generic types, ZSTs and panic paths are covered only as listed.
//!
//! From the repository root, `./scripts/run-kani.sh --run list` lists the ordinary suite and
//! `./scripts/run-kani.sh --run verify-std` checks it with the organizer flags, including
//! `--no-assert-contracts`; neither sets the controls cfg. Run each control on its own and expect
//! its named failure: `RUSTFLAGS="--cfg kani_smallsort_controls" ./scripts/run-kani.sh --run
//! verify-std --kani-args --harness <full-name> --exact`.

mod assembly;
mod comparators;
mod merge;
#[cfg(kani_smallsort_controls)]
mod mutations;
mod network;
mod permtags;
mod realcontracts;
mod scratchgeom;
mod smoke;
mod types;
mod wrap;
