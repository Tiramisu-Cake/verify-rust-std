# C1-only compiler Output equality — preimplementation review

Written 2026-10-09 17:14 UTC after first actual Build3c845267, before change.
Exact c1 unwind recovery/full unwind post/leak reached; normal fails on
FnOnce::Output expected bool after successful unwind. Category: incompatible
proof type interface, not missing ownership or borrow debt.

## Exact derivation and bounded change

Paired complete MIR/source pins remain667e4347/925b05a8/fddb6f1a. Compiler
clauses in normal full record16950–16991 universally quantify two distinct
regions '__14/'__15 over F:FnMut<(&'a T,&'b T)> and matching
<F as FnOnce<(&'a T,&'b T)>>::Output=bool. Existing decoded-clause matcher
validates paired regions/shared mutability/F,T params/Sized generics/Bool RHS
and matching FnMut trait. Instantiate both universal regions with 'cmp;
this follows Rust's actual signature, not the expected destination type.

Retain matcher result as data under exact sort4 AST opt-in only. Keep old
pre-rewrite AST/whole-source/c1-switch hashes and no old body-wide HRTB opt-in.
After exact original AST/c1 switch validation, require exactly [F,T], exact
c1 call F/tuple(&'cmp T,&'cmp T)/method'cmp. Insert one existing
#register_type_projection_equality immediately before c1 switch. No injection
at c2–c5 or other bodies; no new kernel builtin. New separate patch after frozen
5b9cac96 overlay; ordinary git apply. Default output equality OFF. Record one
site under explicit output equality ON; absent/malformed opt-in or unmatched
compiler/call tuple must refuse.

## Conservation argument and self-review

One ghost typing fact, no ownership/heap permissions created or consumed.
The universal compiler clause justifies the instance; this does not infer rights
from address equality, assert purity, constrain F aliases or constrain CURRENT
values. Original callback, ordered refs1/0, normal assignment and unwind
continuation/posts/runtime operations unchanged. Retain exact source/MIR/preAST
and original c1 switch hash. Only postAST differs by this ghost registration.
Strict kernel/alias/prelude stay frozen. Do not enable the older target-wide
HRTB option, which could rewrite later calls and invalidate original AST pins.
Critical risk: collecting bounds alone is not a theorem; exact unique parsed
compiler clause plus actual pinned call types must precede registration.

## Affected gates / next decisions

Fresh complete source/MIR/refinement, frozen kernel and exact postAST identity;
same-unit recover_pair/join before caller; six strict-scope cases and false
normal/unwind posts rerun under resulting console. Additional actual equality
OFF must reproduce exact c1 Output/Bool failure after the unwind path; actual ON
must emit exactly one c1 fact and zero later registrations. These are intended
type-interface controls, not resource negatives. Broader mutated HRTB clauses,
source/scope/alias/storage/profile qualification remain OPEN; exact caller's
compiler clause is input-pinned. No profile admission upgrade.
PASS of c1 normal close/scope/recover/join permits only c1 resource/premise
review; c2 failure is recorded without fixing c2. Unwind credit stays separate.
New missing-resource/debt/false-post gates selected only for affected actual
resource interface; no heap filtering or weakened leak/unwind checks.
