# FRAME late-shadow ghost representation — proposal before implementation

Observed blocker: Build6ad52849-ff34-43f4-bd4a-49b810d52d45 FRAME-on executes
current-wrapper assertions229–230 after actual drop/forget, then231:49–57 reports
inner(true_val) type mismatch: actual *Element, expected MaybeUninit. Old240 is
passed on reached conditiontrue path; false branch/finalresult/unwind/leak not yet.
Old240 was loss of witness through ownerfold, not shadow; this is new late evidence.

Rule: leave exact FRAME runtime, helper contract, fulltargetposts/resources and all
checks unchanged. Substitute only three late ghost references: true_val→true_val_1,
false_val→false_val_1 (including conditional-wrapper assertion). Must first verify
NORMAL and readonly debug-name order/local/type mapping plus frozen translator
make_var_id_name_maps: first surface name binds parameter, second internal suffix_1
binds real MaybeUninit runtime local. Actual wrapper is reached by real call/move/
resource, not replaced with savedinput snapshot. Savedinputs stay logicalstandards.
No source runtime/local binding alpha rewrite, no std/generic signature changes.

Domain: same pointer-specialized actualselect<Element> and generic helper/nested
prerequisites as FRAME; conditional experimental profile, unrestricted select<T>/ZST
separate. Source-only9body full NORMAL/readonly/MIR/refinement/10Marshal capture
required; oldFRAMEexact certificate must refuse fresh ghostsource. New narrow
source/hash/span/ghost/CFG certificate/profile is separate default-off TEST.
No decoder/parser/exporter/kernel/model/spec change or generic shadow resolver.

Self-review: suffixes are implementation-specific, so exact order/type/span/source/
unit pins mandatory; guessed '_1' is not sound binding evidence. Need both actual
wrapper assertions and fullreturnpost; ghost equality on surrogate wrapper alone
would not establish returnidentity. Runtime selects/moves actual wrappers and
assume_init output must connect to savedinput via checked callee contract. No
assertion deletion, assume/addressownershipbridge or weakened targetposts.

Affected controls: oldFRAME source/default-off retained at231; changedsourceoff
exact source refusal; partialpair/mismatchedroot preheaders; exactnewon reaches
same checkedhelper/nested andouter. Wrongname/binding/span/source/Move/edge, wrong
branch/frame/falsepost remain open until individuallytested. Positive progress
requires execution past231–233; completeouter additionallybothnormal/unwind/
return/leak/deadcode andsource/refinement. Setup/typefail not theoremnegative.

Completion preflight: initial full pair d2e0a2fa was192parts and NOT_SUBMITTED. The old FRAME lane transport recipe and FRAME design card are not read by the new adapter/shared helper/collector; remove these two documentation/selection inputs only from infra transport. Preserve shared actual runner, all tool patches/manifests, guards, profiles and source/capture dependencies. Parent card remains published in Git. Capture60bf reached complete source/MIR/refinement/10snapshots; its final collector NameError NAMES is audit-only, fixed to the explicit same nine defpaths. Raw archive4c67905d complete/verified; no repeat capture proof/tool build for that classifier correction.

## New authorized TEST — NEXT phase2026-10-09

Actual obligation: exact selected **original pointer value**, thread token, raw_ptr_own, falseunwind and fullreturn/leak/resource/refinement checks for pointer-specialized actualselect. No pointee access/ownership claim. Caller is actualsort4's raw-pointer selects; pointer arguments arise from v_base offsets/previous checked selections, while pointee permissions come separately from current sourcearray ownership recovered after callbacks.

Hypothesis: corrected artifact path allows old231baseline and freshsourceoff/partial/on to execute; exactlate3suffixrefs select realMaybeUninit wrappers, preserving payload identity through actual moves and checked assume_init. Positive: bothconditionpaths/fulltargetposts+callee bodies, then one actualcaller obligation if beforemain deadline. Contentful failure: inspect firstcurrentvalue/resource/source obligation and repair narrowly undercard; refusal at231 means latebinding notresolved. Setup/frontend/audit failure does not refute target. Negative off/partial refuse exactpreheaders; oldbaseline preserves exact231. Nested must execute atsame finalsource/tool before outer summary use. Wrongsource/span/binding/Move/edge/branch/falsepost admissions remain open unless specificallyexecuted. New phase window60+30 and new3600account override previousclosed phase; coordinatorunchanged.
