//! Bounded SmallSort checks for selected input domains and properties.
//!
//! Module map:
//! - `network`: exchange profiles, real networks, insertion, dispatch, mutating comparators,
//!   coincident swap positions, and the large non-Copy fallback. Sortedness checks count full
//!   values only below the network width. Insertion lengths stop at 20, the callers'
//!   `MAX_LEN_ALWAYS_INSERTION_SORT` threshold, rather than a limit of the insertion helper.
//! - `merge`: stable primitives, merge, general and stable routes, and Drop counts and tags.
//!   `merge::specfix` supplies closed ordered profiles with independent full-value models.
//! - `assembly`: fixed witnesses and stable unit-ZST checks; `comparators` supplies their
//!   reading comparator. `smoke` checks the efficient-swap predicate.
//! - `types`: logical sortedness and multisets for Cell and Freeze non-Copy inputs.
//!   `wrap`: concrete two-element forwarding contracts for Cell, u8, and Freeze non-Copy u8.
//! - `permtags`: identity-tag permutation and source-type dispatch predicates. Transfer to
//!   arbitrary payloads assumes the same route moves whole elements and branches only on
//!   answers, positions, lengths, and type properties. This source-level assumption is not a
//!   generic refinement theorem; it excludes payload mutation, sortedness, and stability.
//! - `scratchgeom`: real stable u64 sorting with separate minimal scratch and full-value counts.
//!
//! Real helper contract domains (comparators read both arguments and return arbitrary bools):
//! - `realcontracts`: swap of u8, u64, or `[u8; 17]` in four elements; u8 in nine or thirteen;
//!   u64 tail insertion at positions 1 through 4 in five elements; sort4 of u64 with separate
//!   source and destination arrays; u64 merge of two or four elements with separate output.
//! - `allocationcontracts`: swap of u8 or u64 in 32 elements with an arbitrary interior base;
//!   u64 merge of eight elements from scratch positions 32 through 39 to positions 0 through 7.
//! - `tailcontracts`: u64 tail insertion at positions 1 through 15 in 17 initialized elements.
//! Verified swap consumers match the nine-, thirteen-, or 32-element proofs; the sort8 consumer
//! matches the eight-element scratch merge proof. Each pair must pass with the same element
//! type, comparator, and allocation geometry. A callback-cover hook is omitted in the smaller
//! swap consumers because verified stubs bypass the comparator, while preserving its type.
//!
//! The five real helper write sets list only element or destination memory. Kani cannot express
//! the footprint of an arbitrary `FnMut`. These contracts may be used with `stub_verified` only
//! on the proved domains above and with comparators that write nowhere else; one successful
//! contract proof does not justify a new consumer. The opt-in control
//! `realcontracts::rejects_swap_comparator_writing_outside_frame_u8` checks this restriction.
//!
//! `cfg(kani_smallsort_controls)` enables only negative controls; ordinary CI leaves it unset.
//! Run controls individually and require their named failure.
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
//! - Trait methods have no contracts: the pinned Kani rejects specialization defaults and
//!   method-generic comparators (model-checking/kani issues #5116 and #4908).
//! - Types, lengths, comparators, or routes beyond those listed, including aliasing, ZST,
//!   and panic cases.
//!
//! `./scripts/run-kani.sh --run list` lists ordinary roots; `--run verify-std` checks them with
//! the organizer flags, including `--no-assert-contracts`. To select a negative control, set
//! `RUSTFLAGS="--cfg kani_smallsort_controls"` and pass
//! `--kani-args --harness <full-name> --exact` to the verification command.

mod allocationcontracts;
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
mod tailcontracts;
mod types;
mod wrap;
