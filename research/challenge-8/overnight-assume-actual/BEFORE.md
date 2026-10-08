# Nine-body actual helper source/MIR calibration: before hosted run

This hosted-only calibration extends the seven-body actual nested Drop and
owner-preserving `forget` source fixture with the two already source-certified
A1 adapters. It does not enable an A1 linkage rule, a guard/forget redirect,
or any other semantic component; it does not verify the actual helper body.
The std `select_unpredictable` runtime body, generic signature, normal and
unwind posts, stock `safety_proof`, nominal guard owner definition and nested
Drop annotations must remain byte-for-byte the seven-body fixture suffix.

The intended body order is:

1. `sort4_certified_maybeuninit::sort4_checked_maybeuninit_new`
2. `sort4_checked_as_mut_ptr`
3. `sort4_checked_pointer_drop`
4. `sort4_checked_generic_drop`
5. `checked_transmute_neo_pointer`
6. `checked_assume_init_pointer`
7. `checked_forget_owned`
8. `select_unpredictable`
9. `<select_unpredictable::DropOnPanic<T> as std::ops::Drop>::drop`

`prepare.py` calls the seven-body source builder with its owned-forget option,
then takes the exact specialized transmute and method adapter declarations
from `prepare-assume-init-2610.py::linkage_fixture_source`. It adds only the
crate feature names and imports those already required by the A1 two-body
fixture, without duplicate `MaybeUninit` or `intrinsics` aliases. The two
A1 bodies retain their existing contracts and exact source certificates.
The actual helper still calls the real std `transmute_neo` and `assume_init`;
placing local adapters in the same source unit is not a call redirect.

The falsifiable immediate hypothesis is only that this expanded source unit
exports all nine complete typed MIR bodies in both NORMAL and readonly modes
and passes original/verified refinement with the pinned actual std body
unchanged. `capture.py` records the full decoded unit and each complete body,
their hashes, precise order and source hashes. Optional fingerprint mode
invokes the reviewed diagnostic-only NoSharing dumper after both exports and
refinement; its intentional refusal is not a proof result. A missing body,
different order, source mismatch, export/refinement error, unexpected
verifier result, or missing fingerprint artifact is inconclusive.

The historical A1 linkage admission pinned a different two-body source unit
and cannot be reused for this nine-body fixture. Any future semantic use
requires a fresh source/complete MIR/AST correspondence certificate for the
whole nine-body unit, separately reviewed actual helper, cleanup and owner
transfer rules, and new positive and negative gates. In particular, the A1
method remains pointer-specialized; this does not establish generic
`MaybeUninit<T>::assume_init` or a whole helper proof.
