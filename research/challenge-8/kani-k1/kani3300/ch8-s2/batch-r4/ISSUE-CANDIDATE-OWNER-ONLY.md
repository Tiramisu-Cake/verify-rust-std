# Owner-only possible upstream issue — unpublished

Source-supported conditional stock mechanism (frozen diagnostic04c61ba): ordinary
FnStubPass replacement of a contracted original can supply a replacement body
without generated contract closures while original-instance contract metadata
still drives closure lookup. This may explain a missing __kani_recursion_check_*
lookup IF the failing unit actually used that body/instance combination.

The actual r3 failing causal CI unit/body is UNKNOWN. Runtime confirmation NOT_RUN;
r4 source changes do not prove either causality or a compiler repair. A minimal
stock-tool reproducer with a contracted target, ordinary stub, exact flags and
captured actual unit/body identity is required before treating this as an upstream
bug report. Preserve a noncontracted ordinary-stub control and an original/verified
control. No reproducer execution, issue, PR or external message is authorized or
performed here. This is only an owner-facing issue candidate note.
