# Remaining actual caller applicability

Read-only independent analysis of source, frozen contracts and saved native/C1
logs. Native source/F/frame resource entailment is complete, but neither native
standalone lemma nor bounded C1 is a callable actual-caller/sort4 summary.

Stock produce_type_interp in frozen verifast.ml783–803 permits a checked pure type
in a real Rust function (ordinary lemma contexts restricted). Saved bridge reaches
T/F producers46–47 and asserts95–96. This provides logical type interpretation,
not own/storage/heap resources; no new producer or trusted axiom was added. Whole
bridge still fails and these observations alone are not completed bridge proof.

The raw C1 pre additionally needs positive T size and array_<T>(dst,4,options).
Native scratch remains array/foreach MaybeUninit ownership. Existing opening
reaches optional T storage and checked identity helper but restoring native MU
requires new_maybe_uninit(inner(old))==old (failure105), not supplied by stock
one-way inner(new(x))==x. Keep opaque native MU frame for source-only subset;
do not fabricate inverse equality or MU ownership. Frozen optional dst pre/post
cannot simply disappear because C1 has no destination writes.

Original SmallSort source230 scratch guard and241–255 source selection remain
unproved CFG conditions. Source selects sort4 for every len8–15, including ZST;
positive-size C1 proves only non-ZST subset. This source observation is not an
opaque inline-const equality in typed MIR; no duplicate condition admission was
used. Generic runtime layout/ZST belongs to merge owner and is untouched here.

After an actual callback, source owners and F state must be CURRENT existential
values, not equal to entry values. Native no-write/read segment preserves original
values; that equality cannot cross FnMut. Full composition needs source-linked
caller entry with exact actual guards, destination permission/frame restoration,
then a sufficiently complete actual sort4 result. Current two partial theorems
must never be used as full function summaries.
