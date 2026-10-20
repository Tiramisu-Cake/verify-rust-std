# R8 S2 focus-scoped dead-code registration rationale

## Defect and applicability

The first R8 target run reached the selected P0a function body but failed its
dead-code check on statements outside that body. The bounded S1 observations
identify the selected compiler body as `verified/lib.rs:44` with MIR span
`44:4–47:5`, and the selected VeriFast focus as line 44 (line 47 is the
function's closing span). The exact pinned
source bytes (`dbcc37321090ac46f90f8cce653e5ce28f6528dfc594bec23340ffd7ac91e2c7`,
lines 42–53) place the default threshold body at 44–47 and a separate
`small_sort` signature starting at line 50. The exact+complete bounded log
scan (`608b9cc62db3f8956e7004bba3d69ac8319affeff0babf78f00e893c7615b135`)
reports AST/REGISTER IDs 55 (`Expr`) and 56 (`Goto/Goto/If`) at 55:12–24,
then DEAD for both; it contains no EXEC for ID 55. A distinct registered
DEAD ID 52 spans lines 50–58. The primary diagnostic is
`verified/lib.rs(55,12-24): dead code`. This establishes an excluded-source
registration failure, not a proof of why symbolic execution omitted those
IDs.

At pinned VeriFast tool head `f76012fb518703b1d98e243ac4f487f16877cfcb`,
`verify_expr.ml:154–162` defines the inclusive source-path/range `check_focus`
predicate. The S1 observation records current focus 44; source lines 54–58
show `if v.len >= 2` in the separate `small_sort` function beginning at line
50. The ordinary `Func` registration path walks bodies unconditionally
through `reportStmts`, while `verify_func` checks the same body under
`check_focus l closeBraceLoc`. This is the AST function class used by the
focused Rust input and the class containing the S1 registration; the
registration caller already has exactly the endpoints used by the symbolic
body gate. Scope that registration walk with the same `check_focus` predicate
and endpoints. Main accepted this narrow Rust `Func`-path boundary. C++
constructor/destructor and Java constructor/method registration paths are
separate AST/body paths outside this Rust R8 fix.

This is an experimental, source-level tool patch under the existing R8
profile. It changes no parser, AST/MIR identity, diagnostic format, dead-code
map identity, rejection rule, `src/verifast.ml` kernel, proof model, compiler,
Rust input, or runner algorithm. Main separately authorized the single
`a1-runner.py` `FOCUS_SEMANTICS_PINS` literal transition for
`src/verify_expr.ml`; all other core bytes and checks stay unchanged. The
exact base-to-result source transition is separately pinned. It must not claim
proof acceptance.

The source chain is explicit: pinned tool HEAD `src/verify_expr.ml`
`f2a2a32c…` → existing diagnostic-only patch `c2246e54…` → this R8 focus
scope patch `2d17c360…`. The kernel remains
`src/verifast.ml=37ed2550…` throughout. The pre-overlay native C4 snapshot is
compared to its historical `c224…` baseline first; the new patch applies only
after that comparison and before the R-only reference build. The R-only
receipt binds the new patch and resulting verifier source hash.

## Preserved guarantees

- A statement in the selected function remains registered. If it is not
  executed, the existing dead-code check still rejects it.
- With no focus, `check_focus` invokes its continuation, so the existing
  whole-program registration and dead-code rejection remain intact.
- Bodies excluded by focus do not contribute dead-code entries to the focused
  invocation, matching the existing symbolic-body selection.
- Registration and execution retain physical source-location identity;
  diagnostic and kernel code remain unchanged.
- The pinned `src/verifast.ml` kernel hash remains unchanged. Only
  `src/verify_expr.ml` has an explicit base-to-result transition, from the
  currently pinned diagnostic bytes to the exact focus-scoped result.
- The R8 core pin changes only the literal for `src/verify_expr.ml` from
  `c2246e54…` to `2d17c360…`; no profile-controlled arbitrary hash is accepted.
- All other verification checks and all 26 semantic matrix inputs remain
  unchanged. The R8 profile remains `profile_accepted=false` until independent
  evidence establishes otherwise.

## Differentiating controls

The compatible Cloud regression set must demonstrate all three conditions on
the exact patched tool and profile:

1. **Selected-body negative:** focus a body with a genuinely registered but
   unexecuted statement; it must exit 1 with the dead-code diagnostic at the
   exact unreachable assignment line.
2. **Excluded-body positive:** focus a distinct clean body while an excluded
   function contains that unexecuted statement; it must exit 0 with no
   dead-code diagnostics, using the same source and all other checks active.
3. **No-focus negative:** verify the same whole source without `-focus`; it
   must exit 1 with the same exact dead-code source line.

Setup/parser failures, failures at another obligation, or incomplete execution
are inconclusive for this regression. No local compiler, tool preparation,
proof, or verifier execution is authorized.
