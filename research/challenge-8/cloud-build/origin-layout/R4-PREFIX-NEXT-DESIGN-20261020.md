# Next prefix coercion decision — design only, NOT IMPLEMENTED

R4 authorizes only the address-taken continuation fix. This proposal requires a
separate explicit scope/profile decision. It does not repair or rerun prefix in
R4 and does not assume a successful slice/as_mut_ptr callee after the cast.

## Exact consumer and current failure

b2_three_from_local at verified214 converts local_5: &mut [u64;3] into
local_4: &mut [u64]. Both decoded regions are erased. AST895 strict target-type
checking rejects its InferredTypeExpr. Actual local values StorageLive creates
an address with metadata_none; the sized-source cast is identity Upcast. It
supplies no equation establishing length3. R4 cont locals cannot repair either.
Full CURRENT false/true/firstContinue-panic posts remain the actual target.

## Proposed bounded implementation sequence, after approval

1. Preserve the actual compiler PointerCoercion subtype in the existing schema/
   exporter/decoder. Current unit pointerCoercion erased it. Require Unsize for
   this route. **Source/type identity alone is not yet a justified replacement**
   for that lost discriminant; choose the explicit subtype scope rather than
   admitting every generic PointerCoercion. Compiler/dependencies stay pinned.
2. Add an explicit checked cast-lifetime ascription hook: attach a ghost binder
   to this exact body/source span/MIR assignment, not to later as_mut_ptr args.
   For the real local-array wrapper establish a local k_values using existing
   begin_lifetime/checked borrow operations after values StorageLive; link the
   named lifetime to that live source borrow. End/close it on every normal and
   unwind exit. Never choose static or merely substitute an arbitrary token.
   The annotation only names a lifetime; it grants no heap/token/borrow resource.
3. Require exact source hash/body, span, Unsize category, lhs_4/move_5 with no
   projection, source mutable array3/u64, destination same-element mutable slice,
   type substitution and checked local-lifetime identity. Reject mismatches;
   do not broaden the existing CURRENT18 matcher or general inferred casts.
4. Build the slice value with correct data/provenance and length3. Existing
   std::ptr::slice_from_raw_parts_mut contract (std/lib.rsspec642–645) is a
   candidate representation operation: result as *u64 == data, result.len()==3.
   It is not yet authority to synthesize a reference/borrow. Justify reuse as a
   representation lowering and prove applicability; no blanket new model axiom.
5. Prove, with existing checked resource/borrow lemmas or a newly **verified**
   proof lemma, the equivalence between the source array full-borrow content and
   slice_full_borrow_content(t,fatptr): same physical array cells, owner values,
   data/provenance, len3 and lifetime. Open/reclose/restore the real borrow and
   token fractions on both exits; no ownership from numeric pointer equality.
   If the frozen model cannot express that checked bridge, stop for a separate
   precise model decision instead of hiding it in lifetime/type inference.
6. Keep the strict CastExpr fallback. Only the exact validated route gets the
   typed lifetime and metadata construction. No source/runtime rewrite of
   values.as_mut_ptr, algorithm/generic signatures/CFG or final posts.

The proposed separate scope explicitly includes the subtype schema/exporter/
decoder and cast-ascription/lowering frontend. It does **not** pre-authorize
kernel, alias/layout model, refiner, prelude or CURRENT18 changes. Any need for
those is an additional decision. Resulting pins/closure and a new independent
review precede Cloud. No inherited proof/profile qualification from R4.

## Minimal future Cloud reproducer and exact resource post

The first probe has an input values: &'a mut [u64;3], creates view: &'a mut
[u64], asserts view.len()==3, then executes the real view.as_mut_ptr. It is a
separate diagnostic, not the actual prefix theorem. Let the entry resource be

P = thread_token(t) * type_interp::<u64>() * [q]lifetime_token('a)
    * full_borrow('a, <[u64;3]>.full_borrow_content(t, values)) * caller_frame,
with 0<q<=1 and an actually established source reference/borrow.

**Normal post P; unwind post P**, preserving exactly that token fraction and
caller frame, no remaining local view loan or leaked lifetime token. The probe
has no writes, so restoring the original array content is justified by its
body; this is not an entry=CURRENT premise for effectful F in the real prefix.
The normal path must establish length3 and data/provenance equality before
using the pointer. Unwind checks stay enabled, including the assertion CFG.
This is the exact logical contract for the design; it is not injected source
or an assumed new lemma. Generated in-out reference contracts must be checked
against this full-borrow representation during implementation.

Gates: frozen baseline gives the known strict-lifetime failure; new exact
positive passes through length3 and real callee with full resource return.
Wrong length assertion fails at the assertion after successful setup. Reject
other coercion subtypes, arrays0/4, wrong element/mutability/body/hash/span/local/
projection/binder, absent annotation, dead lifetime or missing physical owner;
no resource from equal numeric addresses. Include normal/unwind return and
loan/token leak negatives. Finally run actual prefix false/true/firstContinue-
panic CURRENT posts plus all4resource/CURRENT18/HRTB/official-unwind/late-Cleanup/
B1/helper/smoke/default-off/receiver/end/retirement controls on compatible final
identities. No acceptance by combining incompatible historical candidates.
