# Third-run preparation repair

Second build c8ae2005-7b50-41fa-a926-0319bf9787e3 reached the first-sort4
boundary in execution traces, but no whole native positive succeeded.
The original inline const compiles to generic Unevaluated constant#0; the
frozen translator gives it an opaque unevaluated_constant<T> value. It cannot
justify the ghost arithmetic assertion len<16. Add a duplicate ordinary Rust
condition using the same pure size_of expression before the retained original
inline-const condition. It selects the same source path in Rust, but its MIR
explicitly supplies the size comparison. The original condition/check remain
byte-identical. This is a diagnostic selector, not a claim that the opaque
constant has been linked in the verifier. The certificate records the inserted
selector, its source basis, and its line; prefix removal reconstructs original
source bytes. Full caller equivalence remains outside this bounded result.

Qualify MaybeUninit in ghost annotations because use aliases are not ghost
bindings in the current translator. Repair control log entry recognition to
count only actual timestamped verification entries, not diagnostic notes;
wrong-equality must fail at an actual assertion, raw-destination at missing heap
chunks. No assertion, owner, frame, type_interp, return or leak check is removed.
Local validation: Python AST parsing and diff whitespace. No local compiler or
proof execution. Fresh Cloud validation required; prior runs are not promoted.
