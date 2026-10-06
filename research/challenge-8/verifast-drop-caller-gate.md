# Experimental local `Drop` caller gate

The manual `verifast_local_drop_caller_gate` selection uses the pinned
26.09 VeriFast build, paired Z3, nightly-2026-02-05 Rust exporter, and exact
SmallSort source `32574fd06623190132f213cbfeaeca5bd466e3c802ca97a2174e24fd3c240959`.
Its source-build profile inherits the tuple, HRTB, lifetime-cut,
address-taken, and tracked `ManuallyDrop` patches, then applies
`verifast-local-drop-call.patch` to the translator only. The final translator
patch input is `f8751fab591ed98daebf446eb34800e892e72a838c7c083f643bd4efabbb0432`,
the patch SHA-256 is `bc13ff90cbdc4a937200fb6b20efa2dbb9ceaea0a92d0e428c1fd5b47cc3a65a`,
and the expected result is
`03bf4a5c460c1babbd79c80dff7d1c4fc02d21add286498df9bd81fe47796213`.
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
It also requires at least two verifier Drop-call records at the scope close,
covering normal cleanup and successful callback-unwind cleanup. No callback
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

The gate proves only this narrow same-unit local cleanup translation and its
resource transfer. It does not release the insertion held reference, prove
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
input/output pins above describe the corrected source awaiting a NEW run.

Corrected run37423762729 atb3da9a5ef53b8001e63ce511ba27ae8efce67343
builds0/19.14s,RSS426,676KiB and passes pairedZ3/source/tool/four-file audits.
Binary b603f7f3ac0963892f88dad3bdafe446707ce04e845b3054c7b087a1480a184e.
HRTB suite visits3 cases with compiler/decode0; first2 have intended finite
rejections, third hrtb_no_output crashes with Pattern matching failed in
local_drop_call. The intended outer non-ADT fallback is parsed as a redundant
branch of nested match substs (confirmed Warning11), so generic F Drop crashes.
Suite1/.69s; overall1,runner1:15.12,RSS646,784KiB. Remaining regressions and
actual body/caller/refinement gates were not reached. Next fix must delimit
the nested match without changing generic fallback or proof obligations.
No cleanup proof is claimed; work stopped at the owner's request with no active run.
