# H2b local acceptance: O18/O19 production and isolated O20 adversarial posts

Scope **ACCEPTED_LOCAL_H2B_OPTIONAL_STORAGE**, exact O19/O20 twelve-patch
production profile, pinned std/VF/compiler/schema/exporter/refiner/specs.
Production console `d23f655202171369dd803db3e4016bfdd7ae365dfef133c7cb58139b2a809e73`,
translator `6abe2aa920dfe9cc193d1331d0ee5e90310f2ac7609b03d92f3000959d5115bf`,
applied diff `968a36c15523a3de0960d90c9d35b8fac8ba0d69e3889aae2f062ff2b9f0ef54`.
No actual nested DefPath, helper, SAFEforget or sort4 claim. O17 remains its
historical local-candidate result; O18 admission review remains unchanged.

Production proof O19 `a6f9d5e00cc99c06f8c49fa2e27e6a92308a1a79`,
[run37746579002](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37746579002).
Full local generic callee and source-shaped SAFE guard Drop verify normal and
unwind returns/posts/leak; owner constructor, concrete witness, OrdinaryDrop
verify. H2 source7, independently verified typedMIR12, owner/resource negatives
and generic callee6 controls retain intended failures. Fresh fullS6 eight-stage
regression passes. O18 independently established causal H2c source-gap repair
and exact one-field MIR mutations; its audit contains those full details.

O20 `e30bdc72d7af37222c401dd54ed50759eb840547`,
[run37748156620](https://github.com/Tiramisu-Cake/verify-rust-std/actions/runs/37748156620),
isolates TEST overlay `d073bfd93b0a4010842144c713d708a8a550ebcb79af8388832cd41d52d30063`.
TEST console `9bc692525f13f99ba23e3f4098d34bde4a50b0d9bfdf65730c470ac63d5365f6`,
translator `fdda5f2ebf73fb3614ef0d142c8a7bc5bc1f82647d73c14de0fce1b737a1f2f9`.
Independent manifest/copy/apply/build audits preserve exporter/refiner/specs;
TEST console never runs actual/S6 or enters production cache. Root reviewed
no-key AST equivalence. No-key positive fullVF0, both generic method and guard
return/leak paths, owner/witness/OrdinaryDrop. All five mutants use identical
source, paired NORMAL/readonly export/decode/refinement0 and source integrity;
generic callee proves both paths first, selected guard executes real call then
fails precisely its changed generated post (sole error, no Fatal/setup failure).
Original diagnostic classifications are retained; reviewed verdicts below.

| Mutant | Reviewed intended failure | Outcome trace |
|---|---|---|
| initialized | prelude_core:213 cannot entail initialized `some` from optional `dummy`; consuming generated guard post65 | unwind return at real call69; zero guard leak completions |
| t_own | generated post65 missing `own(T_typeid)(_t,_)` | unwind return69; zero guard leak completions |
| second_cell | generated post65 missing second `points_to_<T>(inner,_)` | unwind return69; zero guard leak completions |
| false_normal | generated post65 cannot prove false | unwind return69/leak completes first; normal return70 then fails |
| false_unwind | generated post65 cannot prove false | unwind return69 then fails; normal branch not reached in failed verifier traversal |

Normal/unwind identification follows the unchanged typed graph and return
source spans, not assumed traversal order. The two false variants demonstrate
separate outcome posts; strengthened resource assertions on both outcomes first
fail on unwind. All five are intended generated-post controls after root review.

The nominal owner truthfully requires initialized selected storage and generic
`T.own`; no owner is created by the guard or from bytes. After destruction only
optional pointee storage is returned, retaining stock thread/field/padding and
lifetime resources. Primitive `drop_in_place`/compiler layout/free drop glue and
source-to-MIR correspondence are trusted dependencies inherited from the pinned
profile, not proved universal Rust destructor semantics. Checked same-unit
generic callee body and guard body use these explicit contracts. New H2b trusted
frontend rule chooses this narrowly source/ADT/full-MIR-gated generated post;
the real body proof and adversarial controls constrain it, not an axiom of the
helper goal. `T` is implicit Sized as in this source-shaped unit; no extra Copy,
Freeze or purity restriction. No Element pointee rights occur here.

Actual nested guard needs separate complete source/qualifiedADT/MIR admission
and same-unit callee proof; ordinary SAFEforget needs a verified source summary,
nominal ownership and justified nounwind call linkage. These obligations are open.
