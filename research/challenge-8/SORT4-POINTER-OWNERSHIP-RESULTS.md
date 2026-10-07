# Pointer MaybeUninit ownership phase — closeout

2026-10-07. **CLOSED at the dependent callee's storage/borrow boundary.**
Entry `e0920ecb07cd05ef08acd6fb5a2fb228af9a1f98`; accepted proof source
`182ddf29dc73961723bf32be6b65643c524ca927` on `challenge-8/research`.
**Model and SAFE constructor ACCEPTED as an experimental component.**
Actual `select_unpredictable` RUN / INCONCLUSIVE: both constructor calls execute;
first remaining error is `MaybeUninit::as_mut_ptr`, `verified/lib.rs(38,20-41)`.
Full select and full sort4 are NOT PROVEN. RAPx CLOSED / NO-GO; B/C NOT RUN.

Final evidence: [O4 run](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37601511894), [artifact11473086721](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37601511894/artifacts/11473086721)
`smallsort-research-37601511894-1`, under `maybeuninit-new-pointer/`.
All claims below concern this source/profile/run/artifact unless explicitly
identified as historical. Artifact `matrix/summary.json` reports
`constructor_acceptance: true`, zero omitted source/proof/MIR cases, and
`actual_callee_status: CALLEE_INCONCLUSIVE`. This report follows full text-log,
source, MIR, mutation and profile evidence inspection; the workflow badge alone
is not acceptance. Final documentation changes are not a new proof run.

## Definition, domain and trust

[The pre-implementation decision](SORT4-POINTER-OWNERSHIP-PHASE.md) was committed
at `761cecf` before ownership changes. For the certified unit's exact
`MaybeUninit<*const Element>` specialization (thin pointer, generic Sized Element,
no Copy/Freeze/pointee premise), the DEFINED predicate is:

```
MaybeUninit_pointer_own<Element>()(t,v) =
    match MaybeUninit::inner(v) {
        none => true,
        some(p) => raw_ptr_own<Element>()(t,p)
    }
```

The existing raw pointer value ownership is defined `true`; empty resources
therefore follow from the frozen interpretation, not an assumed ownership
bridge. `inner(v)` remains an option: no equality between initialized and
uninitialized values, and no axiom for opaque `uninit()` is added. Construction
preserves `some(input)` with the complete modeled pointer value/provenance,
without address-only conversion or pointee read/write/nonnull/alignment rights.
Thread token is separate. Nonpointer specializations retain opaque ownership;
legacy generic explicit type predicates remain conservative/opaque.

SAFE ownership dispatch is type-wide inside the certified unit, not removed
for one function. The explicit normal contract carries the defined own chunk;
its introduction lemma has an ordinary checked body with exhaustive option
split. Translation emits its checked call after the certified aggregate. Kernel
verifies lemma and imported runtime body; there is no assumed opaque summary.
The pinned ManuallyDrop identity rule is an existing declared trust dependency,
not a newly proved ManuallyDrop/MaybeDangling implementation or memory bridge.

Profile `experimental-source-linked-maybeuninit-pointer-own-v2`:

| Identity | SHA256 / pin |
|---|---|
| Separate patch | `325af428910cff44fb51e8c11ef0e4c9c3ba928c015f1fdf657580745857ca8d` |
| VeriFast base | `809de4596839b739dd999f9e462242c835e3af46` /26.09 |
| Compiler / target | nightly-2026-02-05, `db3e99bbab28c6ca778b13222becdea54533d908`, x86_64-unknown-linux-gnu |
| Patched console | `cb453bea8ae97acca3ea57090cf1a0cbb6c9fa6b325922ce15f56578cbaa2e4c` |
| Stock console | `dc672335da76fe1bb06cf7ebca916185c34edb65466df0a937645a437c7f0ecc` |
| MIR exporter, identical profiles | `2b8ebb5373d0bdd82cc163f5a298a4291b89dcdb8630a01bf74149987f2d5e0c` |
| Refinement checker, identical profiles | `9f38829f30cb3295653ca111b53592946a97807eee54cba438fffed14c8c1ffe` |
| MIR schema | `7f3ebce320a33bcb956d51b8387754729e6516f4d15ba8dfdc61e6e36f90dfd9` |
| Patched std specification | `5698310f98ae97908f24a6a58b7fd774ebbbc96ac3210b43dd16c45c364970fc` |
| Patched translator | `eae7793266f995ed24c74cbc7b8d45dda8a08525f18ca7d5f14fddb42b112d03` |

