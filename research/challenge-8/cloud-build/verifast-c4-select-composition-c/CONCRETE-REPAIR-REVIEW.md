# Independent review of concrete B2 repair card

**Verdict: GO for the narrowly scoped repair, subject to the constraints below.**
The archived failures identify concrete, localized issues. This review grants
no proof credit and authorizes no kernel, postcondition, or profile acceptance.

## A. Typed numeric comparison

The Build `6e001459` composition log confirms the failure is at
`compare_transport_expr` line 17637 with
`Invalid_argument("compare: abstract value")`. Replacing only the `BigInt`
and `Num` polymorphic equality guards with `Big_int.eq_big_int` and
`Num.eq_num` is the right repair. The frontend lexer already uses the same
numeric equality APIs (`eq_big_int` and `Num.eq_num`). Keep the existing
fallback rejection for unequal values and all other structural, location,
unsupported-node, sharing, count, and reverse-hash checks unchanged.

A small Cloud-only OCaml check after dependency extraction is useful and
proportionate: independently construct large equal and unequal BigInts and
rational `Num`s, then require the two numeric equality functions to return
true/false as expected. Use the already provisioned OCaml/Num toolchain, save
the source and output with the exact build evidence, and do not install another
toolchain or run this check locally. The actual composition must still exercise
the full typed comparator and produce the fresh certificate and imported-body
proof sequence.

## B. Exact outer-bound callback fixture admission

The archived outer-fixture log confirms refusal occurs before any function
header because the early source marker gate allows markers only in
`callback_positive` and `callback_false_post`. The requested extension is
appropriately narrow if it admits a marker only for the exact
`negative_outer_bound_escape` body under all of these conditions together:

- `SORT4_STRICT_LFT_CUT=1`, `SORT4_HRTB_OUTPUT=1`, and the exact single target
  `SORT4_HRTB_OUTPUT_TARGETS=negative_outer_bound_escape`;
- `SORT4_CURRENT_BOUND_AST_EXPORT` is present, absolute, and unused;
- `verified/lib.rs` hashes to
  `bca43d1a7b92cac4faf11362f55b35d115306e920fb0999139a57836dbd94cf5`;
- exactly one marker parses, with all existing source adjacency, exact
  `FnMut::call_mut` type/argument, direct `Continue` unwind, normal successor,
  and recovery-count checks retained.

The current downstream AST-export gate already checks exact target identity,
strict/HRTB flags, absolute unused output path, and the same fixture hash. The
early marker admission must enforce its own matching conditions before it
allows the special marker; it must not accept by body name alone or by a
broadened target list. At this early translation point,
`sort4_actual_owner_sha256` is lexically out of scope: it is declared later in
the file. Reuse the existing C4 source-gate pattern at lines 6835–6840:
`Unix.open_process_in "/usr/bin/sha256sum -- verified/lib.rs"`, close and
require exit 0, and compare the entire output row to the fixed digest and path.
This preserves the exact-source boundary without moving or generalizing the
owner hash helper.

The source fixture is the agreed `positive_f_bound` callback case with only
the function name changed, and retains its original comparison-debt,
normal/unwind posts, and `F`/`T` owner resources. Keep the downstream target
registration AST, actual call execution, and expected end-of-lifetime escape
VC gates mandatory. A marker refusal or setup failure remains non-semantic
evidence.

## C. Reachable-unwind log identity correction

The saved mutant log records unit hash
`203989644124ecd20473efc286cb43a148de4f196c10b4a037f4bdb04cd2d098`; the
fresh decoded-MIR capture records whole-MIR hash
`bb50b114bcda7905c84f890500f4a8991009c4a554ddcbe8d5eb5f6a87229e83`. They
identify different representations, so the current classifier comparison to
`whole_decoded_mir_sha256` rejects valid archived evidence. Compare the
mutant’s logged `unit_sha256` to the pinned source unit digest (already
preflighted against the exact source/unit fingerprint), and retain the
independent whole-decoded-MIR check against the saved capture. This is a
saved-evidence classifier correction only. Preserve the original archive,
classify under its exact proof/tool identities, and do not transfer proof or
negative credit from the earlier run.

