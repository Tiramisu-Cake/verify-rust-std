# M2 capture admission: exact open trust obligation

Read-only reassessment of f760 plus the frozen six-component profile. No new
kernel rule, callback restriction or acceptance is introduced here.

## Problem and pinned representation

cleanup.patch strict exit rebases/checks only Chunk.targs, retaining predicate
symbol, coefficient, argument terms and optional size unchanged (lines646ff).
The patched kernel's Chunk field order is (predicate symbol, type arguments,
coefficient, argument terms, optional size). A lifetime_token can have empty
targs and a physical lifetime in terms; the field distinction is real.
Outer-variable filtering checks type, not value-term/capture provenance.
This is a missing closure argument, not an established accepted counterexample.

The frontend's exact callback whitelist rejects added ghost commands and
matches physical cmp_k, T, source references and tuple operands. Unclosed
(&'cmp T,&'cmp T).own exposes the local lifetime in targs. Explicit borrow
with a lifetime-dependent predicate constructor is already represented by
cleanup-cases.rs callback_cleanup_predicate_term_hidden_type, with expected
frontend refusal. Its failure cannot count as a proof-negative or kernel
counterexample. Exact protocol restores ref/tuple resources before leaving the
scope; end_lifetime/borrow_end run outside using the physical cmp_k token.

## Remaining producer obligation

The actual callback post yields opaque current F.own(t,f1), and recovered
current T.own(t,lv1/rv1). Source syntax alone establishes neither predicate
constructor closure nor term/coefficient/size provenance of those chunks.
We have not established a feasible admitted callback output retaining a local
binder after successful end_lifetime. Kernel soundness and unsoundness both
remain unproved at this boundary. A Boolean value depending on a comparison
is not itself a lifetime capture, so a textual cmp_k search is insufficient.
Solver pretty-printing cannot serve as a sound recursive closure checker.

## Conservative next component, before implementation

A separate admission certificate could classify each strict-exit chunk by:

* structurally unchanged entry frame with outer-typable producer;
* enumerated physical-token lineage, exact matching close/end/borrow recovery;
* fresh or changed output with an independently lifetime-closed producer summary.

Refuse any unclassified new/changed output. This would likely refuse arbitrary
current F/T outputs until their producer is justified, which is an honest
missing theorem rather than a reason to weaken normal/unwind posts or freeze
F. Pin the term/coefficient/size representation, predicate-constructor capture
semantics, and callback summary producer first. Define feasible positive and
exact admission-refusal controls before writing this component. Do not broaden
kernel erasure or treat type-only regression counts as this argument.

## Independent permitted progress

Native arbitrary-n two-hole extract/restore needs only current source values
and existing element-owner resources. It excludes callback/destination capture
and this lifetime cleanup route. Its checked component may advance source
partitioning without settling M2, C1/F frame or actual arbitrary-n merge.
The direct Drop count-n copy similarly does not prove ownership acquisition;
bytes copied under the stock summary are current bytes, not T.own creation.
