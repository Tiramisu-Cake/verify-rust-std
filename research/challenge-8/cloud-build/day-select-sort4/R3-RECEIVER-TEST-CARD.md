# R3 NORMAL as_mut_ptr receiver TEST — pre-implementation review

Observed blocker: Build9bdd5622-7000-483f-8e83-e9847412ddba clears R3 ghost-scope
inventory with scope translator ed8ee5ed8a7f8abb7d9c7cee3a978059b55c0a02e34f908170a80d6cc3ed4102,
then refuses `SORT4-AS-MUT-PTR: actual external receiver operand/binding` before
all proof headers. Actual source a95aff14592b167c62c53c7ed726128ee86c7c19768cfe613504cdec841f8463,
unit407acbaea262ba908ed88434231e9fce1128678840f5d929deaad71838290a92,
body7f8374652a11e36073ad6ed10ec39b0f8de62da53265dd80d2dc2c3565491cee1.
Source hint::select_unpredictable, pointer specialization T=*const Element only;
original466882d74de217766ed8d5c583596c173df47f0e6bd40da7cb1a4c931d7265a5.

Exact evidence: NORMAL two external as_mut_ptr calls at source173/174 consume
Move(_11)/Move(_13), each mutable unprojected Other place of erased mutable
MaybeUninit<*const Element> reference; destinations _10/_12. Receiver reference
assignment comes from runtime shadow wrappers true_val/false_val respectively.
READONLY removes leading ghost lets and retains Move(_9)/Move(_11). Frozen S6
translation arm expects _9/_11 in NORMAL too. R3 admission and full NORMAL/readonly
capture already pin all9bodies/10Marshal objects and 61locals/44blocks; the saved
let2 explains the exact +2 shift. Constructors redirect successfully. Adjacent
A1/drop/forget R3 overrides are already updated; no other observed failure is assumed.

Proposed rule: separate default-off translator TEST layered AFTER scope TEST,
not a baseprofile amendment. Require own exact-root pair, complete R3/R2/nine-body
admission, scope opt-in and existing exact source/unit/body correspondence. For
ONLY the two actual R3 NORMAL as_mut_ptr calls require first _11 then _13; preserve
existing exact callee/type/lifetime/arity, mutable/Other/no-projection/Move and
count2 checks. Source-linked typed MIR tuple corroborates the mapping. Old branch
and profiles retain _9/_11 when TEST absent. No readonly override or new receiver
shape, permissions, argument expression, result rewrite or callee contract.

Correctness self-review: receiver local numbers are compiler temporary identities,
not rights. The complete unit pin fixes their exact reference formation, type,
source spans and call order; checked actual as_mut_ptr callee/body and its normal/
unwind borrow contracts stay the same. Updating this one source-linked admission
mapping changes accepted translation and is explicitly semantic/experimental;
it proves neither genericT/ZST nor soundness. No address equality grants ownership.
Trusted premises stay existing compiler/exporter/refinement and source-linked
experimental profile; no kernel/spec/prelude/model/parser/exporter/refiner change.

Required fresh combined gate: full source/MIR/refinement/inventory/identity recheck;
scope off/partial/on retained; receiver off repeats observed receiver Fatal before
headers, partial rejects exact opt-in, on emits two receiver markers and records
full unfocused proof's first error or full exit with all posts/checks. Isolated
wrong first/second receiver identity controls must fail at this receiver predicate
after same exact R3 admission, not at source/unit/setup. Keep negative copies separate
and parent production/scope source/binary unchanged; hash exact positive/negative
patches/consoles. Broader malformed-place controls remain explicitly unperformed
unless the implementation changes those checks. Original source/unit gate controls
remain compatible historical evidence only, not fresh acceptance of this TEST.

Full target normal pointer selected-input equality+raw_ptr_own/thread and pointer
unwindfalse remain unchanged; generic selectedcurrentT.own/unwindcleanup target is
still open. Any later binding/type failure can justify shadow capture, any genuine
payload/current-wrapper failure needs its own pure/resource diagnosis. A frontend
or unrelated failure is diagnostic/setup, never intended proof negative. Nested
Drop not credited before its same-version body. Collector/TEST pass is not theorem.

Infrastructure uses existing scope lane runner plus opt-in receiver diagnostic
extension in a separate copied tool; same current source/proof closure, added
committed TEST inputs only, <=191parts. One shared Build, timeout1200+60queue reserve
within new3172remaining and deadline/evidence reserve. No old budget is spent.
