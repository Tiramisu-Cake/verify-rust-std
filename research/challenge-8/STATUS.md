# Challenge 8: current checkpoint

Updated 2026-10-07. S7b resumed from
`8fdb5799bdd0bbc6bacea5a36567dc71886b6015` under the owner's narrow authorization.
**IN PROGRESS: one frozen-profile AST provenance diagnostic is being prepared.**
No active run. Auxiliary generic body NOT ACCEPTED; actual linkage NOT ACCEPTED
and no S7 actual redirect. [Report](SORT4-SELECT-FORGET-RESULTS.md),
[design/BEFORE cards](SORT4-SELECT-FORGET-DESIGN.md),
[operating runbook](AGENT-RUNBOOK.md), [roadmap](PLAN.md).

Standalone run37675513854, checked source
`c9c59a85807da0135a8192b1912b15d510c68028`: one generic unsafe forget adapter,
whole unit without focus/macros/select/guard. All seven predeclared bodies execute,
return and leak-check; full VF exits1 with sole
`verified/lib.rs(3,1-16,2): dead code`. NORMAL/readonly export/decode and refinement
exit0; source integrity PASS. Body prefix is not a successful theorem.
Existing ManuallyDrop identity/destructor/no-unwind correspondence remains TRUSTED.

Separate replay37676357686/processor
`dd4b0493b8411d92f61f525a3c7ef6ec0429d021` PASS: immutable old run37669436220
logs, all nine original classifications preserved byte-for-byte. New separate map:
two positives INCONCLUSIVE (dead-code exit1), seven intended proof negatives.
Seven classifier controls PASS. This is no new proof or full S7 admission.

Budget **4601/5400 summed hosted job seconds used; 799 remain**, same budget/no reset:
entry4411 + standalone178 + replay12. All executable checks hosted-only, one active
relevant run at a time. Next diagnostic cap360s includes120s cleanup reserve;
existing console -dump_ast_with_locs only, same exact source/contracts/profile.
No syntax variation or translator/kernel/prelude/exporter/refiner/dead-code change.
If dead-code persists, document AST/trace cause and STOP without actual redirect.

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
