//! Bounded SmallSort checks; exact evidence domains and gaps are in the PR's Known limitations.
//!
//! `merge` checks stable primitives, merge, general/stable routes and normal-return Drop counts
//! and tags. `network` checks exchange, real networks, insertion, dispatch and mutating
//! comparators.
//! `correct` adds fallback correctness and general/stable u8 N14/15 with a 48-element scratch.
//! `assembly` pairs original/mutant witnesses and checks stable unit ZST N1/2/7/8/16/17/31/32.
//! `comparators` supplies their reading comparator; `smoke` checks the efficient-swap predicate.
//! `mutations` contains changed copies used only by opt-in controls.
//!
//! Ordinary contract proofs cover swap, sort4, merge N2..16, u8 prefix/scratch insertion and
//! shifted u64 insertion regions. Ordinary `correct::contract_insert_tail_u8_scratch` covers
//! starts 0/6/7 and lengths 5..8 in a 48-element allocation; its u64 counterpart is opt-in.
//! `stub_verified` requires matching type, comparator, length, allocation and active region.
//! Fallback u64 composition depends on an opt-in base-region contract; exact-array fallback
//! and scratch merge composition also need allocation-locality transfer not proved here.
//! Network/insertion safety checks execute real bodies. Network sortedness is machine checked;
//! permutation beyond N8 uses a structural argument, not a machine-checked full-route theorem.
//! The three `small_sort` trait methods have no requires/ensures; correctness uses harness asserts.
//!
//! Manual stubs cut only `panic_on_ord_violation`; assembly witnesses and selected opt-in
//! coverage/control audits support nonvacuity. `run-kani.sh` does not fail on unreachable covers;
//! historical covers were inspected separately. See the PR limitations for uninit, aliasing,
//! generic types, ZSTs, panic and unwind.
//!
//! From the repository root, `./scripts/run-kani.sh --run list` lists the ordinary suite;
//! `./scripts/run-kani.sh --run verify-std` supplies organizer flags and `--no-assert-contracts`.
//! For controls, prefix either command with `RUSTFLAGS="--cfg kani_smallsort_controls"`.
//! Select expected failures separately with `--kani-args --harness <full-name> --exact`.

// Successful cover checks carry full CBMC witness traces, which the pinned driver retains.
// Audit them explicitly with the existing controls cfg; ordinary assertions and input domains
// are identical. Conditions are still evaluated so that cover-only reads/side effects remain.
macro_rules! proof_cover {
    ($condition:expr, $message:expr $(,)?) => {{
        #[cfg(kani_smallsort_controls)]
        crate::kani::cover($condition, $message);
        #[cfg(not(kani_smallsort_controls))]
        let _ = $condition;
    }};
}

mod assembly;
mod comparators;
mod correct;
mod merge;
#[cfg(kani_smallsort_controls)]
mod mutations;
mod network;
mod smoke;
