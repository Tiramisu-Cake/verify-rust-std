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
* `region-arithmetic-lemmas.c` contains candidate bodies for the
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

`ARITHMETIC-INPUTS-N4.json` uses input schema
`smallsort-w8-arithmetic-inputs-v1` and pins the source and byte inputs. The
preparer also pins this manifest's raw SHA-256 and the exact input path/SHA
allowlist before accepting caller-selected paths or bytes. The inert module
`prepare-region-arithmetic.py` exposes pure byte validation and assembly
helpers. Its CLI first calls the existing provider guard, then reads the
manifest, pinned source bytes, and exact inputs; it writes only to a new
output directory and removes a partial directory on failure. It emits one
positive unit and three separate positive-plus-one-fragment units, along with
the header definitions closure and preparation metadata. The metadata records
source, input, and assembled-unit hashes, the complete three-body positive
inventory, each unit's full body inventory, and distinct marker, fragment
assertion, and assembled-unit assertion lines for each control. The expected
diagnostic predicate remains null/unpinned, so target-line metadata alone
cannot establish acceptance.
The output schema is `smallsort-w8-prepared-arithmetic-v1`. Its lexical body
and banned-token checks only establish that expected source bodies are
present and no explicit `assume`, `assume_correct`, `lemma_auto`, or `axiom`
token was found; they do not establish that any body verifies. Negative
fragments with CRLF line endings are refused so the reported source
coordinates stay exact.

`test_prepare_region_arithmetic.py` tests only synthetic byte fixtures and a
mocked provider. Twelve tests passed for success, refusal, provider-gate
ordering, and partial-write cleanup. Tests exercise main only with mocked
provider and synthetic files. The CLI was not invoked on actual repository
proof inputs, and no actual assembled unit hash is claimed in this handoff.

The input-length facts `len < 2` and `len > 32` remain prospective routing
observations from source inspection only. This artifact does not claim that
actual Rust returns or aborts for those values, or that the branch guards are
bound to ghost facts.

## Limits and next validation

The stock VeriFast 26.09 syntax and proof obligations have not been executed
or checked. Importing the helper is inert; only a future authorized Cloud
invocation may use its CLI. In that phase, first bind this component to
the exact source/MIR stage and target, then check the positive unit and each
negative at its intended assertion with body inventory, return/leak checks,
and the required source-stage-target mismatch controls. Integration still
requires the actual network, insertion, and merge summaries and caller
ownership, framing, unwind, initialization, copy-back, and ZST/control-flow
proofs. No normal-termination or Challenge completion claim follows here.
