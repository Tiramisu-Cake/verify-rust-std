# H2b local-template admission matrix: before the next hosted run

## Observed obligation and proposed boundary

O17 (`37717092130`, proof `11d888ba8ff2231a80c759148194aa9ae6b9d30e`)
proves the *local* source-shaped generic `DropOnPanic<T>::drop` with H2a and
the selected H2b template: the generic callee, guard Drop's normal and
unwind continuations, concrete owner constructor and witness, and ordinary
Drop all return and leak-check. It does not prove the function-local actual
std DefPath. The selected generated post retains stock field, padding and
thread resources and adds only `*inner |-> _` on both outcomes. It must not
return an initialized cell, `<T>.own`, or an `Element` right after the
destructor.

The remaining admission question is whether the exact source/ADT/full typed
MIR certificate admits *only* this local object and call graph, and whether
the generated resource post is as narrow as claimed. In particular, the
reviewed H2a gate checks `is_repr_c=false`, the one private field, spans,
ghost inventory and the full four-block Drop graph, but does not inspect
attributes immediately before `struct DropOnPanic<T>`. A `repr(packed)`
attribute is not represented by the `isReprC` schema field. An otherwise
matching declaration must therefore be rejected at the source boundary.

The narrow proposed source-gate tightening is to require the bytes between
the exact checked local method item end and the guard struct keyword to be
whitespace only. This rejects `#[repr(packed)]`, `#[repr(C)]`, other local
attributes, inserted items and aliases before ADT admission, without
changing the generated contract or verification semantics. The guard's
struct body, source span and typed ADT checks remain mandatory. This
overlay is separate from the O17 H2a/H2b patch pair and defaults to the
existing same-root opt-in; it is not accepted until a new hosted run.

## Trust, domain and full target posts

Trust remains the checked frontend mapping from the pinned std method and
source-shaped local adapter to its typed MIR call, plus the selected SAFE
Drop template shape. The local generic method consumes
`thread_token(t) * *slot |-> value * <T>.own(t,value)` and returns
`thread_token(t) * *slot |-> _` on normal and unwind. The selected nominal
Drop returns stock field/padding/thread resources plus precisely the same
optional pointee cell on both outcomes. No runtime body, generic signature,
free drop-glue contract, memory rule, SMT axiom or verifier check changes.
The actual nested DefPath and outer helper cleanup are outside this local
admission matrix.

Positive control: the O17 source-exact local fixture must export/decode both
NORMAL and readonly MIR, refine, pass the H2a source/MIR gate, and verify
with full verifier exit zero. Require the local generic method and guard
Drop to each show two distinct normal/unwind return/leak pairs, owner
constructor and concrete `u32` witness to return/leak, and ordinary Drop
to return/leak in the **same** unit and active profile.

Negative controls are staged, not collapsed into a green count:

| Boundary | Mutation | Intended result |
| --- | --- | --- |
| Local source/ADT | `repr(packed)`, `repr(C)`, private-field visibility/type/extra field, owner declaration/body, guard body annotation | paired export/decode/refinement if the compiler accepts the fixture; exact source/ADT gate rejection before checked method entry |
| Typed MIR | callee `FnDef<T>`, receiver type, `Move(_4)` vs copy/local/projection, destination, normal edge, unwind `Continue`, cleanup bit, extra statement/block, ghost inventory | complete typed-MIR gate rejection before redirect; a source mutant rejected first does **not** count as MIR coverage |
| Owner | missing cell, wrong target, duplicate returned cell | exact owner close or extra post obligation, after source/MIR admission |
| Destructor resource post | demand initialized pointee, retain `<T>.own`, demand a second pointee or unrelated `Element` right; false normal and false unwind post | exact return/post entailment failure after the real generic call, with both branches where applicable |
| Unselected ADT | ordinary Drop in the same exported unit | full proof under the active selected template, stock post and leak checks |

The first row can be exercised by source fixtures. The second row requires
independently altered *typed MIR supplied to the verifier*, while retaining
the admitted source unchanged. Merely changing the Rust body and being
rejected by the earlier exact source gate is insufficient evidence for a
MIR check. No MIR-injection harness is present in O17; therefore no claim
of a complete mutation matrix follows from the existing four source
negatives. A future hosted harness must preserve the original captured
NORMAL/readonly binaries, record each mutated binary and decoder text,
match exactly one intended typed node, and prove each mutant reaches the
MIR gate rather than failing compilation or refinement setup.

The candidate hosted-only `capture-h2b-admission.py` now prepares eight
source/ADT cases; `capture-h2b-mir-mutation.py` prepares one unwrapped
positive and twelve direct typed-MIR mutants using a disposable exporter
wrapper. The wrapper invokes the pinned real exporter, decodes its result,
changes exactly one field in the unique local guard body, re-encodes it,
and records both binaries/texts and hashes. The unwrapped positive must
prove before any mutant starts. Independent original-source NORMAL/readonly
export, decoding and refinement remain on the unmodified tool home. The
shadow verifier's PATH alone selects the wrapper. Any unmatched target,
encode/decode error, profile mismatch, proof entry or different fatal
reason is inconclusive. This is a test-tool mutation profile, never the
accepted runtime proof profile. The runners are prepared, not executed.

Resource-post mutants that alter the *generated AST* need an isolated
negative overlay with exact source-profile pin and a reviewed one-field
AST delta. A caller post that demands an extra resource is useful, but it
cannot by itself establish that the selected template never generated that
resource. Keep the original O17 `retains_initialized` classification and
artifacts unchanged; the narrow classifier amendment applies only to a
new run. Do not mark a setup failure or an unentered Drop body as an
intended negative.

## Outcome-to-decision map

If the source gate admits a layout attribute, tighten it before any H2b
acceptance. If an exact source mutant fails export or refinement, record it
as inconclusive for that gate and choose a compilable fixture; do not count
it as a negative proof. If resource-post mutants fail before the checked
call, repair the fixture. If the selected template returns initialized
storage or `<T>.own`, revise the template and rerun the full local matrix.
Only after this matrix and an independent actual nested source/MIR linkage
may H2b be considered for actual std evidence.
