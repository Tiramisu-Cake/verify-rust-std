# R15 isolated raw-copy ownership fixture

`a1-actual-copy-lemma.rs` isolates one generic `ptr::copy_nonoverlapping`
operation with the stock pinned VeriFast contract. The positive case requires
an initialized source cell and its sole `T.own` resource, plus a writable
optional destination whose current state is uninitialized. Its normal post
retains that same source owner and records the copied typed representation at
the destination without adding a second `T.own` resource. The stock primitive
has `on_unwind_ens false`.

The cases deliberately keep `T` unconstrained: no `Copy`, `Freeze`, size, or
comparator premise is introduced. The duplicate-owner negative requests a
second `foreach(values, own::<T>(t))` after the copy; the missing-source and
missing-destination negatives target the primitive's respective resource
preconditions. Expected stages are encoded as comments for the Cloud runner;
they are not observed results.

This is a checked-contract candidate, not evidence of a pass. O9's recorded
stock-contract result already established optional uninitialized destination
acceptance for an isolated copy (`OVERNIGHT-SORT4-ROUTE.md`, O9 correction);
R15 must independently classify this generic ownership fixture under its
exact profile. It does not prove the actual `sort4_stable` wrapper/call sites,
source/destination separation from Rust borrow provenance, selection,
padding or pointer provenance transport, ZST geometry, or any comparator
normal/unwind path. A successful result may inform a later actual-body
annotation, but is not a usable actual-callee summary.
