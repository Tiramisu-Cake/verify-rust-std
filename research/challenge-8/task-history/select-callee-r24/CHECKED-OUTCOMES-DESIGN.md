# R24 checked pointer call outcomes

Defect: the first R24 positive proof reaches outer return and leak-check, then
reports the same three dead-code sites. The emitted AST inventory maps the
reported source coordinates to cleanup label 28: the unwind return at lines
135–236, the drop at 235, and its `If` branch. This is a source-reported
coordinate mapping; the AST text does not establish physical or parser-input
identity, and the cause remains a hypothesis pending a Cloud proof. Raw MIR
retains all ten cleanup incoming edges (seven erased-ghost edges, forget,
pointer-drop, and `MaybeUninit::assume_init`). The emitted AST has two incoming
references to label 28, from the pointer-drop call and assume_init call. Both
are redirected to local checked bodies with explicit `on_unwind_ens false`
contracts; the ordinary verifier must still verify these bodies in the same
unit. Their translated `FnCallOutcome` nodes nevertheless retain the cleanup
edge.

Applicability: a new explicit flag enables this narrowly for the exact R24
session, existing R21 route, certified fractional nine-body const-pointer
route, and the already enabled PointerDrop, A1Nine, and A1Link certificates.
It also requires unwind paths to be enabled. The flag defaults off and any
partial, malformed, or wrong-route opt-in is rejected. Only the two exact
already redirected calls in `select_unpredictable` are projected.

Invariants: preserve admission of all ten raw MIR cleanup edges and use the
existing checked-result treatment (`result_of_outcome`)
already used for G1 and checked owner calls. Keep the typed const pointer,
plain `Move` operand, destination, normal target, cleanup target, call
specialization, and source/MIR/certificate checks exact. The two translated
calls become checked results and contribute only their normal target to the
translated successor inventory. Their raw MIR cleanup edges remain present
and admitted by the original checks. Both checked callee bodies remain in the
unit and are verified normally; no assumed summary is introduced. No generic
T, other drop, callback, source, ghost, ownership, or postcondition behavior
changes. Counters reset per unit and final translation requires one match at
each site. The mode emits a distinct marker that states raw MIR cleanup edges
remain.

Alternatives rejected: suppressing checker diagnostics would hide the actual
control-flow mismatch; removing the raw cleanup edges or changing source/MIR
admission would alter the certified input; adding a trusted premise or
assuming a callee summary would weaken verification. This patch only reflects
the already certified false-unwind result in the translated CFG.

Controls: independent static review must audit wrong phase, route, flag,
missing certificate, wrong fractional/body route, pointer depth/mutability,
operand, callee, destination and edge drift, and duplicate/missing counts.
The retained static tests reproduce patch/result hashes; they do not execute
these OCaml guards. Real Python callback tests check flag scope and environment
cleanup. Cloud must compile the translator and execute positive plus all seven
controls with ordinary callee verification. Source, raw MIR and ten cleanup
edge admission checks remain in place. No local toolchain run establishes
formal behavior. Default-off baseline AST is retained as an ablation, with
no parser-input identity or causal proof inferred from textual coordinates.
