# Outer strict-entry inference review

**Recommendation: GO only for a narrowly admitted translator relocation
candidate; HOLD any weakening of strict inference checks or any negative-proof
classification.** Static review only; no implementation, compilation,
extraction, verifier run, or Cloud action was performed.

Build `200ed04f` exports the full outer AST successfully
(`final_flattened_ast_sha256=2644adc375134de00d620bd8406139b0fac65b7ccebc65a07b50836840349bef`), then fails at `verified/lib.rs(84,9-38)` on entry to the strict block, before the real callback call or `end_lft_binding`. This is setup/inference failure, not the intended outer-bound escape VC.

The exact source already has `type_interp::<F>()` in the function precondition
at line 59, alongside `type_interp::<T>()`. The exported target `Func` also
shows the generic callback bound and the exact call-site FnOnce tuple. The
flattened AST puts compiler-generated temporaries in function-scope
`DeclStmt`s before the strict block. In particular, `$_27` at exported AST
line 6205 has type `&mut F` with `InferredTypeExpr`; `$_28` at line 6207 is a
tuple of shared references with inferred regions; and `$_29`–`$_32` at lines
6209–6212 are call/reborrow references with inferred regions. Their runtime
uses are at the call on source line 103. The failing verifier path runs
`freeze_strict_type` over the entry `outer_tenv` before the block body and
correctly rejects an unresolved `InferredType` there.

The saved log does not print the name of the first failing `outer_tenv` entry,
so the specific first element should remain unclaimed without a trace. The AST
does, however, expose the concrete unresolved region-bearing locals that
explain this error shape. A missing `F` type-interpretation premise is not
supported by the artifact and would not resolve the compiler-generated
per-call reference lifetimes before entering the block.

The localized candidate is to move only the certified six generated
declarations (`$_27`–`$_32`) from the function-top list into the already
admitted strict block, after its marker and before the head label. Preserve
each declaration's exact identifier, AST type, initial flags, and one-copy
count. Keep the strict verifier's entry freeze, exit/live-heap/bounds checks,
kernel, function posts, callback call, and cleanup behavior unchanged. This
changes trusted source-to-AST scope correspondence and therefore requires a
new exact candidate profile and fresh Cloud proof; it is not a proof-neutral
runner change.

Before enabling relocation, require exact source and complete NORMAL plus
readonly MIR identity and local-role mapping. Confirm on every normal route
that the selected locals become live only inside the strict prefix, are all
dead before the cut, and have no later use, address escape, heap retention, or
Drop. Separately confirm the callback unwind is the certified direct
`Continue` path, bypasses the normal `StorageDead`s, has no cleanup/drop/use,
and that the strict block exit frees each relocated declaration exactly once
while the unchanged unwind post verifies. Add source/MIR mutants for missing
`StorageDead`, post-cut use, address-taking/escape, wrong local type, and a
changed unwind successor; each must fail its intended gate. Do not generalize
to other bodies or suppress unresolved inference.

Until that candidate passes those gates and the real callback call reaches
`end_lft_binding`, this run provides no outer-bound-negative evidence.

## Reuse of the existing six-local relocation

The reviewed translator already has a TEST-only relocation implementation at
`vf_mir_translator.ml:7644–7748` and the single insertion point at
`5777–5790`. It selects only `_27`–`_32`, requires one local declaration and
one recorded MIR type per ID, checks exact erased-reference/tuple type shapes,
checks address-taken is false, removes six declarations from the outer list,
and inserts the same translated declarations exactly once after the strict
scope marker and before the block head label. Its current admission is
deliberately limited to `callback_positive`, source line 52, source MD5
`7b206fedf030cc663d77378b75e0d141`, and cut line 106. Reusing this mechanism
avoids a new relocation framework.

