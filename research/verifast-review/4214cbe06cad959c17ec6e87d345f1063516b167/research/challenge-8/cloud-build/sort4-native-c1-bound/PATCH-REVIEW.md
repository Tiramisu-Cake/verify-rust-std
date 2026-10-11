# Native C1 bound translator patch — DRAFT / CORRECTION NOT_RUN

The patch `native-c1-bound.patch` applies only to the capture-only translator
SHA-256 `86952a6ac4a61ac854d8a9886cff98ee143a0e75ccf8148fb84e07c0a14ce544`
on tool HEAD `f76012fb518703b1d98e243ac4f487f16877cfcb`. Its result is
SHA-256 `381e80ebe9a789877ee9d0e860da386f7692f54879b39775e01267f0db6f53d6`;
the patch is SHA-256 `eea19eda3723a0f60970df751c7600c326f98ad476d41f61e3f39442beb88693`.
The existing kernel SHA-256 is `37ed2550d276abccbbe0a9ced678137ef587f80782bcff763062df394c2a440c`.
`patch --dry-run -p1` against that capture tree succeeded. There has been no
local compiler or proof execution. The tool profile is **unaccepted**.
An independent static review found the exact MIR inventory consistent with
the canonical d776 artifacts and permits a diagnostic Cloud run only after the
driver hard-gates immutable paired MIR hashes and refinement before verifier.

The first Cloud attempt (7456e9be) passed the full MIR/refinement and refusal
gates but stopped before the bound body at its original pre-AST hash. The
generated `fc2d58d080d63cb0e95f65c626a2567f0cb156a91b60b22a9fd1d2231f8de24b`
differs from the capture AST solely because the already-frozen generic
strict-cut pass had inserted `#strict_lft_binding_scope` at source line 172,
changed the source line 212 `end_lft_binding` to `Goto 47`, and emitted the
outer `Label 47; Noop`. The corrected patch admits the bound mode to the
**existing exact-source native capture exception** while original AST is
constructed. That exception still checks exactly one regular `'cmp` cut at
source line 212; the bound branch then constructs its already-reviewed strict
child and outgoing cleanup wrappers. The full original SHA requirement remains
`18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5`.
Default-off and all unrelated generic strict-cut paths are unchanged. This
source-cut correction passed its next Cloud admission gate.

Fresh build `10006623` passed bound admission and reached normal and direct
callback cleanup. The false-normal and false-unwind controls failed at their
intended assertions. The positive run discharged the source assertions,
automatic return post, free and leak checks, then reported only
`verified/lib.rs(228,2): dead code`. Its post-AST placed the added unwind
epilogue after the compiler's original final `Label 63; Return(returning($_0))`.
The verifier's statement reachability check requires that final translated
normal return chain remain last. The narrow CFG correction guards the exact
seven original tail nodes—`Goto 62; Label 62; Goto 63; Label 3; Goto 63;
Label 63; Return(returning($_0))`—then places the direct-unwind epilogue
between the first `Goto 62` and the remaining six original nodes. The normal
and early zero-size branches jump over it to their original labels; actual
callback unwind enters the epilogue, executes all four cleanup blocks and
returns. No source assertion, normal/unwind post, local-free path, leak check
or dead-code check is removed. This CFG correction is not yet Cloud-verified.

`SORT4_NATIVE_OPAQUE_C1_BOUND=1` is default-off and rejects malformed values,
other active C1–C4/capture modes, missing `SORT4_ACTUAL_AST_SCOPE_TEST=0` or
`SORT4_STRICT_LFT_CUT=1`, and unrecognized controls. The optional control is
`SORT4_NATIVE_OPAQUE_C1_BOUND_CONTROL=none|normal_false|unwind_false`. Only one
`small_sort_general_with_scratch` runtime body with unwind and specless checks
enabled is admitted. The translator checks the complete verified source hash
`7ebcf7cd435c31b3f4669ac6f31a62fd45fcb2c7fa03500bdfbc44ccaca01742`,
the exact source marker/call/cut lines, 79 MIR locals and 64 blocks, `_5`'s
bb0 live/bb1 dead events, callback local live/dead events in bb43–45, and the
bb0 len and bb43 pointer-add normal/Continue edges. The sole compiler FnMut call in bb44
must move `_55`,`_56` without projections into `_54`, target bb45 normally and
have a direct `Continue` unwind. The driver separately pins the normal and
readonly typed-MIR hashes and refinement result.

Before rewriting, the translator writes `native-c1-bound-pre-ast.ml` in the
fixture working directory and requires its full SHA-256
`18973de5dd5ff1a9c94652fd808d42ffe2297096adb8a3cc1980f74a554ccea5`.
It checks 134 root statements and 76 local declarations; `_5` remains outer,
while only callback locals `_55.._62` move from root indices 52–59 into the
unique `'cmp` child. The child must contain the checked four-block source
unwind marker, unique actual FnMut switch, normal debt close, original cut and
goto at fixed source locations. The rewrite inserts the existing narrow
strict lifetime scope and an `Output=bool` projection equality at that real
call, routes its direct unwind through debt close and an external epilogue,
then executes all four source marker cleanup blocks before the original
`unwinding()` return. The normal route keeps source recovery, full native
CURRENT source/scratch/F/thread post assertions, type leaks and unit return.
Both routes keep the original automatic contract through `mk_fn_decl contract`.
The resulting declaration is written as `native-c1-bound-post-ast.ml` for
independent comparison. A successful admission prints
`NATIVE-OPAQUE-C1-BOUND admitted ... NOT_CALLABLE_SUMMARY`.

`normal_false` inserts `assert false` after all normal source post assertions
and type leaks but before the original unit-return goto. `unwind_false` inserts
it after the fourth direct-unwind cleanup block but before the original unwind
return. These are localized diagnostic controls only if a fresh log reaches
them after the real FnMut call. The driver must classify setup or earlier
resource failures as inconclusive.

Open review items: the exact post-AST still needs fresh capture and a full
normal/direct-unwind free-path audit. MIR also has a `ptr::add` `Continue`
unwind edge before the callback, and the `v.len()` call precedes the `_5` dead
event. This patch leaves their frozen lowering untouched; a reviewer must
check stock primitive behavior and all represented outgoing paths rather than
infer that `Continue` alone makes them impossible. The callback-free prepared
positive currently stops at reverse reference-own opening, so no actual
callback theorem or whole-sort4 proof is claimed here. External slice-pointer
method summaries, caller guards and call edge are still separate obligations.
