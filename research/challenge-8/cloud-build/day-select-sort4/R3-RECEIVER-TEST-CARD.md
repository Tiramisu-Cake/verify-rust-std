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
committed TEST inputs only, <=191parts. One shared Build, timeout900+60queue reserve
within new3172remaining and deadline/evidence reserve. No old budget is spent.

## Implementation pins and controls

Implemented as a separate optional nested diagnostic in the existing
`o26-r3-ghost-scope-test` lane. `O26_WITH_R3_RECEIVER_TEST=1` requests it;
absence defaults to `0`. The exact receiver opt-in pair is
`SORT4_R3_RECEIVER_TEST_REPO_ROOT` and `SORT4_R3_RECEIVER_TEST=1`; its root
must equal the exact scope and R2 roots and both R3 owner/nine plus R2
input-relation admissions must be active. The changed mapping is in translator
hash `7451dee6edcd63a4151eb45816a882f51107c7f096b047762cc482b154f61fd6`,
from exact scope parent `ed8ee5ed8a7f8abb7d9c7cee3a978059b55c0a02e34f908170a80d6cc3ed4102`.
Patch SHA-256 is `284a135f0c43c0ef50a7d48cd5bc6e294415e0168fa9e11a9238c0ab9c0c6c09`.
The parent reconstruction follows frozen20, refresh22, R2 component24 and the
scope TEST patch from source object
`f76012fb518703b1d98e243ac4f487f16877cfcb`.

The Cloud helper retains full receiver-off, partial-pair, receiver-on, wrong-first
and wrong-second logs, stage summaries, tool snapshots, and patch/console hashes.
A receiver control is valid only after the ghost-scope marker and exact source
admission. The two wrong-identity runs are translator fault-injection diagnostics
for the intended receiver predicate; they do not test malformed-place
admissibility. An incomplete requested nested gate fails the outer scope audit.
All acceptance, target-contract, malformed-place admissibility and theorem-credit
fields remain false. The full target NORMAL and unwind posts, source, unit, body,
specification, kernel, exporter and refiner are unchanged. Builds and proof runs
remain Cloud-only; this implementation has only received static checks so far.

The current candidate recipe uses an explicit receiver entrypoint under the same
scope lane identity; it sets receiver flag1 and delegates to the unchanged-default0
scope launcher. No lane alias or new scheduler registration. Main review corrected
OCaml let scope, nested scope/R3 env propagation, exact snapshot key sets, timeout
refusal, marker order and separate log/binary hashes. Architectural review confirms
this diagnostic mapping only; fresh malformed place/Move/mutability/type and
source/unit/body controls and actual callee obligations remain acceptance blockers.
