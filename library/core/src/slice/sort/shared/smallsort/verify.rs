//! Bounded SmallSort checks for selected input domains and properties (Part 1).
//!
//! The three `small_sort` trait methods have no contracts. On the current Kani pin, contracts
//! on specialization `default fn` and PFC on trait methods with their own generic `F` are not
//! accepted (reproduced on `cd355b0b`, Actions runs 41894986646 and 41894991130).
//! Helper contracts here use closed profiles that each fix one comparator.
//!
//! `merge` checks stable primitives, merge, general/stable routes and normal-return Drop counts
//! and tags. `network` checks exchange, real networks, insertion, dispatch and mutating
//! comparators, same-position exchange and the Freeze non-Copy large-value fallback.
//! `assembly` checks fixed-size original witnesses and stable unit ZST N1/2/7/8/16/17/31/32.
//! `comparators` supplies their reading comparator; `smoke` checks the efficient-swap predicate.
//! `types` checks logical sortedness and multisets for Cell and Freeze non-Copy trait inputs.
//!
//! `swap_if_less`, `sort4_stable`, `insert_tail` and `bidirectional_merge` carry no generic
//! contract: no order or frame summary holds for an arbitrary `FnMut`. Their contract proofs
//! check closed profiles (`merge::specfix`): a tag fixes the element type, one canonical
//! comparator and a full-value model; the profile runs the real helper, and a guard rejects any
//! other comparator value. Ordinary profile proofs cover selected swap types and orders, sort4
//! u64/[u8; 16], merge u64 N2..8/u8 N2..9 (u8 N9 also from scratch48), u8 prefix and u64
//! start-1 insertion. No ordinary harness uses a verified stub; general/stable N0/N1 run real
//! bodies. Stubbed composition and larger contract domains are outside this suite.
//! Network/insertion safety checks execute real bodies. Network sortedness is machine checked at
//! the listed lengths; the ordinary network asserts the probe count only for N < 9. Longer
//! compositions belong to separate research results, not to this suite.
//! `wrap` checks N2 forwarding contracts that run them for Cell<u8>, u8 and a Freeze non-Copy u8.
//!
//! Manual stubs cut only `panic_on_ord_violation`; covers and eight opt-in negative controls
//! support nonvacuity. The controls are compiled only with `cfg(kani_smallsort_controls)`, which
//! CI never sets, and each must fail its named check: `assembly::reject_mutant_swap_u8_n2` (the
//! negated exchange in `mutations`), `wrap::rejects_payload_corruption`,
//! `wrap::rejects_always_true`, and in `merge::specfix`
//! `specfix_full_value_checker_rejects_payload_change_u8`, `specfix_wrong_f_swap_rejected_u8`,
//! `specfix_wrong_f_sort4_rejected_u64`, `specfix_wrong_f_insert_rejected_u8` and
//! `specfix_wrong_f_merge_rejected_u8`. Other diagnostics and lengths are a separate Part 2.
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
mod smoke;
mod types;
mod wrap;
