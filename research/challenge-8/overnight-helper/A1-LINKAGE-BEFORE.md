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

### O11 failure and O12 repair decision, before rerun

O11 first hosted linkage gate: run `37709227889`, proof SHA
`480cb9f10fa8bf11cb70b7f9925e19eaadf6c92a`. The exact combined source
and NORMAL/readonly export/decode/refinement passed for all 15 method cases,
but none reached a function proof. The first frontend certificate mismatch was
`MIR place/projection _2`. There are **two distinct immutable destinations**
in the reviewed O9/O11 graph: callee `_2` receives the constant-size assertion
as an assignment; caller `_2` receives the `assert_inhabited` unit result as a
call destination. The draft graph gate had required mutable destinations at
both sites. The separate linkage patch now requires `_2` immutable at both,
and retains mutable checks for every other assignment and call destination.
This exact-graph correction changes only admission; source, call redirection,
pointer primitive and normal/unwind behavior are unchanged. It needs a **new**
hosted run. O11
source-mutation controls independently produced the exact source-prefix
certificate fatal before any function proof, but their classifier expected a
different exit format and therefore reported `INCONCLUSIVE`. The classifier
now checks the observed exact fatal first line, exit 2, and absence of proof
and unrelated errors. These are pending fresh classifications, not accepted
O11 negatives. O11's two G1 framed positives remain separate diagnostics;
the A1 primitive matrix was not rerun in this job.

### O12 proof result and probe-contract repair, before O13

O12 run `37710354025` proves the exact two-body unit by itself: the checked
`transmute_neo` callee and exact updated-std `assume_init` adapter both execute
their complete bodies, return and leak checks; full verifier exits zero after
mandatory dead-code checks. NORMAL/readonly export/decode and refinement pass,
and both full reviewed MIR graph pins match. The typed redirect is exercised
once. This is a pointer-specialized local method theorem under its stated
initialized-wrapper and pointer-value ownership precondition, not an actual
outer helper or a generic `assume_init` theorem. Three source mutation
controls reject at the exact A1 source gate before function proof.

All 14 probe variants reached the two-body unit. The two positive probes
then failed at their own return leak check because the probe post omitted
`raw_ptr_own::<Element>()(tid,result)`, which the proved method returns.
The frame-loss and thread-loss controls consequently leaked that ownership
as well as their intended missing resource. O12's original classifications
remain INCONCLUSIVE or location-unreviewed. The generator now returns
`raw_ptr_own` in every probe with a successful initialized method call,
without changing the method, primitive, source gate, or target post. The
negative classifier is tightened to one error at the exact probe/adaptor
obligation, requires both callee and method full return/leak traces, and
rejects contaminated leak messages. A fresh hosted run is required before
positive probe and intended-negative acceptance. The `none`/unknown and
absent-thread precondition failures are not inferred from probe success.

Self-review: an alias or import shadow would change the Rust call symbol and
would not establish this obligation. Name-only redirection could prove a
different method body. A result-expression rewrite could erase unwind; use
the existing call outcome path. Do not classify the method as proved until
the combined unit proves the local callee before consuming its summary and
the complete normal/unwind method contract passes.

O9 source/MIR review: run 37707055478, proof SHA `0781cdbd`. The combined
fixture has source integrity and all export/decode/refinement stages passing.
The callee's complete MIR record SHA is the same
`743990d692c78f43b786768f777ea4b7063178732ac8fec119e6e2d26d44d9ea`
as O4/O7, a single block with exact const-size assertion, plain local Move,
one typed Transmute and return. The caller's complete MIR record SHA is
`e50270cdd0ee9b08da77992b67b27a82d7ff57445ef8ab944a0bde3152396f47`:
bb0 calls typed pointer `assert_inhabited` with unreachable unwind; bb1
copies the input into `_3`, calls the real typed std `transmute_neo` with
`Move(_3)`, normal bb2 and `unwind continue`; bb2 returns. The local callee
fully verifies before the caller, which stops precisely at the missing std
function summary. This is the reviewed input for the separate redirect patch.

Patch self-review: opt-in `SORT4_A1_LINK_REPO_ROOT` checks four exact std
source pins, the full O9 callee+caller source prefix, both exported contracts,
generic and local types, and all ordered statements/terminators and successors
of both bodies before enabling one typed call redirect. The hosted matrix also
checks both full decoded MIR hashes. The redirect emits `FnCallOutcome` and
leaves the original MIR unwind inventory in place. A source mutation control
must fail the prefix gate, and a graph mutation must fail either the frontend
graph gate or the separately pinned complete MIR check. A green O10 is still
required; O9 itself is only applicability evidence.
