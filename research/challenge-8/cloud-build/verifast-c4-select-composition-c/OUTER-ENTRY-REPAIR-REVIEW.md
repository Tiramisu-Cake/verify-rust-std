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
