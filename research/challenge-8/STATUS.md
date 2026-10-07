# Challenge 8: current checkpoint

Updated 2026-10-07. **S7c CFG repair IN PROGRESS**, explicitly authorized from
`070b9236daa3ab5d7176702c9855167b22a06e49`. Diagnose physical dead-code loc identity
on frozen S6v4 before minimal ManuallyDrop::new normal FnCallResult successor fix.
Uninstrumented acceptance requires unchanged source/MIR/refinement, unwind/shared
cleanup/dead-code/false-post controls and existing component regressions.
Budget unchanged:4752/5400 used,648 job seconds remain; no active run.
No actual linkage/redirect or guard/Drop/assume_init/model/exporter/refiner/kernel
extension. [BEFORE card](SORT4-SELECT-FORGET-DESIGN.md#s7c-cfg-repair-before-implementation).
Historical S7b STOP is superseded only within this narrow authorization.

S7b resumed from
`8fdb5799bdd0bbc6bacea5a36567dc71886b6015` under the owner's narrow authorization.
**STOP: complete auxiliary proof is blocked by frozen translation/dead-code acceptance.**
No active run. Auxiliary generic body NOT ACCEPTED; actual linkage NOT ACCEPTED
and no S7 actual redirect. [Report](SORT4-SELECT-FORGET-RESULTS.md),
[design/BEFORE cards](SORT4-SELECT-FORGET-DESIGN.md),
[operating runbook](AGENT-RUNBOOK.md), [roadmap](PLAN.md).

Standalone [37675513854](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37675513854), checked source
`c9c59a85807da0135a8192b1912b15d510c68028`: one generic unsafe forget adapter,
whole unit without focus/macros/select/guard. All seven predeclared bodies execute,
return and leak-check; full VF exits1 with sole
`verified/lib.rs(3,1-16,2): dead code`. NORMAL/readonly export/decode and refinement
exit0; source integrity PASS. Body prefix is not a successful theorem.
Existing ManuallyDrop identity/destructor/no-unwind correspondence remains TRUSTED.

Separate [replay37676357686](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37676357686)/processor
`dd4b0493b8411d92f61f525a3c7ef6ec0429d021` PASS: immutable old run37669436220
logs, all nine original classifications preserved byte-for-byte. New separate map:
two positives INCONCLUSIVE (dead-code exit1), seven intended proof negatives.
Seven classifier controls PASS. This is no new proof or full S7 admission.

AST diagnostic [37678089113](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37678089113),
checked source `a6f077a5aa89ad25df94295320cdbe18ebe4b9d9`, uses only the existing
-dump_ast_with_locs option. It retains the same exit1 failure; source pairs, both
complete MIR files and effective tool hashes match the first run. AST confirms
normal Goto1 and orphan label2/ReturnStmt(unwinding()) at the whole adapter span.
This explains the structural reachability mismatch; printed spans do not identify
the remaining physical loc-table key, which was not instrumented. No missing
ownership resource was diagnosed in this body. STOP without cleanup pruning,
dead-code exemption, syntax variants or semantic/model/tool changes.

Budget **4752/5400 summed hosted job seconds used; 648 remain**, same budget/no reset:
entry4411 + standalone178 + replay12 + AST diagnostic151. This iteration341s.
All executable checks hosted-only, one relevant run at a time. No active job,
no uncommitted semantic draft or actual redirect. Mandatory standalone acceptance
has failed; full S7 actual linkage/matrix is not opened by the diagnostic prefix.
No further dispatch at this checkpoint; a scoped design decision is needed to
reconcile the frozen translated cleanup with the mandatory acceptance gate.

S6v4 components remain accepted from run37656621026, proof source
`75681fbc57bda633f59096cdc28f0c1aa61daef8`, frozen patch
`c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1`.
Pointer-value model, constructor, as_mut_ptr, typed intrinsics and narrow pointer
drop stay accepted within their documented compiler-glue/frontend trust boundary.
Actual stock-projected prefix supplies initialized selected cell via constructors
and stock opens, passes runtime drop60 and closes61/62. It still stops at forget63:
std/lib.rsspec420 requires nominal `<DropOnPanic<*const Element>>.own(t, guard)`,
absent. No guard-own=true, new guard/Drop model or Element/slot rights introduced.
Full S7 nominal source/MIR/call admission, thread/cell/frame/borrow/mutation matrix
and new-profile regressions NOT RUN. Full helper/sort4 NOT PROVEN.

assume_init/general union/Drop/refinement/memory/alias/provenance/kernel remain
outside this task. S5j correction retained: readonly export/decode0, refinement1
RawPtr bb1cmd4; normal preprocessing separately fails after-tail ghost close.
RAPx CLOSED/NO-GO; B/C NOT RUN; no upstream PR/messages/submission.
