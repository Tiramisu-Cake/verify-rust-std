//! Bounded Kani checks for SmallSort (Towards Challenge 8).
//!
//! # Modules and properties
//!
//! - `merge` defines probe-count, sortedness and region predicates, and contracts exercised on
//!   `bidirectional_merge`, `insert_tail`, `sort4_stable` and `sort8_stable`. It also checks real
//!   general/stable routes and normal-return Drop counts and tag multiplicities. Real merge
//!   checks execute `merge_up`/`merge_down`; `assembly` also checks `merge_up` advancement.
//! - `network` checks `swap_if_less`, the fixed 9/13-element networks, insertion, trait dispatch,
//!   exact exchange allocation/frame properties and arbitrary or interior-mutating comparators.
//! - `correct` checks fallback u64 lengths 8..=16 and u8 lengths 9..=16 using verified insertion,
//!   plus general/stable u8 lengths 14/15 with scratch 48. Prefix insertion is ordinary;
//!   explicit scratch insertion contract checks are opt-in controls.
//! - `assembly` pairs selected original bodies with mutation witnesses and checks stable unit ZST
//!   lengths 1/2/7/8/16/17/31/32. `uninit` supplies only their ZST-aware comparator; it does not
//!   establish uninitialized-memory safety. `smoke` checks `has_efficient_in_place_swap`.
//! - `mutations` contains deliberately changed copies used only by opt-in controls.
//!
//! Safety harnesses on real general/stable/network bodies use u64 lengths up to 32 and read both
//! comparator arguments before choosing an arbitrary result. Insertion checks are bounded through
//! length 20 and enumerate valid offsets; no arbitrary-length insertion theorem is claimed.
//! Ordered checks use specific pure strict orders on u8/u64. Combined reported correctness covers
//! general/stable u8 0..=16 and u64 0..=12/16, fallback u8/u64 0..=16, and network u8 0..=15 and
//! u64 0..=14. Network permutation beyond length 8 also relies on structural composition of the
//! checked exchange contract and insertion-tail results, rather than a full-route multiset check.
//!
//! # Contract composition and trusted boundaries
//!
//! `stub_verified` uses `proof_for_contract` for matching types, comparators, lengths and regions:
//! `network::swap_if_less_*`, `w2p2_k9s_*` and `w3_k9s_*` plus backing17 instances check exchange;
//! `merge::w3_sort4_contract_*`, `sort4_*` and `sort8_*` check stable primitives;
//! `merge::w2p2_bm_*`/`bm_*` check merge; shifted-tail proofs in `network` check u64 backing17.
//! `correct::l2_insert_tail_prefix_u8` checks backing17 prefixes. The scratch insertion checks in
//! `correct` and exact length/type tail checks in `merge` are opt-in contract diagnostics.
//! `sort9_optimal`, `sort13_optimal` and `insertion_sort_shift_left` retain contract annotations;
//! their alternative contract harnesses are historical diagnostics. Retained ordinary checks use
//! their real bodies, not verified stubs of those three functions. The fixed network's permutation
//! argument composes two-cell exchanges; it is not a separate sort9/sort13 contract proof.
//! General/fallback callers rely on the stated callee domains. Extending an allocation or scratch
//! domain needs a locality argument; a successful caller alone does not prove an unchecked callee.
//!
//! Ordinary manual stubs replace only `panic_on_ord_violation` with a path cut. Separate controls
//! cover its reachability and check that false assertions and invalid preconditions are detectable.
//! A controls-only network mutation also replaces `small_sort_network` with its changed copy.
//! These checks exclude comparator panic and unwind recovery. Ordinary CI lacks uninit checks;
//! enabling a controls cfg does not enable them. See **Known limitations** in the PR description
//! for uninitialized memory, aliasing, generic types, ZSTs, scratch-locality premises and gaps.
//!
//! # Running
//!
//! From the repository root, `./scripts/run-kani.sh --run list` lists ordinary harnesses. Use
//! `./scripts/run-kani.sh --run verify-std` for the organizer's verification settings. The script
//! selects the Kani pin in `tool_config/kani-version.toml` and supplies the unstable contract,
//! memory-predicate, loop-contract, quantifier and stubbing flags, with `--no-assert-contracts`.
//! For controls, use `RUSTFLAGS="--cfg kani_smallsort_controls" ./scripts/run-kani.sh --run list`
//! to enumerate them separately. Run selected controls with the same RUSTFLAGS and
//! `--run verify-std --kani-args --harness <full-name> --exact`.
//! Expected failures must be selected and interpreted separately from the
//! ordinary suite; controls also include positive contract and reachability diagnostics.

mod assembly;
mod correct;
mod merge;
#[cfg(kani_smallsort_controls)]
mod mutations;
mod network;
mod smoke;
mod uninit;
