# W8 region arithmetic candidate (N4 preparation)

State: **UNVERIFIED / STATIC PREPARATION ONLY**. This is a handwritten pure C
ghost arithmetic candidate. It is not source extraction, generated input,
actual Rust behavior proof, callee summary, caller proof, or B1/B2 evidence.

## Source association

Prepared against source commit `cd371e035c7e573760c43bf934d53e8118ee3e7d`,
`library/core/src/slice/sort/shared/smallsort.rs`, source blob
`40939f922bcb6fdc7ee0d30427fa861827043827`, SHA-256
`85c75bc93745ff1d4a6d33939d48408c2f7304aa8ffd952b73199ec1f8a175e1`.
The static reference is `small_sort_network` around lines 311–371, especially
the `<2` return, `>32` abort, `len / 2`, two-region selection, and the
`region.len() >= 13 / >= 9 / else` prefix choice. These are associations to
the pinned source text, not a parser/MIR/source-binding result.

## Candidate contents

* `region-arithmetic.gh` defines the integer prefix selector and split
  expressions.
* `region-arithmetic-lemmas.c` contains checked-body candidates for the
  prefix bounds and the finite `18..=32` split/choice facts. The split lemma
  uses explicit cases for every admitted length, so it does not depend on an
  unproved general division bridge.
* `len25-both-prefixes-9.negative.inc`, `region8-prefix-9.negative.inc`,
  and `len33-fits32.negative.inc` are separate fragments, each with one
  labeled prospective false control.

For a future Cloud check, assemble `region-arithmetic-lemmas.c` together with
exactly one selected `.negative.inc` fragment in a synthetic unit. Do not use
all three fragments in one unit: the first expected failure would prevent
later controls from reaching their intended assertions. Each assembled unit
must check and inventory the complete three-body positive set
(`w8_prefix_in_bounds`, `w8_split_and_prefix_facts`, and
`w8_prefix_choice_facts`) before its single negative target. The fragments
are not standalone inputs and intentionally do not include a `.c` file.

The input-length facts `len < 2` and `len > 32` remain prospective routing
observations from source inspection only. This artifact does not claim that
actual Rust returns or aborts for those values, or that the branch guards are
bound to ghost facts.

## Limits and next validation

The stock VeriFast 26.09 syntax and proof obligations have not been executed
or checked. In a future authorized Cloud phase, first bind this component to
the exact source/MIR stage and target, then check the positive unit and each
negative at its intended assertion with body inventory, return/leak checks,
and the required source-stage-target mismatch controls. Integration still
requires the actual network, insertion, and merge summaries and caller
ownership, framing, unwind, initialization, copy-back, and ZST/control-flow
proofs. No normal-termination or Challenge completion claim follows here.
