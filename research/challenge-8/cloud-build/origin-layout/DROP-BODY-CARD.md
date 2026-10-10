# Concrete source-linked one-cell Drop body diagnostic

Status: prepared for independent review; no Cloud result or actual-callee credit.
Profile: `experimental-merge-origin-layout-concrete-u64-v1`, tool `8cb0121b03a5164495bf0d7c6c236ea9504d5ce4`.

## Obligation and scope

The pinned `smallsort.rs` block at lines 295–309 declares the private three-field
`CopyOnDrop<T>` and its `Drop::drop`, whose body copies `self.len` current source
elements to `self.dst`. The bounded consumer is the one-cell guard at line 551
in `insert_tail`, with `T = u64`. This diagnostic mechanically substitutes `T`
with `u64` in the exact extracted block and in both original and verified case
files. It is a **source-linked specialization**, not a compiler-generated
monomorphic MIR instance. It cannot establish an actual callee, compiler glue,
generic safety, a comparator frame, or full `insert_tail`.

The direct control retains the historical full count-n `req`, normal `ens` and
`on_unwind_ens false` byte-for-byte except for mechanical type substitution.
Its inherited `safety_proof` still opens generated FBC/default own and now
executes the required checked `call()`; any
prototype-compatibility failure is retained. Even if its runtime body reaches
the copy and return, a separate compatibility error keeps the whole case
INCONCLUSIVE. A conditional-body label requires complete verifier success and
return/leak gates.
The canonical cases retain the generated safe-Drop FBC precondition and the
generated normal/unwind postcondition, including their compatibility and leak
checks. AST admission checks both generated outcome arms separately: each must
return the exact `src`, `dst`, `len` fields, padding and thread token, with no
completed payload inserted. Ghost `safety_proof` opens FBC and `own`, checks the existing root and
src/dst geometry, then executes `call()`. A `first_body_false` case may count
only if the real method body is reached; a `prototype_false` case tests the
canonical prototype immediately after opening FBC/own. Runtime copy operands
and dynamic `self.len` stay unchanged.

The one-cell `own` carries an existing quarter source share, an uninitialized
destination and the CURRENT u64 value. This differs from the historical direct
contract and the frozen `copy_nonoverlapping` specification, both of which
require initialized destination storage. A refusal at this entailment is a
contract-interface blocker in this diagnostic; the already observed concrete
literal-one copy from an uninitialized destination remains separate evidence
and must not be negated by this generic historical specification. Do not assume an initialized gap, replace the
destination contract, or claim that a conditional direct-body PASS applies to
the one-cell caller. The diagnostic does not add authority, an ownership pool,
an entry-value snapshot, or a layout premise.

## Falsifiable result and stages

The positive first checks exact source, specialization/ghost strip, qualified
MIR body and three fields, AST canonical FBC/own/prototype and dynamic copy,
export/decode/refinement, then root bounds/alignment/separation, direct strong
pre entailment, method body, canonical post, return and leak. The classifier
reports the **first** failure stage; setup/frontend/refinement/unrelated helper
failures are inconclusive. A completed direct control establishes only the
conditional specialized body on this exact profile. A canonical refusal at
initialized `dst`, root alignment, guard interval, or residual payload is
preserved as such, never counted as a positive or intended negative.

Cases are `direct_positive`, `direct_first_body_false`, `canonical_dst_pre`,
`canonical_positive`, `prototype_false`, and `first_body_false`. The
`canonical_dst_pre` case checks initialized destination entailment immediately
after opening FBC/own, so it remains informative if root layout blocks the
full canonical case. The two canonical false cases must fail at the
exact asserted location after their preceding gates. Original/verified files
must match after removing recorded ghost text; the original must match the
independently specialized pinned block. Each Cloud stage must retain its source
hash receipt. Full normal and unwind posts, dead-code, return and leak checks
remain active. `on_unwind_ens false` belongs only to the conditional Drop-body
contract and does not turn off caller unwind checking.

## Trust and layout boundary

No compiler, verifier, parser, translator, schema, prelude, kernel or std source
change is part of this diagnostic. In particular, `gen_drop_contract` and
generic `drop_in_place` remain unchanged. The current model gives the guard no
source-qualified positive byte extent or alignment. The prior generic V3b
canonical diagnostic stopped at self alignment after checked root limits. If
this concrete run stops there, a repeat without new evidence is unwarranted.
A future layout import must bind the pinned compiler/target's qualified
`CopyOnDrop<u64>` instance to the verifier's *same* `sizeof/alignof` terms;
a measured numeral or source name alone is not a proof premise. A semantic card,
independent review and affected positive/negative gates are required before
such a tool change. Proof status stays OPEN until a fresh Cloud run passes its
own exact obligations.
