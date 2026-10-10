# Resource boundary: native entry versus bounded C4

This is an address-based source/spec review, not a fresh proof verdict. The
first diagnostic is Build `07e046f8-3d43-4016-8f83-f6429a5bd9a2`, proof/infra
`538662831180e6b21549c12b3d1275872fc56c28`; its raw outcome is reviewed separately.

The native boundary is the actual safe signature of
`small_sort_general_with_scratch` at SmallSort line 220. Its automatic contract
owns the source slice, the scratch slice of `MaybeUninit<T>`, the comparator
reference and the current thread resources. The original `FreezeMarker` bound
is retained; it is not an extra purity or callback restriction. Splitting the
source array and its `foreach` owners at four transfers actual permissions.
An equality of the pointer value alone cannot supply those permissions.
The stock `produce_type_interp<T/F>` calls introduce logical type chunks;
they are not inferred from the native heap and are explicitly disposed of.

The bounded C4 pre is `MEMORY_PRE_CONTRACT` in `overnight-sort4/capture.py`:
current thread/T/F types, positive T size, initialized source4 and T owners,
optional T destination4, comparator cell and F owner. Its full normal/unwind
posts existentially recover CURRENT source, destination and comparator values.
They do not assert equality to entry snapshots. Its normal return currently
closes a bounded prefix, not initialization of the whole destination by the
remaining sort4 body.

Actual preparation at SmallSort lines 225–254 reads length, has early return
and scratch/abort guards, obtains both slice pointers, divides length by two,
casts the scratch pointer and selects sort8 versus sort4. A proof of a ghost
`len>=8` diagnostic proves neither those guards nor the native call edge.
The selected condition implies four source and scratch elements. It does not
imply positive T size for lengths 8–15. For lengths at least 16 it implies
size greater than 16. ZST/layout work remains separate and no size fact is
added as a substitute for the missing unrestricted transition.

MaybeUninit size/alignment equalities are already stock specification facts.
They do not turn a native MU array/owner into optional T storage. The checked
stock open lemma transfers one cell to optional storage; close reconstructs
`new_maybe_uninit(old.inner())`. The stock left inverse proves preservation of
`inner`, but does not supply the right inverse for arbitrary old wrappers.
Native mutable-reference posts can permit CURRENT wrapper values rather than
the exact entry list; nevertheless their matching MU ownership must also be
restored. A one-cell storage roundtrip alone proves neither that owner transfer
nor the full scratch-array/native post. No failed exact-old helper may be used.

Before C4, the runtime prefix does not touch destination storage. Retaining
the original MU array and its opaque owners as a frame therefore avoids any
runtime need for a wrapper inverse. A prefix interface using that frame would
require its own proof and fresh source/MIR/AST correspondence; it is not the
existing optional-T C4 theorem and is not implemented here. The frozen C4
binding rejects altered files and explicitly forbids callable-summary credit.
Neither a resource identity lemma supplied with fresh raw C1 inputs nor an
ordinary call to the truncated sort4 body would bridge this control-flow gap.

The historical strict-cut draft is excluded. Existing C4 strict semantics
support the prior four callback boundaries; native resource cases turn those
bounded projection flags off. No evidence currently establishes that a new
strict-cut rule is necessary for this resource transition. Any new rule or
combined projection is a separately reproducible blocker, not an implementation
permission in this session.
