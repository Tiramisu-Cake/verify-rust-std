# R15 selector permutation dependency draft

`a1-actual-selector-permutation.rs` isolates the five arbitrary boolean selector decisions in the actual `sort4_stable` body. Its pure ghost lemma takes all ten intermediate/output indices as integers and states each selector equation as a disjunction of Boolean cases, avoiding conditional expressions in the contract. The body enumerates all 32 boolean assignments and asserts the resulting four output indices. The postcondition bounds `imin`, `ilo`, `ihi`, and `imax` to `0..=3` and proves all six pairwise inequalities, so the selected outputs form a permutation of the four source positions.

The lemma assumes no ordering relation between comparator results, comparator purity, `Copy`, `Freeze`, or element-size condition. The generic pointer-parameter function is a minimal MIR target anchor; the lemma itself does not depend on `T`.

The negative lemma keeps the same selector equations but asks for `imin == 4`; its intended failure is the false selected-index postcondition after calling the positive lemma. This is a source-only negative control, not proof evidence. A 32-case synthetic arithmetic oracle is the only local validation. No actual-source preparation, compiler, exporter, or verifier was run; the draft needs ordinary source-pair, focus, parser, and proof review before any integration.
