# Fresh actual sort4 graph capture — diagnostic card

The actual obligation is the unchanged `sort4_stable<T, F: FnMut(&T, &T) -> bool>`
in `library/core/src/slice/sort/shared/smallsort.rs` at std blob `40939f9`.
O24 reached its complete body and first refused the source-written reserved
`__vf_sort4_first_unwind` marker. The hypothesis for this Cloud capture is
that the same exact source, paired complete typed MIR, and refinement can be
recovered independently of the actual select proof on the separately identified refreshed owner
profile (frozen20 plus certificate deltas21/22, owner opt-ins disabled here). The source/MIR candidate checker may then record a fresh **proposal**
for review; it grants no frontend semantics.

The fixture's explicit diagnostic domain is `size_of::<T>() > 0`, four
initialized source cells with exactly one `T.own` each, optional writable
destination storage, current `F.own`, thread and type interpretations. `T`
has no Copy/Freeze bound, and legal comparator state/interior effects, normal
answers and panics remain possible. Its active normal post preserves current
source ownership, optional destination and current comparator ownership; this
is deliberately partial. The full normal target additionally initializes
four destination representations without duplicating `T.own`. Each of the
five full unwind targets returns current source ownership, optional
destination before any body copy, current comparator ownership and no borrow
debt. The fixture does not prove either full target or generic/ZST coverage.

Run `actual-sort4-capture.py` only inside the owner-authorized Cloud Build
with `--proof-root`, `--cloud-dir`, `--tool-home`, `--schema`,
`--compiler-sysroot`, `--evidence`, and `--deadline-epoch`. The proof checkout
is disposable. The driver pins the preparation, capture, admission and
checked-lemma inputs; replaces only the two obsolete GitHub provider guards
with the identified Cloud guard; clears callback/HRTB/CUT opt-ins; and invokes
the existing first-call preparation with fresh NORMAL and readonly exports,
decodes, full graph inventory and refinement. It then runs the existing
first-call source/MIR candidate audit without a reviewed admission manifest
and independently invokes the full verifier on that isolated fixture. The
complete original/verified source, binary and text MIR, graph records, stage
logs, tool/profile pins, exact first error and guard-only overlay diffs remain
in evidence. All five FnMut, eight select and four copy calls must remain.

The expected positive capture is exact O24 source and whole-function graph
hashes, all export/decode/refinement stages zero, candidate classification
`CALIBRATION_REVIEW_REQUIRED`, and the first full-verifier error on the
reserved marker in the named `sort4_stable` body. A source/graph mismatch,
audit parser refusal or different first error is inconclusive and must be
preserved. The existing preparation source mutation must reject the changed
first comparator at its source certificate; no intended proof negative or
semantic component is accepted by this capture.

If the marker is later given a separately reviewed handler, stock VeriFast
checks the normal FnMut result branch before the unwind branch. The current
normal path lacks an accepted early lifetime exit before `c2`; a normal
failure can stop the verifier before the direct unwind handler executes.
That failure must be reported as the first actual blocker, not as an unwind
proof. This capture changes no kernel, verifier semantics, runtime std source,
postcondition, workflow trigger or accepted component status.