`environment.txt`, `patch-source-identities.json`, `specification-audit.json`,
`applied.patch` retain the complete identity comparison. Only translator and
`bin/rust/std/lib.rsspec` changed; other specs, parser/kernel, prelude,
memory/alias model, exporter/schema/refiner frozen. No layout/old patch chain.
This is experimental acceptance under those trusted assumptions, not organizer
admission, complete-model soundness or verification of unmodeled provenance.

## Complete source/MIR applicability

`matrix/summary.json:source_certificate` pins MaybeUninit source
`7d588bf99e1bd7293b4b9c40fd71a6d5ed71ec6945920b166fc0c90547785702`,
constructor runtime body
`26a6c87090e954dea0b4a43f081516f00d2e4ba5103ac6ea1b846c4fe3f2e261`,
and exact two fields. ManuallyDrop/MaybeDangling hashes are retained there too.
Original/verified source remains unchanged across exporter, decode, refinement
and verifier stages; ghost stripping, source endpoints and SAFE annotations
bind the local copy to the pinned source.

Before enabling representation/redirect, the gate matches item path/kind,
public visibility, generics/HIR/drop flags/Sized predicates, union variant/
variance/field identities/types/spans/repr, argument binding and exact exported
contract text/location. Exactly four typed locals and two non-cleanup blocks:
`_3=Copy(_1)`; exact zero-sized FnDef ManuallyDrop::new<*const Element>, argument
Move(_3), destination _2, normal edge BB1/unwind Continue; `_0` aggregate with
active field value(index1), Move(_2); Return. Storage operations and mutability,
projections, types, block identities, all calls and no extra ghost/operations
are checked. Unknown/changed graph forms reject, not merely count names/calls.
SAFE no-unwind follows the proof, not the MIR Continue edge.

The exporter supplies path strings rather than opaque crate-hash DefId identity.
The explicit pinned-source/local-copy/typed-MIR equivalence certificate is the
trust link; this limitation is recorded, not claimed away. The corrected
false-post probe is allowlisted by exact function/expected redirect count, while
constructor body/graph certification stays identical.

## Acceptance matrix

Positive `matrix/constructor_positive/verifast.log`: SAFE prototype at10,
checked ownership lemma at std/lib.rsspec447 (both option branches, leak checks),
imported constructor at10, return/leak at22; frame caller25, return/leak48;
**0 errors,54 statements**. Caller requires no pointee resources for val, retains
fractional frame cell and independent mutable i32 cell, proves exact inner,
opens returned own and separately exercises none. Normal token/resource posts
and `on_unwind_ens false` intact. Integer identity positive carries its original
opaque resource and passes; missing-own integer negative fails that same original
SAFE prototype obligation, demonstrating unrelated behavior was retained.

Each row below has `matrix/<case>/verifast.log`, `fixture.json`,
`source-integrity-refinement.json`, original/verified source, exported binary/
text MIR and separate exporter/decode/refinement exit records in the artifact.
Proof failures are exit1 after checked constructor body; applicability failures
are exact certificate Failure/exit2 before proof. All frontend/refinement stages
exit0. Cases are never interchanged as evidence.

