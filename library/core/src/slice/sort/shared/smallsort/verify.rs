//! Bounded SmallSort checks for selected input domains and properties.
//!
//! Module map:
//! - `network`: exchange profiles, real networks, insertion, dispatch, mutating comparators,
//!   coincident swap positions, and the large non-Copy fallback. Sortedness checks count full
//!   values only below the network width. Insertion lengths stop at 20, the callers'
//!   `MAX_LEN_ALWAYS_INSERTION_SORT` threshold, rather than a limit of the insertion helper.
//! - `merge`: stable primitives, merge, general and stable routes, and Drop counts and tags.
//!   `merge::profiles` supplies closed ordered profiles with independent full-value models.
//! - `fixed_inputs`: fixed witnesses and stable unit-ZST checks; `comparators` supplies their
//!   reading comparator. `smoke` checks the efficient-swap predicate.
//! - `types`: logical sortedness and multisets for Cell and Freeze non-Copy inputs.
//!   `forwarding_contracts`: concrete two-element forwarding contracts for Cell, u8, and
//!   Freeze non-Copy u8.
//! - `tag_permutation`: identity-tag permutation and source-type dispatch predicates. Transfer to
//!   arbitrary payloads assumes the same route moves whole elements and branches only on
//!   answers, positions, lengths, and type properties. This source-level assumption is not a
//!   generic refinement theorem; it excludes payload mutation, sortedness, and stability.
//! - `trait_model`: cfg(kani) conditional sort model for non-default trait methods, enabled
//!   only for u64, the canonical `U64Cmp` function pointer, and each entry's listed lengths.
//!   `trait_contracts`: ordinary PFC roots for stable, unstable, and Freeze entries at N2/N3,
//!   with sortedness and full-value multiplicities. Stable uses an array plus separate N+16
//!   scratch; unstable and Freeze use backing N+2, active 1..N+1, and exterior frame checks.
//!   The N3 consumer calls real unstable forwarding with only the matching Freeze leaf stubbed.
//!   Unstable PFCs also compose that leaf; credit requires the same F, length, and geometry.
//!   The whitelist is conditional; function items and other comparator values stay disabled.
//!   Opt-in controls calibrate full values, multiplicities, and the disabled model branch.
//! - `scratch_geometry`: real stable u64 sorting with separate minimal scratch and
//!   full-value counts.
//!
//! Real helper contract domains (comparators read both arguments and return arbitrary bools):
//! - `helper_contracts`: swap of u8, u64, or `[u8; 17]` in four elements; u8 in nine or thirteen;
//!   u64 insertion sort of two or three elements with any valid offset; u64 tail insertion at
//!   positions 1 through 4 in five elements; sort4 of u64 with separate source and destination
//!   arrays; u64 merge of two or four elements with separate output.
//! - `helper_contracts_wide`: swap of u8 or u64 in 32 elements with an arbitrary interior base;
//!   u64 merge of eight elements from scratch positions 32 through 39 to positions 0 through 7.
//! - `insert_tail_contracts`: u64 tail insertion at positions 1 through 15 in
//!   17 initialized elements.
//! Verified swap consumers match the nine-, thirteen-, or 32-element proofs; the sort8 consumer
//! matches the eight-element scratch merge proof. Each pair must pass with the same element
//! type, comparator, and allocation geometry. A callback-cover hook is omitted in the smaller
//! swap consumers because verified stubs bypass the comparator, while preserving its type.
//!
//! The five real helper write sets list only element or destination memory. Kani cannot express
//! the footprint of an arbitrary `FnMut`. These contracts may be used with `stub_verified` only
//! on the proved domains above and with comparators that write nowhere else; one successful
//! contract proof does not justify a new consumer. The opt-in control
//! `helper_contracts::rejects_swap_comparator_writing_outside_frame_u8` checks this restriction.
//!
//! Trait write sets likewise exclude arbitrary callback writes. Verified trait stubs require
//! comparators that write nowhere else and matching bounded real-body leaf proofs.
//!
//! `cfg(kani_smallsort_controls)` enables negative controls and their matching frame-only
//! calibration leaf; ordinary CI leaves it unset. Run each control with its named expectation.
//!
//! Conventions:
//! - Ordinary covers must be reachable; `run-kani.sh` does not enforce this itself.
//! - Panic stubs cut only the explicit order-violation abort path.
//! - Fixtures supply initialized input and exclusive mutable storage; region predicates
//!   check pointer geometry.
//! - Closed ordered profiles guard the exact comparator and use a pure model without
//!   invoking the callback.
//!
//! Not covered:
//! - Uninitialized-memory, value-validity, and immutable-byte permission checks, or unwinding.
//! - Specialization `default fn` contracts remain blocked by model-checking/kani issue #5116.
//!   Non-default trait impls have conditional contracts only on the domains listed above.
//! - Types, lengths, comparators, or routes beyond those listed, including aliasing, ZST,
//!   and panic cases.
//!
//! `./scripts/run-kani.sh --run list` lists ordinary roots; `--run verify-std` checks them with
//! the organizer flags, including `--no-assert-contracts`. To select a negative control, set
//! `RUSTFLAGS="--cfg kani_smallsort_controls"` and pass
//! `--kani-args --harness <full-name> --exact` to the verification command.

mod comparators;
mod fixed_inputs;
mod forwarding_contracts;
mod helper_contracts;
mod helper_contracts_wide;
mod insert_tail_contracts;
mod merge;
#[cfg(kani_smallsort_controls)]
mod mutations;
mod network;
mod scratch_geometry;
mod smoke;
mod tag_permutation;
mod trait_contracts;
pub(super) mod trait_model;
mod types;
