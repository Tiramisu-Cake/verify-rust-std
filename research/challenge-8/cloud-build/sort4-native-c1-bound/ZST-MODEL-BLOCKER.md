# Native C1 ZST blocker — localization, no semantics patch

DRAFT pending fresh physical-ID and callback-free controls. This is a minimal
review handoff for the VeriFast maintainer; no peer profile imported and no
publication/message sent. Source-specific binding alone currently has no
established admissible repair preserving native opaque scratch and every branch.

## Pinned static chain

Tool HEAD f76012fb518703b1d98e243ac4f487f16877cfcb; effective kernel37ed2550,
translator381e80eb (full pins in NATIVE-C1-BOUND-TOOL-MANIFEST.json). Frozen
`src/verifast1.ml:6500–6519` creates an axiom for **every declared struct**:
`0 < sizeof(struct_typeid(args)) <= max_uintptr`; args are quantified.
`sizeof_core` represents both generic parameter T and StructType through
`sizeof(typeid)`; generic sizedness alone supplies no positive-size condition.

Stock `bin/rust/std/lib.rsspec:429` declares `struct MaybeUninit<T>`.
At478–480, automatic `size_of_MaybeUninit` equates its size to `size_of<T>`.
The frozen translator's `translate_adt_ty` StructKind/UnionKind mapping at791–817
also represents actual Rust union MaybeUninit as StructTypeExpr; actual std
`library/core/src/mem/maybe_uninit.rs:355–358` is a union, admitting ZST layouts.
This combines to positive T size when the MU size term is introduced.

Native scratch contract is `array<MaybeUninit<T>>(strip_metadata(scratch),
ptr_len(scratch), values)` with foreach owners. In raw3521 target entry, the
source141 scratch array invokes stock array_inv before source145 size guard;
array_inv post includes `count * size_of<MaybeUninit<T>> <= isize::MAX`.
Stock size_of contract itself only returns size_of<T>; it has no nonzero req.
Source FreezeMarker, FnMut lifetime/type binding and CFG correction impose none.

The precise auto-lemma trigger event is not printed in old verbose2 logs. The
static axiom/equality chain is verified; its instantiation in3521 is inferred
from the entry term and zero-branch pruning. Fresh diagnostic evidence below
must distinguish observed physical IDs/queries from this inference.

## Required preservation and scope

Actual original root131 Goto63 afterLabel3 is only the old candidate, not yet
an observed physical ID. Never remove ZST return, add assume(size>0), merge its
location with a visited node, or suppress dead-code checking to obtain green.
Native source/F/thread/type resources must remain derived from safe entry;
scratch MU opaque. No MU/reference inverse or optional-T adapter needed.

Any repair of the unconditional struct lower bound, union/layout representation,
MaybeUninit model, triggers or kernel is a general semantics/model change.
Current owner assignment allows diagnosis only there. A maintainer proposal
needs its own rationale/admission/regression gate including generic ZST, unit,
MU<()> and ordinary nonZST/normal/unwind controls, before this target is rerun.
No connected C4 extension until full native C1 exit0 with retained paths/checks.
