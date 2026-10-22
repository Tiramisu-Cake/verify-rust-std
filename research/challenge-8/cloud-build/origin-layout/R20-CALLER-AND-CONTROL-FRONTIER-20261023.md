# R20 static caller and control frontier

Static investigation of tool `39f6b0cacd00575c8ca2d39e9f15632723bf1227`.
No compiler, extractor or verifier was executed locally. These are source
observations and implementation directions, not proof results.

## F5: separate unwind-copy resource negative

The R19 marker admits an array assertion, owner-drop lemma and array conversion
(`vf_mir_translator.ml:6660–6673`). Its count expression is unrestricted, but
the same checked block is copied on normal and unwind paths. The published
callee supplies the same resource shapes on both outcomes. A bad count alone
therefore does not distinguish the unwind copy. Removing the owner-drop call
is the existing static shape refusal, not a resource negative.

Weakening only the callee unwind post to `array_` is insufficient: the changed
actual callee must itself prove that post before its caller can be assessed.
The R9 guard-return recovery is attached to the returning arm of the selected
Drop (`vf_mir_translator.ml:3575–3587`), not a generic hook for every callee
unwind exit. The late-callback internal outcome flag is scoped to its own
reference recovery. The R19 rule also excludes overlapping callback/R9 plans.
No source-only variant closing F5 has been established. Do not report F5 closed
or raw-caller acceptance solely from the five R19 controls.

## Original caller: existing checked borrow route

The exporter currently erases region variables and the pointer-coercion subtype
(`vf_mir_exporter/src/lib.rs:2458–2492,2718–2725`). Mutable reference creation
uses the ignored-reference path (`vf_mir_translator.ml:3929–3963`). The slice
pointer special case covers `as_ptr`, with no explicit `as_mut_ptr` arm
(`:2892–2897`). Array type interpretation still lacks generic ownership/full
borrow content (`:1807–1825`). These remain separate from RawPtr refinement.

Existing lifetime logic can encapsulate concrete resources without a new
ownership premise: `borrow(k,P)` consumes `P()` and returns a full borrow and
end token; `borrow_end` restores `P()` after the lifetime ends
(`bin/rust/rust_belt/lifetime_logic.rsspec:117–125`). The checked pattern in
`tests/rust/safe_abstraction/str_mut_ref.rs:62–70` constructs metadata, closes
borrow content and borrows it. Slice borrow content is an element array and
element ownership (`bin/rust/prelude_core.rsspec:467–469`).

A candidate original-path implementation must carry exact coercion kind,
source/target types and lifetime identity, derive length from the actual array,
use checked array conversions and element ownership, encapsulate those same
resources, resolve `as_mut_ptr` to the data component, and restore the same
resources on normal and unwind paths. Existing `Array_to_array`/`array_to_Array`
and lifetime lemmas are possible building blocks, not an implemented solution.
The slice reference helpers with TODO `req true` cannot establish this protocol.
A new trusted borrow/memory premise would require the owner; none is assumed.

## RawPtr state control candidate

Changing an initializer fails in aggregate comparison before address-taken
reconciliation (R18 P2). A better candidate keeps two differently initialized
locals identical in both programs and changes only which local is addressed.
The intended failure is the existing unequal-local-state check in the
`LocalAddressTaken` handler (`refinement_checker.ml:2959–2960`). Its actual
reachability and source/stage binding remain Cloud-UNVERIFIED. The indexed
projection control remains INCONCLUSIVE until it reaches its intended gate.

This next control is now prepared as `unequal_address_taken_state` in the
existing RawPtr control runner. Both sources initialize both arrays identically;
only the addressed local changes. Matching requires the exact `_1`/`_2` state
diagnostic, both RawPtr operand listings, function context and unchanged typed
source/stage receipts. Earlier aggregate refusal, wrong pair, timeout or setup
failure is INCONCLUSIVE. The five earlier cases remain present. Ten synthetic
service tests pass; the running first R20 Build uses the preceding control
version, so it cannot establish this new case.