For the negative target, the only admissible extension is a separate exact
branch for `negative_outer_bound_escape`: require strict lifetime and HRTB
output flags, the exact singleton target, absolute unused current-bound AST
export path, exact source SHA-256
`bca43d1a7b92cac4faf11362f55b35d115306e920fb0999139a57836dbd94cf5` and
MD5 `533c766ca85f97db615a700882dc0e89`, source file `verified/lib.rs`, function
line 52, and the unique `'cmp` cut at line 106. Retain the existing exact six
local type/id/count/address-taken checks and one-insertion assertion. Keep the
existing callback-positive branch byte-for-byte and preserve the normal
outer-fixture export and registration gates. Do not activate relocation by
name or environment flag alone.

This static review does **not** clear relocation: the Build200ed04f archive
contains the exported AST but no complete NORMAL/readonly MIR event capture.
Before any semantic edit, capture both modes for the exact target and
`recover_pair`. Require source/body hashes and actual Reader records mapping
the normal six roles and readonly six roles. Review all normal CFG routes:
each selected local becomes live only inside the strict prefix, has no alias
or address escape beyond its recognized reference/tuple uses, reaches
`StorageDead` before the cut, and has no later use or Drop. Separately review
the direct callback `Continue` unwind: no cleanup, later use, or Drop; block
exit frees each relocated AST declaration exactly once while original
unwind posts remain in force. Any missing event, new path, type/role mismatch,
or retained alias means HOLD and no relocation. Existing exact admission
mutants must continue to refuse before proof.

### Normal MIR capture review

Read-only review of
`/tmp/verifast-c-2a5e-extracted/allprooflogs/cases/integration/outer-discovery-normal-mir.txt`
confirms the six roles and one normal route. Normal MIR declares `_27`–`_32`
with the expected erased-region types. Each has one `StorageLive` in the
line-103 call block, uses only for the mutable callback receiver,
construction/reborrow of the two shared-reference arguments, and the one
`core::ops::FnMut::call_mut`, then one `StorageDead` in that call's normal
return block (source line 103). All six deaths precede the line-104 post-call
ghost close and line-106 lifetime cut. I found no later use, second
`StorageLive`, Drop, or cleanup use for these IDs in the target body. The
FnMut call has direct `unwindAction=Continue`, so its unwind edge exits without
a cleanup block or subsequent MIR use. The borrow chains are `&mut *is_less`
for `_27`, `&*left -> _30 -> _29`, and `&*right -> _32 -> _31`; `_29`/`_31`
are placed as values in tuple `_28`. No address is taken of a temporary's own
storage.

This supports the normal-path relocation rationale, but the readonly MIR
capture still needs independent review before GO: the compiler renumbers
locals, and its StorageLive/dead/call/unwind facts must be mapped by role, not
assumed from these normal IDs. No semantic edit is cleared yet.

### Fresh NORMAL and readonly capture review

The corrected capture-only Build `7c662097` supplies both full target-body
records and reports `proof_credit=false`. I independently hashed the text
files; their body hashes match the capture record:

- NORMAL body `967b297f9044c1c9ba81b6e5e469c5ef6d013e33b4f17cf8134138fd4fe065c5`;
  whole decoded MIR `5a2e53473c99720b20f5186469c91c49c562cd8b89c7f9d9160589979e66d220`.
- Readonly body `1fa420e27a2c8e7e9983a347b3958a6926ca52abc762ee3c8d3c9347fd90e49e`;
  whole decoded MIR `4d8512c3d899f543c4e4808215151708fe1aa417886a2ec04bd1fa531b460b57`.

Readonly uses renumbered locals with an exact role match to NORMAL:
`_7` receiver maps to NORMAL `_27`; `_8` argument tuple to `_28`; `_9` / `_10`
are left reborrow / backing reference and map to `_29` / `_30`; `_11` / `_12`
are right reborrow / backing reference and map to `_31` / `_32`. All six
readonly locals have one `StorageLive` in the source-103 call block, uses only
in those reference/tuple constructions and the one `FnMut::call_mut`, and one
`StorageDead` in the normal return block before source line 104 and the line
106 cut. The call's unwind action is direct `Continue`; it has no cleanup
successor. The complete six-ID occurrence scan shows no later use, extra live,
Drop, or cleanup use in either mode. The references are values borrowing the
formal callback and pointees; no MIR operation takes the address of one of
these temporaries' own storage.

