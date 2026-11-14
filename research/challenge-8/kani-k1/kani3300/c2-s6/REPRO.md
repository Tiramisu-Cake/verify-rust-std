# STOP: required hook control remains NONDISCRIMINATING / UNKNOWN

Exact input: S5 8d67298c48eb7b2381f806a6353433d1440e3d94,
tree 5fb7dbaa6f79a75ca552be9d4d5c7b535cf38058. No compiler execution.
This is a missing discriminating control, not a newly established production defect.

## Source-backed reproduction and expected distinctions

1. `repro/generated-modifies-no-shadow.rs`: legal pointer-shaped `modifies(out)`.
   Current replacement expansion is `Pointer::assignable(untracked_deref(&out))`.
   Generic hook return type is `&mut MaybeUninit<u16>`, not MaybeUninit storage.
   `transfers_shadow` only recognizes union/MU storage, not that reference.
   Therefore a successful PFC cannot count as the requested shadow-return hook control.
   Additionally a SimpleCheck PFC need not execute the replacement closure at all.
2. `repro/generated-modifies-invalid-target.rs`: change to `modifies(*out)`.
   `untracked_deref(&*out)` has the desired MU return, but generated
   `Pointer::assignable` has no MU Pointer impl. PFC check expansion also casts
   the modifies expression `as *const _`; a by-value MU cannot provide that cast.
   Source-backed expected result is a setup/type-check failure, not protocol refusal.
   Exact native diagnostics NOT_RUN; no count invented.
3. A local ordinary union implementing the public, unsealed Pointer trait could
   satisfy replacement Pointer::assignable, but still cannot satisfy PFC's
   by-value union `as *const _` cast. No mock hook or production trait/model change made.
4. `repro/ordinary-hook-return.rs` is a different candidate: explicit call of the
   actual public internal UntrackedDeref hook with reference arg / MU return.
   It is not a generated modifies-expression call. Actual reachability, ABI,
   interception after MIR instrumentation, complete protocol failure set/count,
   and exclusion of an earlier delayed-analysis failure remain UNKNOWN.
   This is the concrete next observation, not an accepted expected oracle.
5. `repro/fn-item-{plain,shadow-return}.rs` are further diagnostic candidates.
   They pass a free FnDef through a generic FnOnce wrapper without a MU argument
   tuple. Actual optimized Item versus Shim remains UNKNOWN; do not count an
   optimized Item as Shim coverage. No blanket fn-item Unsupported asserted.

## Exact implementation bindings inspected

- library/kani_macros/src/sysroot/contracts/replace.rs:131-150: generated hook and Pointer::assignable.
- library/kani_macros/src/sysroot/contracts/check.rs:56-75: PFC modifies expression cast.
- library/kani_macros/src/sysroot/contracts/check.rs:201-210: current argument copies are ordinary let bindings, no hook.
- library/kani_core/src/lib.rs:619-659: public Pointer trait and pointer/reference implementations.
- library/kani_core/src/lib.rs:667-674: real hook marker and bodyful untracked_deref<T>(&T)->T.
- kani-compiler/src/kani_middle/transform/check_uninit/ptr_uninit/uninit_visitor.rs:131-133,575-590,1233-1237:
  shadow predicate, pairing guard, LoadArgument and Item/body predicate.
- kani-compiler/src/codegen_cprover_gotoc/codegen/statement.rs:954-977: ABI lowering precedes hook dispatch.
- kani-compiler/src/codegen_cprover_gotoc/overrides/hooks.rs:747-789,1705-1711: actual marker selection and shallow dereference assignment.
- library/kani_core/src/mem_init.rs:501-553: protocol consumption assertions; no arbitrary failure count substituted.

## Disposition

Task §3 requires a legal actual hook carrier and §7 prohibits silently omitting a
requested control. Source attempts above do not establish it. STOP, no freeze,
no source commit, no new production fix. A direct ordinary call is a viable
candidate for further coordinator observation; this report does not prove that
all legal hook controls are impossible. A bounded production fix is appropriate
only if an exact observation establishes a defect; do not change the memory model
or goldens in order to force a freeze.

## Authorized HOOK continuation — superseding disposition (2026-11-15)

The preceding STOP/UNKNOWN analysis is preserved historical input. Run43645985416
established the actual direct internal hook path and FnDef shim outcomes; void run43645617823
has no semantic credit. TASK-KANI3300-C2-S6-HOOK.md authorizes the bounded typed Hook
predicate correction. Generated modifies(out) is legal NONCARRIER; modifies(*out) remains
INVALID_TARGET E0277, not a rejection control. Direct actual UntrackedDeref MU return is
the qualified rejection control, with baseline fail-closed internal placeholder and intended
candidate explicit pairing Unsupported (not a baseline false SUCCESS).

Candidate/source/control details: hook-fix/CONTROL-MAP.md, HOOK-MAP.md, CI-REQUEST.md;
current exact immutable source in C2-FREEZE.json. New useful assertions require matched
baseline/candidate observations of the same fixtures. Current disposition is preparation
complete, QUALIFICATION_PENDING; not a successful native outcome/freeze acceptance.
