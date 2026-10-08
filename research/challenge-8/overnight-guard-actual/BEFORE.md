# Actual nested Drop: six-body source/MIR capture before semantic transfer

O21's exact pointer-specialized actual helper contains the qualified local
`select_unpredictable::DropOnPanic<T>` owner. Its nested Drop has the same
five-local, four-block runtime shape as the independently checked H2b local
Drop: two source-written ghost opens, a copy of `self.inner`, then a typed
`std::ptr::mut_ptr::<impl *mut T>::drop_in_place::<T>` call with `Move(_4)`,
normal bb3 and unwind `Continue`. Its DefPath and ADT are qualified, so the
unqualified H2a/H2b admission must not be reused by name substitution.

The next source-only fixture adds the exact H2a generic unsafe
`sort4_checked_generic_drop<T>` body and its full contract **before** the
unchanged actual function. It retains the actual full normal pointer-value
post, false unwind post, stock `safety_proof`, truthful qualified owner,
actual nested ghost opens, all runtime operations and all S6 local callees.
Its `original` twin is derived by ghost stripping; the actual std body is
checked against pinned `hint.rs`. No runtime or target signature changes.

This capture exports NORMAL and readonly MIR, decodes the complete six-body
unit, checks refinement against the original twin and saves full outer,
nested and generic-callee body records. It installs **no** frontend rule,
redirect or generated Drop template and asserts **no** actual proof. The
expected result is exact source/ghost identity, one ordered generic method,
one qualified nested Drop and explicit normal/unwind call successors.
Missing/extra bodies, changed runtime bytes, export/refinement failure or
absent ghost calls is inconclusive setup, not a proof negative.

Only after inspecting the complete new MIR may a separate default-off gate
pin the full source, qualified ADT, owner declaration and spans, all decoded
unit/body fields, exact generic method contract/body/DefPath, qualified
nested Drop local types/field projection/Move(_4)/call successors, and the
outer shared cleanup inventory. A separate hook could then redirect only
the qualified nested method to the same-unit proved generic callee and
select the generated Drop post that returns `*inner |-> _` along with stock
field/padding/borrow/thread resources on **both** normal and unwind paths.
It must consume the initialized `T` value through real Drop and return no
`<T>.own`; `Element` pointee rights are never introduced. The generic
callee must be proved under `thread + *slot |-> value + <T>.own(t,value)`
with normal and unwind post `thread + *slot |-> _` before its summary can be
accepted for the nested body. The eventual full six-body proof must verify
the qualified nested body before accepting any outer summary, regardless
of lexical verification order. Outer shared cleanup and the real SAFE
forget obligation remain intact.

Future admission controls need exact source/owner/ADT/DefPath negatives,
direct typed MIR mutation of nested `Move`/projection/generic substitution
and normal/unwind edges, plus generated-post resource negatives demanding
an initialized cell, retained `<T>.own` or duplicated storage. These
controls must fail at their intended gate/proof obligation after independent
NORMAL/readonly/refinement checks. This card authorizes only source/MIR
capture; no semantic overlay or proof claim is part of this component.

## O23 complete decoded representation probe (separate patch 16)

The NORMAL/readonly Capnp text records source and control flow, but a
later semantic gate will inspect eager OCaml decoder values. To avoid
assuming the text projection includes every field, the separate,
default-off fingerprint probe runs at the entry to `translate_vf_mir`,
before any S6/owner certification. It accepts only a complete hosted
diagnostic environment: mode 6, 7 or 9; an existing absolute evidence
directory; a caller-supplied SHA256 of the complete verified source; and
the exact ordered DefPath inventory for that mode. The source hash is a
capture-integrity check, not a trusted pin or admission certificate.

The probe serializes the complete eagerly decoded `D.decode_vf_mir`
value and every complete `D.decode_body` value with
`Marshal.No_sharing` into separate files. The hosted capture computes
SHA256 for every byte file after independently successful NORMAL and
readonly export and refinement, verifies source hashes were unchanged,
and records the intentional diagnostic refusal. The probe always
refuses before any proof rule can activate, including on a complete
match. No parsed field is omitted, projected or normalized. These bytes
are compiler/decoder/serializer-profile dependent; later semantic use
requires review of their full representation, an exact pinned source
and compiler profile, and separate negative controls.
