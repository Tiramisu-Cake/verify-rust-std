# Actual `MaybeUninit::new` linkage on 26.10 — review before implementation

O4 proof SHA `86e84ace` captured the unchanged pointer-specialized actual
`select_unpredictable` body from std `cd371e03`. NORMAL/readonly export/decode
and refinement passed. The capture-only fixture has no S6 activation variables
and no checked local constructor. Its full verifier entered the actual function
and stopped at verified line 25, `No such function:
std::mem::MaybeUninit::<T>::new`. Complete typed MIR contains two calls with
exact def path `std::mem::MaybeUninit::<T>::new`, one `*const Element` type
argument each, `Move` from `_5`/`_7`, destination `_4`/`_6`. Both normal and
reachable cleanup graph remain present; this first failure does not settle the
later ownership, guard, forget, intrinsic, or `assume_init` obligations.

The accepted S6 translator already has an actual-body branch that expects
exactly two constructor redirects. It activates only after certification of a
local `sort4_certified_maybeuninit::MaybeUninit` union and
`sort4_checked_maybeuninit_new` body within the same exported compilation, with
`SORT4_MAYBEUNINIT_REPO_ROOT` set to the pinned repository. The local union and
constructor are a source-equivalent copy of `MaybeUninit::new<*const Element>`;
the translator maps their certified type and aggregate to the std model. A
bare environment variable or name match is insufficient because the local
source, full typed MIR, contract, spans, and actual redirect count must pass.

Proposed minimal experiment: append exactly that O3-accepted local constructor
module to both original and verified actual fixtures. Preserve the actual
function signature and entire runtime body byte-for-byte, and keep the original
equal to verified after ghost stripping. Activate only the constructor S6 gate
for this one hosted case. Require source pins for hint/maybe_uninit/manually_drop,
the exact helper body and local module, a complete NORMAL/readonly typed MIR
record, successful exporter/decode/refinement, S6's local constructor source/MIR
certificate, local constructor proof with return/leak check, and exactly two
redirect markers. The expected first remaining error is the next unsupported
actual operation, likely `as_mut_ptr`, and is diagnostic only. No actual helper
postcondition is accepted from reaching a later error.

Negative controls should mutate the *auxiliary* constructor operand or union
field with the original/verified runtime pair still equal after ghost removal.
The existing S6 certificate must reject before local body proof. A separate
actual-call-count mutant may replace one of the two `new` calls only as a
negative fixture; it must fail either the exact actual-source certificate or
the two-redirect gate. The production actual body is never changed. Keep
full logs and original classification for all controls; setup/frontend errors
are inconclusive, not intended negatives.

Trust boundary: exact std source to local-copy constructor and exporter
`def_path_str` applicability remains an explicit source/MIR correspondence,
not DefId equality. `MaybeUninit_pointer_own` is defined in the accepted S6
spec and owns no `Element` cell (`raw_ptr_own<T> = true` in stock). The checked
local lemma/constructor do not provide actual storage ownership or a generic
helper proof. S6 accepted patch, target std runtime, exporter, decoder,
refinement, and verifier safety/leak/unwind switches remain unchanged.

The scope of this component is **constructor linkage only**. After its hosted
result, a distinct reviewed step can add the accepted `as_mut_ptr` adapter and
then typed intrinsic/pointer-drop linkage, with fresh exact actual MIR gates.

## Implemented diagnostic gate

`check-constructor-linkage.py` implements the one-component fixture and two
source mutants. The auxiliary module precedes the actual function so VeriFast
checks its return/leak behavior before the actual body reaches the next missing
operation. The script imports the exact O4 actual-source preparer and the O3
constructor source builder; it has no independent rewrite of their runtime
bodies. It records full NORMAL and readonly MIR, stage/source hashes, the
unpinned-next-error log, and separate classifications. The positive requires
the existing S6 certificate marker, both redirect markers, the exact `2/2`
counter, the checked local constructor body/return/leak, actual function entry,
and a single first unsupported `as_mut_ptr` error. The two negatives require
their exact S6 source-certificate reason before any function proof. These are
falsifiable expectations, not claims already observed. Any other error is
`INCONCLUSIVE` and must guide the next revision.

The script is hosted-only. Python AST parsing and `git diff --check` passed
locally; no exporter, verifier, refiner, Rust compiler or fixture preparer was
run on the server. Hosted invocation on the existing S6 console:

~~~bash
python3 research/challenge-8/overnight-linkage/check-constructor-linkage.py \
  --tool-home "$source_home" \
  --schema "$source_home/src/rust_frontend/vf_mir/vf_mir.capnp" \
  --compiler-sysroot "$compiler_sysroot" \
  --evidence "$ev/constructor-linkage" \
  --deadline-epoch "$((OVERNIGHT_JOB_STARTED_EPOCH+1020))"
~~~
