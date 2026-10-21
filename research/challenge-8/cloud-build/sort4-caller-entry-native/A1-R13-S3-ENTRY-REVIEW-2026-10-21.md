# R13 S3 entry-cleanup review

## Decision

**GO for the bounded S3 source hypothesis.** The delta moves the already checked
generic ghost cleanup to function entry for the generated P0c and false31
observers and the P1 caller, and removes the later duplicate cleanup calls. I
found no runtime-source change, new ownership assumption, or scope expansion
to the real quicksort body.

## Review

The generated observer source is built from the pinned quicksort signature and
guard prefix, cut before the original `small_sort` call. In that cut,
`left_ancestor_pivot` is not read after entry. The P1 diagnostic caller retains
the signature and threshold/`small_sort` call prefix, then cuts before the
non-base continuation; it also does not use the pivot after entry. A single
entry call therefore consumes the arbitrary `Option<&T>` resource once before
the threshold call and, for P1, before `small_sort`. It covers both returning
and unwinding paths through those calls. The bounded S2 log records the
threshold call’s returning and unwinding outcomes and still reports
`Option_own` at the function return after the exit-only calls. The pinned
translator models those outcomes in separate branches and attaches ghost
statements at their source positions, supporting the placement hypothesis.

This remains diagnostic-only. The full source quicksort later reads the pivot
at the ancestor comparison and assigns `None` on one path, so moving cleanup to
entry in that complete algorithm would not be justified. The fixture keeps the
source-derived signature, retained runtime call/guard order, intended
assertions and returns. Its helper consumes both `None` and `Some(&T)` through
the reviewed shared-reference ownership representation; no None-only premise,
Copy/Freeze restriction, assumed bridge, postcondition weakening, or runtime
drop was added. The cleanup annotation is ghost-only and the tests compare the
ghost-stripped observer and P1 source with the expected runtime bytes.

The emitted positive fixture source also changes for P0a/P0b/P-dispatch because
the fixture builder deliberately shares one positive source unit; their target
allowlists remain unchanged, and the source generator enforces byte identity
across the positive cases. This does not widen their proof targets.

One non-blocking editorial remnant: the P1 cut comment still says the checked
cleanup is at the tail even though the annotation moved to entry. It has no
runtime or proof effect, but should be renamed when convenient.

## Validation and limits

I ran the focused source-construction test file: **6 tests passed**. The tests
check one entry annotation before runtime calls, no exit duplicates, unchanged
runtime bytes after ghost stripping, both observer assertions, and P1’s retained
runtime prefix. No compiler, exporter, preparer, verifier, or Build was run.
The tested helper body’s earlier S2 result is not an S3 caller result. This
review approves only the bounded placement hypothesis; S3 must still establish
the same-Build P0c caller receipt and the required native P1 gates, and no proof
credit follows from these synthetic checks.
