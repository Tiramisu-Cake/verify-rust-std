# H_align: concrete Rust ZST versus the pinned VeriFast model

Read-only audit during the 2026-10-07 bounded no-patch phase, checkpoint f1c0774.
Pinned source809de4596839b739dd999f9e462242c835e3af46; no tool patch or execution
accompanies this audit. Hosted results and concrete proof progress are recorded
separately in [results](SORT4-ALIGNMENT-RESULTS.md).

## Source-to-model path

The original type stays `#[repr(align(8))] pub struct Z;`, with Rust size0 and
alignment8. Those are properties to calibrate in the model, not new proof premises.

| Stage | Pinned implementation / saved evidence | Consequence |
| --- | --- | --- |
| Rust fixture | Original/verified sources of37532204465, concrete Z cases | Empty original type with explicit alignment8; no replacement type or annotation layout assumption |
| Exporter | [lib.rs:1100](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/rust_frontend/vf_mir_exporter/src/lib.rs#L1100) serializes adt_def.repr().c() | repr alignment8 is not exported as an ADT layout fact |
| Wire schema | [vf_mir.capnp:269](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/rust_frontend/vf_mir/vf_mir.capnp#L269), AdtDef ends with isReprC | No size/alignment or repr(align) field; saved decoded Z has empty fields/isReprC=false |
| Translator | [vf_mir_translator.ml:6043](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/rust_frontend/vf_mir_translator/vf_mir_translator.ml#L6043) | Reconstructs VF StructType from fields; attaches only ReprC here, not alignment8 |
| Size/alignment expressions | [verifast1.ml:6465](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/verifast1.ml#L6465) | Struct sizeof and alignof are symbolic functions of typeid |
| Struct size assumption | [verifast1.ml:6508](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/src/verifast1.ml#L6508), unconditionally generated _size_limits | 0 < sizeof(Z) <= max_uintptr; fieldless nonpacked struct gains no equation size0 |

The positive-size fact is incompatible with the actual empty Rust type. The
observed failure at `assert size == 0` in37532204465 and37535499783 therefore has a concrete
model cause. `align==8` was not reached, but the missing exporter/schema/translator
fact already explains why it cannot be inherited from the original repr attribute.
No claim of a new hosted misalignment miss or a std runtime bug follows.

## Why pointer limits fail

[prelude_core.rsspec:189](https://github.com/verifast/verifast/blob/809de4596839b739dd999f9e462242c835e3af46/bin/rust/prelude_core.rsspec#L189)
defines typed pointer add through byte add of i * size_of(T), preserving provenance.
The concrete fixture supplies a zero-count array_<u8>; array__inv exposes limits
at base and base+0. It does not promise an additional positive-sized range.
Because the concrete model's size(Z) is positive/symbolic, i>0 can move beyond
that range. This explains the failed pointer_within_limits(ptr_add_(base,i,Z_type_info))
obligation at both37532204465 and37535499783 .add line21. This is a source-model
explanation; the logs alone do not prove one failure causally implies the other.
Actual Rust ZST arithmetic would have zero
stride; no numerical address rewrite or added typed resource is justified here.

Existing is_valid_layout_size_of_align_of and size_align provide nonnegative size,
positive power-of-two alignment and divisibility. They do not derive this exact
struct's size0/align8; deriving size0 consistently would contradict _size_limits.
A checked lemma cannot repair the missing representation fact against that axiom.
Assuming size0/align8, changing Z, manipulating repr/model attributes, or accepting
an inconsistent proof context is outside this no-patch phase.

## Scope of the boundary

The concrete ZST layout/add control cannot be closed faithfully under the present
model and unchanged contract. A future decision would need a reviewed correction
to Rust layout encoding and the struct-size model, with admissibility/regressions,
or another separately justified independent component. No extension is implemented.
Do not add layout assumptions to the adopted caller contract or exclude ZST.

This does not refute independent generic arithmetic geometry. Symbolic generic
size0 remains in that theorem's input domain. Its checked local hypotheses must
come from the original byte/provenance/valid-layout resources. Even a generic pass
cannot silently instantiate a faithful concrete-Z model that the tool lacks, prove
automatic copy UB detection, or close ownership/reference/unwind requirements.
The strict header/assertion replay controls are another independent diagnostic.
RAPx remains CLOSED / NO-GO and B/C NOT RUN.

Latest hosted continuation37535499783/sourceea635ea completed in38s,1/3 NEW slots.
Checked generic helpers/local bounds and i=1,2,3 branch posts/leak checks pass; the
residual generic alignment post remains INCONCLUSIVE. Classifier replay and both
intended negative controls pass separately. Phase CLOSED at this concrete boundary;
unused slots retired, no patch or additional run. The recommended next decision is
a minimum-scope trust/admissibility review of faithful Rust layout encoding versus
an independent component. No proof from an inconsistent size context is acceptable.
