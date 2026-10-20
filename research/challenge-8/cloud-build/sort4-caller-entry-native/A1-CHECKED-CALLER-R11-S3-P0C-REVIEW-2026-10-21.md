# R11 S3 P0c checked-cleanup review

## Decision

**GO for the checked generic cleanup mechanism as a bounded proof candidate; HOLD release of P0c until the exact focused build proves the helper body or provides a same-build helper-proof gate.** The static ownership path supports the intended disposal without `type_interp<T>`. Merely seeing the ghost call accepted under `-focus` would not establish that the helper body was checked.

## Ownership-path review

The S3 helper in `a1-fixtures.py` has an explicit generic lifetime and type in
both contract and body. In the pinned VeriFast source at
`f76012fb518703b1d98e243ac4f487f16877cfcb`, `Option_own` is generated as an
enum own predicate whose `None` arm is `Emp` and whose `Some(r)` arm owns its
field (`rust_parser.ml:995–1015`). The active standard model declares
`Option<T>` with those two variants (`bin/rust/std/lib.rsspec:1568–1572`).

For a shared reference, the translator defines its own assertion as the
pointee's shared assertion (`vf_mir_translator.ml:2308–2323, 2377–2379`). For a
generic pointee `T`, `translate_param_ty` expresses `T.share` under
`CoefAsn(DummyPat, ...)` (`vf_mir_translator.ml:2500–2524`). Thus opening
`Option_own::<&'a T>` and matching `Some(r)` leaves a dummy-coefficient
`T.share` chunk. `check_leaks` removes chunks with dummy fraction coefficients
before checking that no other chunks remain (`verify_expr.ml:180–192`); the
helper returns the thread token in its postcondition. This is direct source
support for the proposed residual-resource closure, rather than an inference
from an unopened abstract ref predicate. The translator path adds no
`type_interp<T>` precondition. I found no need for an ownership bridge, axiom,
`leak`, `forget`, or runtime drop in this construction.

The isolated source-construction test passes all three cases. It checks the
lemma text and call placement, but does not establish that VeriFast checks the
lemma implementation or that focused verification evaluates that body.

## Release condition

The S3 design appropriately marks Cloud verification as the first proof
evidence for the lemma. Before using the observer's helper call as P0c
discharge, the exact focused invocation must either include and check this
generic lemma body or be gated on a same-build proof of that exact body. Keep
the binding receipt tied to the source pair, tool/profile, and build, and retain
the existing 26-case matrix/admission requirements. Until then the static
review is GO for the candidate's ownership logic, not proof credit or a claim
that the observer leak is fixed.
