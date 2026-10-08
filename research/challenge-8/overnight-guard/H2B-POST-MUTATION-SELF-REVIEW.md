# H2d test-only selected Drop post: static self-review

`verifast-h2d-test-only-drop-post-26.10.patch` is an isolated overlay after
H2c. It statically applies to the staged O18 H2b/H2c translator source.
It has not been compiled or verified and is not an accepted proof profile.

The opt-in key is read only after the existing H2a exact local
source/full typed-MIR certificate and the H2b same-root template gate.
Without the key, the selected `DropOnPanic<T>` branch constructs exactly
the existing `Ast.Sep(Ast.PointsTo(inner, RegularPointsTo, DummyPat),
stock_padding)` and passes the same `post` to both outcomes. Ordinary Drop
types still take stock padding and `post,post`. No precondition, runtime
source, ownership predicate, pointer method, redirect, ADT gate or memory
rule is changed. An unknown key or key without H2b rejects before proof.

The five named mutations each change only the generated selected post:
`initialized` switches `DummyPat` to `DummyVarPat`; `t_own` adds a generic
`TypePredExpr(T,"own")` assertion with an existential value; `second_cell`
adds another optional pointee cell; `false_normal` and `false_unwind`
conjoin false to exactly one outcome. The stock field own/padding/thread
fold is retained. `assertions.ml:1638–1651` distinguishes `DummyPat`'s
uninitialized points-to symbol from `DummyVarPat`'s initialized one.

`capture-h2b-post-mutation.py` constructs one byte-identical source fixture
for all variants, first requires an unmodified positive full proof, then
runs the mutants with the test key and captures paired MIR/refinement and
the full verifier log. It records the test overlay and console hashes.
`run-h2d-test-console.sh` is the separate hosted build boundary: it copies
the pinned, already patched production VeriFast checkout, compares its
uncommitted diff byte-for-byte with the production manifest, applies only
H2d in the copy, restores pinned build dependencies if the production
console cache skipped them, removes the copied production console and
builds a distinct binary. The script checks that exporter, refiner and
support specifications match production/stock, records all relevant
source/binary hashes, and passes only the H2d diagnostic fixture to that
TEST console. It never writes the production console cache and never runs
S6 or actual Rust against the TEST console. The script passed only
`bash -n`; no hosted build has used it yet.
Mutant outcomes are deliberately `POST_MUTANT_DIAGNOSTIC_ONLY` or
`GUARD_POST_FAILURE_REQUIRES_REVIEW`: the exact first error's branch,
predicate and location are unknown until hosted execution. A later
classifier may promote only a failure after the checked generic callee
and real guard call, at the named generated post. A setup error, missing
marker, failed source/MIR certificate or unrelated proof failure cannot
become an intended negative.

This test console is *never* positive proof evidence for the actual nested
std Drop. The production H2b/H2c positive and its separate admission
matrix remain the relevant local component evidence. The actual nested
DefPath requires its own source/MIR and caller resource proof.

## Root review and isolated hosted integration (2026-10-08, before O20)

Root inspected `gen_drop_contract` and Ast constructors against pinned26.10.
`ExprCallExpr(TypePredExpr(IdentTypeExpr(T),own),[LitPat(tid),VarPat(value)])`
matches existing generic-owner construction; DummyVarPat distinction is
explicit. Each mutant changes only selected generated post, retaining stock
resources, pre and checked real body. Key absent constructs the same assertion
AST as production (binary bytes differ because the isolated overlay is compiled).
Unknown key/template-off rejects. Never permit this TEST key/console as actual
proof evidence. Main approves isolated diagnostic execution, not acceptance.

Root reviewed `run-h2d-test-console.sh`: copy exact pinned production source/diff;
re-establish pinned build dependencies on cache hit; fresh separate binary; audit
exporter/refiner/spec identity, explicit test manifest; run only H2d controls; no
production cache write. Static patch applies after all twelve O19 patches;
`bash -n` and non-executing Python AST parsing are permitted server checks.
Full post errors/outcome order must be inspected before classifying any mutant.
