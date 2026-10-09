# Type interpretation and generic MU storage — independent review

Read-only review by GPT-6 Sol resource_review against source15056f9e and saved
frozen production model, plus exact upstream f76012fb verifast.ml783-802.
No new semantic implementation/proof credit in this note.

Native generated contract (`gen_contract`, saved translator5729-5881) supplies
thread/currentThread, native slice FBC array+owner foreach and F current cell/own,
but no explicit type_interp<T/F>. Stock `produce_type_interp` is admitted in real
functions and nonghost_callers_only lemmas and denied in ordinary ghost lemmas.
It creates a logical chunk without consuming heap resources. Thus using it in
this real caller is an existing trusted verifier rule, NOT a derivation from
caller ownership or Rust type checking. The exact c1 type premise cannot be
reported heap-derived merely because the command verifies. No rule changed here.
Upstream usage: tests/rust/safe_abstraction/tparam_own.rs35. Source handler explicitly
prevents use while proving type interpretation's own obligations. Any produced
chunk needs a truthful disposition for full generated caller post/leak.

Generic MaybeUninit model has only inner(new_maybe_uninit(v))==v, not inverse.
open_MaybeUninit consumes original MU cell and yields optional T cell inner(old).
close_MaybeUninit_ returns new_maybe_uninit(inner(old)). Existing framed opaque
MU own foreach remains about old wrappers. Equal inner does not establish equal
wrapper or matching owner. Pinned byte conversion specs also lack a byte-for-byte
round trip through optional<T>; reconstructing T can change representation/padding.

A checked pure ghost token cannot manufacture the missing full writable byte
permission and original wrapper authority simultaneously. Retaining fractional
original authority conflicts with later full writable T storage. Adding inverse
MU equality or MU.own=true would alter the model and is not justified by current
laws. A truthful later model extension would need exact byte-preservation or
proven owner transfer under actual mutation, plus unchanged/mutated-inner,
same-inner/different-wrapper, ownership-duplication, normal/unwind and leak controls.
No such general model change is made in this entry-phase candidate.

ZST remains legal selected actual branch for len8..15. Source-frame subset needs
no size restriction; exact existing c1 pre requires size>0 and therefore remains
conditional even if storage/type issues are solved. No inference from Freeze
specialization to Copy/purity/no-lawful-alias or no-panic is permitted.
