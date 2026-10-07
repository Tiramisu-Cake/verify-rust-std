# Challenge 8: current checkpoint

Updated2026-10-07. **S6 narrow drop COMPONENT_ACCEPTED (v3); v4 READY for fresh hosted gates.**
Owner resumed only payload `*const Element` / receiver `*mut *const Element`
from bea6248. Broader04d67f4b draft/Drop/guard/forget/assume_init/union/refiner/
kernel/memory/alias/provenance remain frozen. Wholehelper/sort4 NOT PROVEN.
[Phase](SORT4-SELECT-POINTER-PHASE.md), [design/trust/gates](SORT4-SELECT-POINTER-DESIGN.md),
[results](SORT4-SELECT-POINTER-RESULTS.md), [actual](SORT4-SELECT-CALLEE.md).

Budget **3752/5400 summed hosted job seconds used;1648remain**, no reset/noactive.
Last completion37654585346/sourcef1774d5:184s16:45:53–16:48:57UTC.
Previous fresh37651717720/dfc1f1d:266s; diagnostic37648838042:65s and
37649244205:69s are included, not proofs. Full budget ledger in results/log.

V3 full fresh drop2positive+11proofnegative+22admissions, ctor/asptr/intrinsic
matrices and14baselines PASS. Same-profile completion authenticated all tool/
compiler/spec/std identities, retained original classifications/rawlogs and combined
2 unchanged coordinate replays with16 NEW intended rejects:18/18 NORMAL controls PASS.
Baseline full admission/redirect passes; drop call57 fails pre110 initialized
`points_to<*Element>(__result2, _)`; thread/currentThread checks pass.
Projected source/export/decode/refinement/full36/19 and method cert PASS, but final
redirect hardcodes baseline `_23` while exact projected receiver is `_26`.
This admission failure precedes proof and is not a resource result.

V4 preimplementation design card committed a649f96 before code: ONLY final receiver
checkpoint chooses `_26` for fully certified projection and `_23` for baseline.
Patch c7cc08a995bac5879901f4fe08030f09d23bdfefb1a3ab5893be12a8dd1f8fc1,
profile experimental-source-linked-select-pointer-drop-v4. Static review PASS.
No OR/count relaxation, AST/MIR rewrite, source/runtime/CFG/spec/glue change.
Full NORMAL/readonly map and all five annotation coordinates documented before
admission change. Fresh full component/regression gates and19 independent NORMAL
controls (including oldreceiver26→23) precede actual baseline and stock projection.
Next permitted action: publish exactSHA, one hosted dispatch, cap25min1500s with
120s reserve/proof<=300, then STOP at projected/drop resource pre or next blocker.
No new budget or broad semantic phase. Push HTTP500 temporarily prevented publish;
no force/reset/local verification fallback.

Checked method/ghost resource identity lemma are separate from TRUSTED compiler
raw-pointer drop glue correspondence; recursive free stub NOT runtime-body proof.
Existing initializedcell/fullpointervalue/thread/frames required, no Element rights.
Frozen frontend ghost substitution/synthetic unwind correspondence trusted separately.
Stock open/close_MaybeUninit derivation is a hypothesis until actual proof reaches it.

S5j correction: readonlyexport/decode0, refinement FAIL RawPtr bb1command4;
normal preprocessing separately after-tailghostclosefailure. No readresource proof.
RAPx CLOSED/NO-GO,B/C NOTRUN,no upstream PR/messages/submission.
