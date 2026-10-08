# A1 transmute call linkage — BEFORE

2026-10-08. O7 verified the exact pointer-specialized local
`transmute_neo` body, with O4-reviewed complete MIR graph, full normal and
readonly export/decode/refinement, return, leak and dead-code checks. The
independent symbolic and framed body proofs also passed; their ten intended
proof negatives failed at the expected primitive preconditions, postconditions
or leak obligations. The actual-source `assume_init` adapter remains blocked
at its call to `std::mem::transmute_neo`; no actual call linkage is claimed.

Obligation: retain the actual `assume_init` body and its MIR call to the
unstable public `std::mem::transmute_neo::<MaybeUninit<*const Element>,
*const Element>(move _3)`. The call's normal successor and `unwind continue`
must stay in the MIR graph. A local callee candidate in the same verification
unit must retain the exact `transmute_neo` body specialized only by the two
type substitutions and have a separately proved full pointer contract.

Proposed correspondence: after certifying both exact source bodies, the
updated std source/layout/intrinsic pins, and complete typed MIR records,
redirect only that typed method call to the local proved callee summary.
The redirect shall preserve `FnCallOutcome` and its existing normal/unwind
successors. The local callee's false unwind post is proved by its body and the
narrow pointer primitive. The method's own post remains the exact complete
pointer value, raw-pointer value ownership, current thread and no unwind.
No `Element` cell is granted. No generic `transmute_neo` summary is trusted.

Trust boundary: the primitive's physical representation correspondence
remains trusted and separately source pinned. The call redirect itself is a
trusted frontend correspondence between the original std symbol at this one
typed callsite and the proved local specialization. The certificate must
reject changed body text, contract, source versions, function identity,
generic types, argument shape, call count, local declaration type, MIR graph
or unwind structure. The next hosted run first captures both functions in
one unit without redirection; no proof acceptance follows from capture alone.

Controls after implementation: unchanged symbolic and independent-frame
method posts pass; `none`/unknown initialized value, false/wrong result,
frame/thread loss and duplication, and added `Element` rights fail at the
specified proof obligation. Wrong source/destination/pointee, mutable raw
pointer, Copy, projection, changed source body or call graph reject admission.
S6 full profile and standalone A1 primitive matrix must continue to pass.

Self-review: an alias or import shadow would change the Rust call symbol and
would not establish this obligation. Name-only redirection could prove a
different method body. A result-expression rewrite could erase unwind; use
the existing call outcome path. Do not classify the method as proved until
the combined unit proves the local callee before consuming its summary and
the complete normal/unwind method contract passes.
