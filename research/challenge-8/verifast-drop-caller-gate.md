# Experimental local `Drop` caller gate

The manual `verifast_local_drop_caller_gate` selection uses the pinned
26.09 VeriFast build, paired Z3, nightly-2026-02-05 Rust exporter, and exact
SmallSort source `32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`.
Its source-build profile inherits the tuple, HRTB, lifetime-cut,
address-taken, and tracked `ManuallyDrop` patches, then applies
`verifast-local-drop-call.patch` to the translator only. The final translator
patch input is `f8751fab591ed98daebf446eb34800e892e72a838c7c083f643bd4efabbb0432`,
the patch SHA-256 is `6f5c2089b16364bc3d33eb98724fef60b5da4022bc70e77eb778b563eadb26ed`,
and the expected result is
`53fdb2ae74f66fd40efc9c60f633cfc159a2b84c2201979000572821d253da37`.
The build still requires the exact four modified VeriFast files.

The gate runs all 8 HRTB, 12 lifetime-scope, and 5 tracked-reference
regressions first. It then reruns the existing exact-source 364-byte
`CopyOnDrop<T>::drop` method proof before assembling any callers. The caller
extractor imports the direct destructor extractor, so it cannot silently
copy a stale Drop contract. Every original/verified pair is audited by
removing ghost comments and checking exact byte equality; the Rust standard
library source and direct contract hashes are recorded.

`cleanup_one<T>` owns only a fraction of the initialized source, the complete
initialized destination, the thread/type tokens, and one `foreach(T.own)`
sequence. Normal local cleanup must establish the exact copied destination
and return the same source fraction and single ownership sequence.
`cleanup_callback<T, F: FnMut()>` creates the real local guard, calls the
mutable callback, and carries the updated callback ownership through both
normal and unwind postconditions. The runner checks the callback call record
and the compiler MIR for the callback function, the normal and cleanup
`drop = (` terminators, a cleanup block, and the `unwindResume = void` edge.
It also requires at least two verifier call records at the scope close. Those
source-span records can include freeze/unfreeze helpers; independently inspect
the actual MIR edges and whole-unit caller postconditions before attributing
them to normal and callback-unwind destructor execution. No callback
purity or panic-free premise is added.

Negative fixtures separately omit source permission, destination permission,
or the element ownership sequence. An unannotated actual Drop retains the
generic `drop_in_place` path and must fail. A deliberately false exact-value
postcondition must fail while verifying the named actual Drop body after its
copy statement. Two annotated custom Drop fixtures (an extra physical field
and a `T: Copy` bound on both struct and impl) must pass Rust export/decode and
then fail at the local-Drop frontend guard. Every negative classification is
fail-closed; frontend/export failures cannot count as proof or intended
rejection.

The gate checks this narrow same-unit local cleanup translation and its
resource transfer. Run37431775757 reached the first caller, as detailed below.
It does not release the insertion held reference, prove
the insertion loop, recover full destination ownership for general insertion,
or claim support for projected-place Drop or nontrivial field glue. Build,
export, refinement, and proof execution occur only on GitHub-hosted Actions;
the editing server is limited to static checks.

First hosted run37423344712 at3a020357cfe5cb6e01eaaf1ef3575dd0abeea00b
passes source/tool/prelude/patch/four-file/dependency setup but stops at OCaml
translator7740: unbound record field item.def_id. Build2/12.73s,
RSS426,848KiB; runner1:07.68,RSS646,360KiB,allsetup. No body/caller/negative
proof, compiler MIR, regression or refinement was executed. The current patch
adds only an explicit D.trait_impl_item annotation to that lookup; the new
input/output pins above describe that record-type correction, tested in the
subsequent run below.

Corrected run37423762729 atb3da9a5ef53b8001e63ce511ba27ae8efce67343
builds0/19.14s,RSS426,676KiB and passes pairedZ3/source/tool/four-file audits.
Binary b603f7f3ac0963892f88dad3bdafe446707ce04e845b3054c7b087a1480a184e.
HRTB suite visits3 cases with compiler/decode0; first2 have intended finite
rejections, third hrtb_no_output crashes with Pattern matching failed in
local_drop_call. The intended outer non-ADT fallback is parsed as a redundant
branch of nested match substs (confirmed Warning11), so generic F Drop crashes.
Suite1/.69s; overall1,runner1:15.12,RSS646,784KiB. Remaining regressions and
actual body/caller/refinement gates were not reached. This failure motivated
the delimiter-only fix exercised in run37431775757. No cleanup proof was
claimed from that earlier run.

Run37431775757 at197d5a1 passes all 25 regressions, exact-source actual Drop
body/copy proof and source/refinement audits. `cleanup_one` exports/decodes its
MIR, invokes the annotated actual method through local cleanup, consumes the
normal postcondition and passes the leak check. VF exits 1 solely because the
unexecuted `UnwindResume` block is reported as dead code at the whole-function
source span. Its MIR has normal `Drop -> return` and a cleanup-only unwind
successor; the checked method has literal `on_unwind_ens false`. Later caller
and negative fixtures have not run. The current patch keeps the original AST
unwind branch but removes that impossible successor from the block-reconstruction
graph only for this selected same-unit method. `cleanup_callback` has a real
may-unwind callback predecessor to its cleanup block and remains the positive
control for retaining that path. A new hosted run must check both callers and
all intended negatives before the gate can be called successful.
