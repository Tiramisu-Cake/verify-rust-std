//! Bounded SmallSort checks; exact evidence domains and gaps are in the PR's Known limitations.
//!
//! `merge` checks stable primitives, merge, general/stable routes and normal-return Drop counts
//! and tags. `network` checks exchange, real networks, insertion, dispatch and mutating
//! comparators.
//! `correct` checks u8 prefix insertion through the insertion profile.
//! `assembly` pairs original/mutant witnesses and checks stable unit ZST N1/2/7/8/16/17/31/32.
//! `comparators` supplies their reading comparator; `smoke` checks the efficient-swap predicate.
//! `mutations` contains changed copies used only by opt-in controls.
//! `types` checks logical sortedness and multisets for Cell and Freeze non-Copy trait inputs.
//!
//! `swap_if_less`, `sort4_stable`, `insert_tail` and `bidirectional_merge` carry no generic
//! contract: no order or frame summary holds for an arbitrary `FnMut`. Their contract proofs
//! check closed profiles (`merge::specfix`): a tag fixes the element type, one canonical
//! comparator and a full-value model; the profile runs the real helper, and a guard rejects any
//! other comparator value. Ordinary profile proofs cover selected swap types and orders, sort4
//! u64/[u8; 16], merge u64 N2..8/u8 N2..9 (u8 N9 also from scratch48), u8 prefix and u64
//! start-1 insertion. No ordinary harness uses a verified stub; general/stable N0/N1 run real
//! bodies. Stubbed composition and upper domains of the removed raw contracts are retired.
//! Network/insertion safety checks execute real bodies. Network sortedness is machine checked;
//! permutation beyond N8 uses a structural argument, not a machine-checked full-route theorem.
//! The three `small_sort` trait methods have no requires/ensures; correctness uses harness asserts.
//!
//! Manual stubs cut only `panic_on_ord_violation`; covers and selected opt-in controls support
//! nonvacuity. `run-kani.sh` does not fail on unreachable covers; historical covers were inspected
//! separately. See the PR limitations for uninit, aliasing, generic types, ZSTs, panic and unwind.
//!
//! From the repository root, `./scripts/run-kani.sh --run list` lists the ordinary suite;
//! `./scripts/run-kani.sh --run verify-std` supplies organizer flags and `--no-assert-contracts`.
//! For controls, prefix either command with `RUSTFLAGS="--cfg kani_smallsort_controls"`.
//! Select expected failures separately with `--kani-args --harness <full-name> --exact`.

mod assembly;
mod comparators;
mod correct;
mod merge;
#[cfg(kani_smallsort_controls)]
mod mutations;
mod network;
mod smoke;
mod types;