| Case | Accepted target |
|---|---|
| `nonpointer_missing_own` | EXPECTED_OPAQUE_OWNERSHIP_REJECT: `verified/lib.rs(52,6-32): error: No matching heap chunks: std::mem::MaybeUninit_own(int32_t_typeid)(_t, result0)` |
| `wrong_inner_post` | EXPECTED_PROOF_FAILURE: `verified/lib.rs(42,54-56): error: Assertion might not hold. (Cannot prove std::mem::MaybeUninit::inner(pointer_typeid(Element_typeid), __result) = some(wrong).)` |
| `false_uninit` | EXPECTED_PROOF_FAILURE: `verified/lib.rs(41,54-56): error: Assertion might not hold. (Cannot prove std::mem::MaybeUninit::inner(pointer_typeid(Element_typeid), __result) = none.)` |
| `false_assert` | EXPECTED_PROOF_FAILURE: `verified/lib.rs(41,16-21): error: Assertion might not hold. (Cannot prove false.)` |
| `false_postcondition` | EXPECTED_PROOF_FAILURE: `verified/lib.rs(35,91-93): error: Cannot prove condition. (Cannot prove result0 = wrong.)` |
| `resource_duplication` | EXPECTED_PROOF_FAILURE: `verified/lib.rs(42,48-49): error: No matching heap chunks: [f]points_to<u8>(frame, frame_value)` |
| `wrong_active_field` | EXPECTED_APPLICABILITY_REJECT: `local constructor runtime body differs from repository / source_certificate` |
| `wrong_operand` | EXPECTED_APPLICABILITY_REJECT: `local constructor runtime body differs from repository / source_certificate` |
| `wrong_return` | EXPECTED_APPLICABILITY_REJECT: `local constructor runtime body differs from repository / source_certificate` |
| `extra_operation` | EXPECTED_APPLICABILITY_REJECT: `local constructor runtime body differs from repository / source_certificate` |
| `renamed_function` | EXPECTED_APPLICABILITY_REJECT: `expected exactly one checked constructor body / typed_certificate` |
| `wrong_binding` | EXPECTED_APPLICABILITY_REJECT: `checked body shape or external call count differs / redirect_count` |
| `nonpointer_input` | EXPECTED_APPLICABILITY_REJECT: `checked constructor input is not *const Element / typed_certificate` |
| `extra_union_field` | EXPECTED_APPLICABILITY_REJECT: `certified union fields or types differ / typed_certificate` |

MIR fault injection uses the same patched console/spec with per-case shadow
exporter: real pinned export -> decode -> exactly one mutation -> encode.
Canonical and mutated binaries/text, recomputed exact mutation, source integrity,
real exporter hashes and successful refinement are all retained. Invalid MIR is
rejected before semantic activation; proof controls use the active accepted rule.

| MIR case | Exact rejected condition |
|---|---|
| `mir_operand` | `constructor place: _1 / full_graph`; exit2 |
| `mir_return` | `constructor place: _0 / full_graph`; exit2 |
| `mir_active_field` | `constructor union identity/type/active field / full_graph`; exit2 |
| `mir_type` | `checked constructor input is not *const Element / typed_certificate`; exit2 |
| `mir_identity` | `expected exactly one checked constructor body / typed_certificate`; exit2 |
| `mir_extra_operation` | `constructor first block statements / full_graph`; exit2 |
| `mir_hir_parameter` | `HIR generic identity: Element / typed_metadata`; exit2 |
| `mir_contract` | `constructor exported contract annotation text/location / typed_metadata`; exit2 |
| `mir_binding_span` | `function signature MIR span does not identify source item / typed_metadata`; exit2 |

All9 intended MIR controls PASS; none omitted. Canonical MIR binary SHA256
`1a5666723d1520b4c80e0901827a0bd0d18f33449299a5710874da5747067669`;
each distinct mutated hash in its `mutation-record.json` / summary record. These controls
reach the new rule's admission checks, not an unrelated unsupported union.

`classifier-tests.log`:5 fail-closed test groups PASS, including stage/message/
location/resource/prototype/admission/mutation/profile integrity mutants.
14 separate baseline controls PASS: paired stock/experimental pointer frame and
intended false assertion; paired C nonempty, C++ empty, existing Rust generic
struct, C struct and C++ constructor. Baselines alone do not accept the extension.
No dependent SWO/layout experiment repeated. Full matrix mode removed the previous
feasibility restriction; optional diagnostic mode still cannot claim acceptance.

## Actual callee and stop

Same O4 accepted profile/source and artifact, `matrix/actual_select_after_constructor*`.
Actual body SHA256 remains
`0d4233fe67c243c9d46201603fb143182ba2f5caa35f5d63907a3d5c50ed9613`;
hint blob `fe59166363b9cc049c0d48f4349f4dc9c0e458b8`, source SHA256
`d94ef86fbdac952fe7c9a6028536e15539b33dc188966fa4e9340fa7d94c30f8`.
The unchanged N6 pointer adapter preserves all3intrinsics, DropOnPanic guards,
drop/forget/assume_init and full selected-pointer/frame/no-unwind target.
Before helper insertion original/annotated adapter hashes remain cd6feb7a/bd332fbb;
final full unit hashes4c3cd8e1/8cec14ed are recorded exactly in stage integrity.