No source or semantics work was performed for this review. No compiler,
verifier, or Cloud command was run.

## Post-implementation review — tool commit 09389e2

Reviewed the exact tool diff from B2 commit
`e2e674f8727259ef08c68e58bb5dae1bd723cf76` to repair commit
`09389e2c0a4d6d2ed4e1146df0ad6321832c12cb`. It changes only the two typed
numeric equality guards and the early callback-marker admission gate. The
guards use `Big_int.eq_big_int` and `Num.eq_num`; the unequal-value case still
falls through to the existing structural mismatch refusal.

The added outer-fixture gate requires the exact body name, strict lifetime
flag, HRTB flag and singleton target, plus an absolute unused AST-export path.
It uses the fixed `verified/lib.rs` sha256sum row and checks the process exit
status. That source gate is placed before `sort4_actual_owner_sha256` is in
scope, as required. The existing marker count and downstream checks remain;
the final AST-export hook independently repeats target, flags, output path,
body count, and source-hash admission. I found no broadened target or
body-name-only opt-in in this diff.

The new Cloud numeric check constructs large equal and unequal BigInts and
equal and unequal rational values, and is compiled/run after the pinned
dependencies are extracted using `ocamlfind ocamlc -package num -linkpkg`.
The runner places the dependency bin directory on `PATH` first. The test is
small and directly covers the concrete equality semantics without replacing
the required end-to-end typed composition check. The recipe includes the new
source file. The profile pins the resulting translator hash as
`f250c2d137fd0998438afee375b7eddd88bd3a916b12dcf7ffb62953d1a4b7d2` and a new
composition patch SHA, under the distinct experimental profile
`verifast-c4-select-composition-20261011-c1`.

The reachable-unwind driver correction now compares the logged unit hash to
the pinned `source_pins["unit_sha256"]` and records the whole-decoded-MIR hash
separately. The earlier full-MIR/source fingerprint gate remains independent.
This is a classifier repair and does not revise the archived proof result.

**Post-implementation verdict: GO for the second Cloud run under the new C1
experimental profile.** The numeric check is supplementary; the Cloud run must
still demonstrate fresh B2-derived compilation, the exact fixed producer AST,
typed transport certificate, imported-body order, composition proof and
negative controls. Prior B2 crash/refusal results remain setup failures and
receive no semantic credit. I reviewed source and profile metadata only; I ran
no compile, verifier, Cloud action, or tool execution.

## Patch-delivery review — runner commit 9ff47c3d

The corrected composition patch is based on the intermediate translator blob
`d189d58a`, recorded as snapshot `57bdb9ed2fc45a420fb3b3f98ee004f01d709846`,
after the pinned tool-C4 and selector-integration patches. Its target blob
`2a60021e3a88eabc97cf3a80d11214739e1e05ec` matches the translator blob at
reviewed tool commit `09389e2c0a4d6d2ed4e1146df0ad6321832c12cb`. The updated
composition patch SHA `0a5eb46815defaef599cc13c2c6aaad7325da9e998661f9039f8cfc13049b147`
matches the C1 manifest. The delivery receipt records the exact three-patch
order from official base `f76012fb518703b1d98e243ac4f487f16877cfcb`, all five
effective source hashes matching the manifest, and no foreign index or
worktree mutation. The 30-module source pack and reviewed tool commit remain
unchanged.

**Delivery verdict: GO for submitting runner commit `9ff47c3d` under the
existing C1 experimental profile.** This resolves the earlier packaging-only
refusal; it gives no compile, proof, or negative-control credit. The next Cloud
run must still report its own exact patch preflight and fresh verification
results.
