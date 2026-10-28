//! Bounded SmallSort checks. Exact domains and the trust ledger are in the PR description.
//!
//! `merge` supplies count/sortedness/region predicates and checks merge, stable primitives,
//! general/stable routes and normal-return Drop counts/tags. Real merge checks include
//! `merge_up`/`merge_down`; `assembly` also checks `merge_up` advancement.
//! `network` checks exchange, real networks, insertion, dispatch and mutating comparators.
//! `correct` adds fallback u64 N8..16, u8 N9..16, and general/stable u8 N14/15 with scratch48.
//! `assembly` pairs original/mutant witnesses and checks stable unit ZST N1/2/7/8/16/17/31/32.
//! `uninit` contains only their comparator, not an uninitialized-memory proof.
//! `smoke` checks `has_efficient_in_place_swap`; `mutations` is controls-only.
//!
//! `stub_verified` / `proof_for_contract`: match type, comparator, length and memory region.
//! Exchange proofs are in `network::swap_if_less_*` and its exact-array contract families.
//! Stable primitive/merge proofs are in `merge::w3_sort4_contract_*`, `sort4_*`, `sort8_*`,
//! `w2p2_bm_*` and `bm_*`; some are opt-in. Shifted u64 tail proofs use backing17 in `network`.
//! `correct::l2_insert_tail_prefix_u8` is ordinary; scratch48 tail proofs are opt-in.
//! General/stable composition additionally relies on scratch-locality transfer.
//! Real network/insertion checks do not use verified stubs of sort9/sort13/insertion.
//! Network permutation beyond N8 uses structural exchange/tail composition, not full-route counts.
//!
//! Ordinary manual stubs cut only `panic_on_ord_violation`; paired controls check reachability.
//! A separate negative control replaces `small_sort_network` with its changed copy.
//! See Known limitations in the PR description: bounded insertion through N20, remaining
//! correctness gaps, uninit/aliasing, generic types, ZSTs, comparator panic and unwind recovery.
//!
//! From the repository root, `./scripts/run-kani.sh --run list` lists the ordinary suite;
//! `./scripts/run-kani.sh --run verify-std` supplies organizer flags and `--no-assert-contracts`.
//! For controls, prefix either command with `RUSTFLAGS="--cfg kani_smallsort_controls"`.
//! Select expected failures separately with `--kani-args --harness <full-name> --exact`.

mod assembly;
mod correct;
mod merge;
#[cfg(kani_smallsort_controls)]
mod mutations;
mod network;
mod smoke;
mod uninit;
