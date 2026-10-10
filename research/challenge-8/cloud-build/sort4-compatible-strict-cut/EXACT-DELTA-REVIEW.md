# Parent addressed static review — diagnostic only

2026-10-10; review after semantic card and independent DESIGN-REVIEW, before
any Cloud compilation or proof. Exact two-file delta patch
01f52d929a3678aed81bef8659f4e0ad6926487da1667139e7a66d6664526154,
production translator4d3a190f/kerneladbf2c3d to753166a8/7870f3eb.
Verdict: GO for an isolated fresh capture-only Cloud diagnostic; NOT profile
admission and NOT native/C1 helper proof. Frozen production remainder must stay
byte-identical. No copying of a historical experimental kernel is admitted.

Translator2697..2710 passes explicit strict scope metadata; find_blocks5390..5455
checks the end/head/successor shape, forbidden ingress and reentry. 6511..6626
admits only one exact marker in its named let_lft block, rejects marker-bearing
strict-OFF and ignored unwind, shortens the block at the marker and preserves
the original exporter brace dummy as Noop. This Noop is the obsolete brace,
not the end_lft obligation: the generated #strict_lft_binding_scope is operative.
5500 adds that scope discriminator. Capture7008..7045 serializes the complete
Func, checks immutable marshal identity, and capture-only1 deliberately refuses
FULL_ORIGINAL_AST_CAPTURED_NOT_PROOF before target verification.

Kernel2526..2640 freezes resolved inferred types/bounds and rejects unresolved,
cyclic or unsupported forms; validates the sole local lifetime declaration.
2725..2733 scans local type identity and bounded equality arguments/results.
2799 preserves strict heap chunks instead of the legacy type-scoped filter.
2825..2886 checks current outer bounds, exit outer variable types and EVERY
live chunk type argument BEFORE any rebase. Rebase restores only immutable
entry metadata for outer parameters, preserving predicate, coefficient, terms,
size and chunk count. Normal continuation, return and outgoing labels all pass
through token restoration and free_locals then the escape check (2892..2910).
Exception escape is explicitly refused, not skipped; Rust direct-unwind CFG
must be independently reviewed in fresh capture. Finally restores bound table.

Material unresolved compatibility risk: an F/FnOnce::Output equality mentioning
cmp may be refused as current outer bound metadata. Do not erase it by rebasing
before checks. This candidate can be conservative and fail; no compatibility
result is inferred. Binder-sensitive type forms and inference/heap/outer-type/
bound escape, debt/owner/token conservation, all exit/free mutations and frozen
C1/C2/production regressions still need concrete fresh target-first fixtures.
The invalid outer-type/bound fixtures are explicitly NOT_RUN. No green count
would admit this rule. Existing C3/C4 conditional results keep their own chain.

The first new Cloud run uses capture-only1 for all strict-ON cases. Compilation,
paired MIR/refinement and fresh AST/refusal are diagnostic evidence. Every
strict-ON helper/escape proof remains NOT_RUN pending fresh addressed review;
ordinary default-OFF and marker-OFF control retain their separate classifications.
