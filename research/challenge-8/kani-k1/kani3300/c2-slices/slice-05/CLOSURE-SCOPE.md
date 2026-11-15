# Closure masks and limits

This slice extracts only the accepted F closure mask implementation. Sized zero-byte
closure environments, including captures consisting entirely of zero-sized values,
have no data bytes. Nonempty environments use monomorphized upvar types and the
closure's own field offsets/order. Padding stays false; nesting composes the enclosing
offset exactly once. Captured references describe the reference storage, not initialized
pointee payload. No all-true environment, tuple-layout substitution or blanket admission
of union/UnsafeCell captures is introduced.

The21 closure-upvars/closure-zst fixtures preserve scalar, reference, raw, padded,
aligned-ZST, MU value/reference, union value/reference, nested and offset cases from F.
Union-as-field and other existing layout refusals remain explicit. Owner1 selected-body,
ordinary entry and cycle logic and owner4 storage/protocol supply the prerequisites;
this slice changes neither protocol nor analysis semantics.

Seven mode fixtures and seven root-composition fixtures retain exact intended SUCCESS
checks and negatives. Recursive ordinary/check paths retain the accepted analysis-cycle
Unsupported boundary; recursive simple-check remains a positive control. Replace caller
fixtures retain their local PFC companions and exact caller selection. Companion presence
does not establish checking, shadow transfer under Replace/RecursiveCheck, or structural
isolation. S5 oracle coverage records all21 old semantic roots, including8 strong cases.

The final F DOCS-MAP has no owner5 export prose segment (and explicitly assigns no
closure-limit sentence). Therefore this slice carries the F closure implementation/test
comments and this research scope note. Existing shared user docs remain unchanged;
owner6 general/mode/cycle/Scope A prose and edge README remain6. Adding temporary prose
would break lossless exact-F composition. No new support promise is made.

All runtime outcomes on this cumulative head remain PENDING. The accepted4 receipt
closes its own earlier obligations; the47 head5 obligations and S5 sensitivity4/4 require
exact-head native evidence from the coordinator. F7 is absent and no structural isolation
credit is inherited from frozen F.
