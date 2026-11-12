# KANI3300 M2-B/S3 — PREPARED / UNVERIFIED
- Local reviewed Kani candidate: 58497d98d085a5144a70c358205c0e46318feeb6; not pushed.
- Trace: coordinator run43252039413, CI4804129592, reported exact5f7 + M2-A C03.
- .1 tests LEFT, runtime object50 base0 length3; selected witness byte is object50:2.
- Reached body is write_initialized::{closure#3}::{closure#0}, inner contract Assert copy.
- Last selected-byte write: reset FALSE, State1009; no later matching shadow value write/retarget.
- Later set(FALSE) is object49:0, nonmatching; RHS immutable object20 seed is not the problem.
- `_16` contains [1,2,3]; old inner MIR lacks normal-return `_16` and post-write out setters.
- Actual failure is body equality; ensures/out write is later and not reached in this trace.
- Alias analysis followed raw registration panic; codegen uses a closure-calling trampoline.
- Narrow override restores that bridge and preserves discarded closures as unreachable.
- No seed/model/ABI/DFCC/retarget rewrite; typed setters are existing instrumentation.
- Added unchanged C03 regression + lawful flat-MU ensures holes in both operand directions.
- Original M2/M2-A sources/goldens hash-unchanged; explicit source/type/signature audit complete.
- Luna HIGH static review: no established blocking correctness/type/identity findings.
- Cyclic clause calls remain a conditional termination/generalization gate; no cutoff/summary added.
- JSON/hash/source/diff checks and authorized rustfmt PASS; build/clippy/solver NOT_RUN locally.
- Coordinator must establish restored setters, full C03 PASS and precise negative/control outcomes.
- M2-B/S semantic gate OPEN; M2-B/R resource gate separate/unresolved; M3 HELD.
- Cloud $0; compiler/verifier0; dispatch0; no new proof credit. STOP for coordinator CI.

## M2-B/S3R — test-only const-allocation repair (2026-11-12)

- Candidate: `4f64cc617cbe6ebd13e83c07cc62fcf245e0b53c`, direct child of
  `58497d98d085a5144a70c358205c0e46318feeb6`, in `/root/kani-fix-3300-m2b-seed`.
  Commit subject includes `[skip ci]`; local commit only, no push/force/reset/stash.
- Coordinator-reported baseline (not independently rerun): Uninit Quick `43255336861`
  on `58497d98d0` plus CI-only `b161cc025a`, excluding only transfer-qualification/legal-pair
  and postcondition-hole because the resource gate remains open. Unit 5/0, kani Uninit 22/0,
  ui 14/0, script 1/0; expected uninit 133/2. C03 ordinary-singleton and
  out-pointer/normal-abort PASS; all others PASS except these two ensures-hole tests,
  which failed compilation with E0515 at the direct `&[MaybeUninit::uninit(), ...]` return.
- Repair changes ONLY `ensures-left-hole.rs` and `ensures-right-hole.rs`: declare a
  block-local `const HOLE: [MaybeUninit<u8>; 3]` with the identical initializer, then
  return `&HOLE`. No production code or expected-output file changes.

Rust-rule check without a compiler:

1. `MaybeUninit::new` and `MaybeUninit::uninit` are const functions (const-stable since
   Rust 1.36), so all three array elements can be evaluated in the const-item initializer.
   `MaybeUninit<u8>` permits an uninitialized payload; constructing/borrowing that wrapper
   does not read the payload. See [MaybeUninit API](https://doc.rust-lang.org/std/mem/union.MaybeUninit.html#method.uninit)
   and [constant expressions](https://doc.rust-lang.org/reference/const_eval.html#constant-expressions).
2. The borrow now refers to the evaluated constant value, so it no longer requires
   promotion of the runtime expression containing the `uninit()` call. The array value
   has neither interior mutability nor a destructor, and is eligible for promotion;
   consequently `&HOLE` has the required `'static` lifetime. This follows from
   [constant-item references](https://doc.rust-lang.org/reference/items/constant-items.html#r-items.const.static-temporary)
   and [constant promotion](https://doc.rust-lang.org/reference/destructors.html#constant-promotion).
   This is a source/rules conclusion, not an observed compiler exit for the pinned nightly.
3. A const item does not designate a named static storage location. Its shared borrow
   retains an immutable const/anonymous allocation; no mutable stack fixture, `static mut`,
   initialization write, zeroing, or `assume_init` was introduced. Payload mask remains
   `[None, Some(7), Some(7)]`; companion remains `[Some(7); 3]`.
4. Attributes, signature, harnesses and raw_eq operand order are byte-unchanged. The first
   payload read remains in the ensures Assert: left-hole expects the left operand's
   uninit-read FAILURE; right-hole expects the right operand's uninit-read FAILURE.
   The initialized companion must pass in each case; a generic FAILURE is insufficient.

Validation: exact replacement assertion against the parent confirms the two-file scope,
unchanged surrounding source/goldens and line width <=100; `git diff --check` PASS.
Local cargo/rustc/Kani/CBMC/rustfmt and all CI were NOT_RUN; Cloud $0, dispatch0.
Coordinator CI must confirm compilation and operand-specific negative/control outcomes.
No new semantic gate closure or independent proof credit; resource gate remains separate/open.
STOP.
