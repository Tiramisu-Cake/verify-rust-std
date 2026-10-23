# R23 array/slice borrow content fix — design note (2026-10-24)

## Defect and applicability

The R20 helper converts a checked fixed-length `array::<u64>` plus per-element `own::<u64>` resources into slice full-borrow content and back. The P2 raw-caller and R19 synthetic unwind runs report a Verifast type mismatch at `verified/lib.rs(43,45-46)`, `Actual: *[u64]. Expected: *[T]`, before the intended target. Static comparison shows the helper directly specializes `slice_full_borrow_content::<u64>` in first-class `full_borrow`/`implies` predicate-expression positions, while the existing `slice_ref.rs` contracts use the resolved typed predicate `<[u8]>.full_borrow_content(...)`; the checked prelude definition maps `<[T]>.full_borrow_content` to `slice_full_borrow_content::<T>`.

## Invariants

- Keep the helper's exact `array::<u64>(p, 3, ?current) &*& foreach(current, own::<u64>(t))` resource and all existing `p`/slice pointer-metadata and length-3 preconditions.
- Preserve both checked directions: array content to slice content and slice content to array content, including both `implies` chunks and `full_borrow_implies` conversions.
- Use the existing typed predicate definition in first-class predicate-expression positions that require specialization. In top-level `req`/`ens` assertions, apply the predicate value with `()`; when passed as a value to `full_borrow` or `implies`, leave it unapplied. Keep the actual `open` and `close` of the concrete slice constructor where its body is being unfolded/folded.
- Do not change the prelude, parser, kernel, runtime, proof predicates, array model, memory model, or any assumptions. This is a source syntax correction; local static checks do not establish that the Cloud verifier now accepts it.

## Distinguishing checks

- A focused static service test checks predicate-value versus assertion-application syntax, exact direction-specific req/ens expressions, pointer and length constraints, both implication chunks and their body lemmas, and retains exactly the two direct `open`/`close slice_full_borrow_content::<u64>` commands.
- The existing Evidence Brief records this candidate's early `*[u64]` versus `*[T]` mismatch before the target; the next authorized Cloud cycle is the only way to verify the typed-expression adjustment against the actual compiler and verifier. No local proof execution is authorized.