**Conditional GO for the exact six-local relocation candidate**, reusing the
existing `SORT4_STRICT_LFT_RELOCATE` implementation with a separate
`negative_outer_bound_escape` source/flag/export admission branch as described
above. Both independently captured MIR modes now support moving these
declarations into the exact `'cmp` strict block: normal execution kills all
six before the cut; direct callback unwind exits with no cleanup/use/Drop and
the strict AST block can free the six local declarations once. This verdict
does not grant proof credit. Keep the verifier's fail-closed entry/exit logic,
original normal/unwind posts, identity/call/unwind gates, and all existing
admission mutants. The edited candidate still needs fresh Cloud build and
proof; its strict-negative row is creditable only if it passes the real call
and fails at the intended post-cut outer-bound VC. Capture hashes and this
review must be retained with that candidate.

### Implementation preflight review

Reviewed the current translator and runner diffs. The existing positive
`callback_positive` relocation source/MD5 path remains intact. The new
`negative_outer_bound_escape` branch requires strict cut and HRTB output,
the exact singleton target, absolute unused AST-export path, and the fixed
`sha256sum` row for the target file; the shared relocation gate additionally
requires `SORT4_STRICT_LFT_RELOCATE=1`. Its source MD5 selection is specific
to this target. The exact six-ID/type/address-taken/count checks and single
insertion assertion are reused. I found no kernel, postcondition, or existing
positive-branch weakening in the reviewed tool diff.

The runner creates the exact renamed source fixture, recaptures full NORMAL
and readonly target MIR and refinement, and compares the returned inventory
to `manifest["outer_scope_capture_pins"]` before invoking the target proof.
The capture values to pin are the two body hashes and two whole-decoded-MIR
hashes recorded above. This equality is a fail-closed replay check, not a
replacement for the separate source-hash/translator gates.

**Source review: GO, conditional on the final manifest containing the exact
four reviewed outer-scope capture pins and its new profile/runner identities
before Cloud submission.** At review time the checked manifest was still the
C3 discovery manifest (`profile_id=...-c3-discovery`) and had no
`outer_scope_capture_pins`; the new runner would fail closed at that lookup.
Do not submit until the final manifest replaces that discovery profile and
pins the reviewed capture. No compile or proof was run for this review.

### Final manifest check

The updated manifest now pins exactly the independently hashed capture:
NORMAL body `967b297f...fe065c5`, whole MIR `5a2e5347...e66d220`; readonly
body `1fa420e2...fd90e49e`, whole MIR `4d8512c3...b460b57`. It records capture
Build `7c662097-71a7-4c0a-8b80-ef1d15f8a622`, archive
`fd7deccc56b4c6adea1b40fa8e1e5b6c770b43bc023f53639617ed02be1c9719`, and
`proof_credit=false`. The translator effective-source hash also matches the
reviewed tool source. This resolves the MIR-manifest pin condition.

One runner identity condition remains before submit: the manifest still lists
`candidate_runner_commit=4c2e2447...`, while the checked proof checkout is at
`cc95e4f29b2869631d3665d37a830a10f3c9fb29` and has uncommitted driver and
regression changes. Commit the reviewed runner changes, then update the
manifest to the exact candidate runner commit and execution status. Until
those identities agree, hold Cloud submission; the source/tool portion of
this review is GO, but the submitted runner package is not yet identified by
the manifest.

The runner provenance was subsequently corrected: the manifest now pins
`candidate_runner_commit=fec0744073852fb4a2d1bc71ba90af6f77a1d312`, matching
the new capture/runner commit in the delivery chain; the profile remains
experimental and `C3_SEALED_FINAL_UNRUN`. With this provenance correction, the
final preflight review is **GO to submit** the exact candidate for fresh Cloud
verification. Proof credit remains entirely dependent on the new Cloud result.