Export/decode/refinement/source integrity PASS; complete constructor certificate
PASS; exactly two source-linked external calls redirect. Actual SAFE prototype
passes and named body enters; calls at22/23 are verified using the constructor
body proved earlier in this same source/profile run. The checked ownership lemma
is also verified in this unit; the error occurs before its local constructor
body is visited again. Same-version checked-body evidence is the positive unit. First error at38,20–41:
`No such function: std::mem::MaybeUninit::<T>::as_mut_ptr`.
No successful actual-callee return/leak or normal/unwind post proof follows.

Observed source: `library/core/src/mem/maybe_uninit.rs:648` takes `&mut self`
and casts its storage address to `*mut T`. Scope inference: the value-own
predicate carries no storage/borrow permission, so this next source-linked
operation requires a separate storage/borrow capability assessment. Existing
model support for that operation was not measured; a new alias model is not
claimed necessary merely from the resolution error. This is an unsupported
callee-resolution boundary, not a disproved pointer contract or an intended
negative. The exact adapter, full MIR and logs are retained for a new decision.
No new storage/alias/borrow model or opaque summary was added. Intrinsic/copy,
DropOnPanic/Drop body, forget/assume_init and final selected-value/frame/unwind
obligations remain NOT PROVEN / not reached as complete operation proofs.
Generic `[const] Destruct` API and constructors for other T specializations are NOT RUN.
General unions, aliasing/borrowing, copy, FnMut, Drop and unwind outside constructor
are NOT IMPLEMENTED; full sort4 NOT PROVEN. RAPx CLOSED/NO-GO; B/C NOT RUN.

## New-phase execution ledger

All compilation, verifier/classifier and executable checks on GitHub-hosted
Actions, workflow_dispatch only, one relevant run at a time; no local tests/builds.
Job duration includes preparation/build/cache/upload, including failed runs.
Previous phase budget did not transfer. <=1800s/job and300s/proof retained.

| Run / source / artifact | Job seconds | Outcome and next evidence-based correction |
|---|---:|---|
| [O1/37598560122](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37598560122), `798863a89d8d9420670dd8b3c56766a861a6db34`,11471388654, patch31d3ca50 |137| SAFE prototype requires defined own before body; add explicit own post and checked introduction. |
| [O2/37599522829](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37599522829), `0f5b790cc58b30ee3aee12e8989a169e19998fb5`,11472570359, patch023e12f0 |128| Body54/5proof negatives pass; integer own contract and exact applicability classifier need repair; complete metadata gate added. |
| [O3/37600901979](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37600901979), `a452018e98e8894c66f9da41becaa8cf7a4a83c5`,11473245626, patch325af428 |126| Integer annotation syntax and extra-field mutant's earlier repr rejection miss intended targets; harness-only correction. |
| [O4/37601511894](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37601511894), `182ddf29dc73961723bf32be6b65643c524ca927`,11473086721, patch325af428 |127| Full acceptance PASS; actual callee reaches as_mut_ptr boundary; STOP extension. |

**518/5400 summed job seconds (8m38s),4 NEW runs;4882s retired at phase boundary.**
No active/queued relevant run; no pending implementation draft. Final docs-only
commit/push records this closeout separately from proof SHA. Earlier failed raw
runs and artifacts remain evidence, not accepted controls. Historical patch pins:
O1 `31d3ca507cc7ec4a090ef45330b0f3758c1fbcdbbb4c68d66c256166801d6aea`;
O2 `023e12f00a132ca8fd2dd46e0515c296317eeca573bb5a6c413321b2fe9ba292`. O4 archive includes
large shadow tool profiles;770 evidence files (6,906,949 bytes) excluding their
binary copies were downloaded locally for evidence audit; full archive remains in Actions.
Operating runbook unchanged. Next permitted work without a new phase is read-only
review/documentation; as_mut_ptr storage/borrow capability requires a separate
owner decision, not the remaining budget of this closed phase.
