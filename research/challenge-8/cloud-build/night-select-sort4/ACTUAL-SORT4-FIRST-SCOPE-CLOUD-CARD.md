# Actual sort4 first callback scope TEST (Cloud only, blocked)

The exact O24 `sort4_stable` source enters its first `FnMut` call and refuses
the reserved unwind handler at verified source line 185. The print-only AST
probe preserves complete function snapshot
`dc7e8487ae46470ebcb9f964cb158c44d9bf75042cffa79d465f4d7e67001d39`
and locates that call inside the unique comparison lifetime block. An isolated
strict CUT relocation fixture verifies, but its rule is not accepted for the
actual function. This TEST asks whether a reviewed, exact AST scope rewrite can
place the comparison lifetime exit after the first call's normal and unwind
resource recovery while retaining the original full normal/unwind posts.

Only the already-built isolated strict relocation tool is copied. The new
patch may touch only its translator, and its conditional actual-sort4 branch
must leave other functions, the kernel, parser, schema, specs, runtime source
and existing cut/relocation paths unchanged. It is a semantic frontend TEST,
not accepted production behavior. The committed proof patch and review
manifest require exact hashes and a recorded prerequisite review before Cloud
execution; until then the runner reports `BLOCKED_UNTIL_REVIEW` and exits.

The same Build must first supply a complete strict relocation diagnostic,
reviewed strict CUT matrix and intended false normal/unwind post controls.
The production-console actual-source baseline must preserve source
`fddb6f1a0a90948042c99fd1037b7e939586c9e7b9e46a63367a7d876e04ccc9`,
original `3602050e45025745d80b308802be9e552310959abcee4b95bfe8c24f8ca04b72`,
complete NORMAL/readonly graph hashes `667e43477674d9e834b462b612f498af81598ec18622f0a60337ae4fdc6b017d`
and `925b05a8c2bb66be8ad5a7f091f8232d9e930782b5ca01067cf7d1bec349f5b5`,
55 blocks, 137 locals, five FnMut calls, eight selects and four copies,
paired refinement and first reserved-marker refusal. Its console SHA must
match the production SHA recorded by the same-Build relocation audit and
differ from the isolated strict CUT console. No old proof verdict
is inherited from a new tool or source.

The patched tool must be compared with the exact source/patch and stock
binaries before and after execution. The fresh production-profile O24 baseline
must retain the source-line-185 reserved-handler refusal. With the AST test
set to `0` and strict CUT opt-in absent on the patched tool, strict CUT must
refuse the first cut at its
explicit opt-in check; this early frontend refusal is only an off control, not
an actual-body negative. A separate strict CUT control selection must keep
the reviewed control verdicts on the new console. The enabled branch runs the
unweakened full actual proof with both `SORT4_ACTUAL_AST_SCOPE_TEST=1` and
`SORT4_STRICT_LFT_CUT=1`, and preserves raw logs, exit, first error, source
and tool identities. Milestone lines in the raw log remain observations if a
later normal or unwind obligation fails; they are not independent path proofs.
An exit zero is only an
experimental full-body result until every source/MIR/AST mutation, liveness,
alias/escape, pointer validity, heap/bound, false-post, no-cut/S6 and generic
admissibility gate is reviewed. A setup or admission refusal cannot count as
an intended resource negative. Nothing here claims a full actual-sort4 theorem.
