# Challenge 8: historical sorting-model observations

Recorded: 2026-10-06, from the research conversation.
Companion: [C verification survey](C-VERIFICATION-SURVEY.md).
Source references: [artifact catalog](C-VERIFICATION-ARTIFACTS.md).

## Evidence status

The conversation reported the following finite checks of separately rewritten
mathematical models:

| Model | Reported domain | Reported observations |
| --- | --- | --- |
| `sort9_optimal` schedule | All 512 Boolean inputs; 25 compare-exchanges | Zero sorting failures |
| `sort13_optimal` schedule | All 8192 Boolean inputs; 45 compare-exchanges | Zero sorting failures |
| `sort4_stable` key/identity selection | All 256 four-tuples of keys from 0..3 | Sorted keys, permutation of identities and stable equal-key order |
| `sort4_stable` unconstrained decisions | All 32 five-tuples of Boolean comparison decisions | Output identities are a permutation of 0,1,2,3 |

**Reported, not reproduced in this commit.** The original model program,
execution log, environment and exact Rust source SHA were not preserved with
the conversation's report and have not been recovered. These counts must not be
added to the project's hosted verification coverage or cited as a reproducible
Rust proof. No executable model is added or run in this documentation iteration.

For a future rerun, the source expressions and schedules were inspected at
project commit `d436977f9dd2bbc8ec4892174df1fd5a2f778dee`, SmallSort blob
`e555fce440872898e47fd5114f32eb15401d07df`.
This is the pin for the reconstruction specification below, not retroactive
provenance for the earlier execution.

## Network model specification

Represent a sequence of immutable values. For each pair `(i,j)`, replace
the pair with its minimum followed by its maximum. Process pairs sequentially
in the exact source order; leave all other positions unchanged.

The following data is transcribed from the repository's own Rust schedules
(R2), not from another participant's proof code. Line breaks group consecutive
calls for readability and introduce no parallel semantics.

### Nine inputs

```text
(0,3) (1,7) (2,5) (4,8)
(0,7) (2,4) (3,8) (5,6)
(0,2) (1,3) (4,5) (7,8)
(1,4) (3,6) (5,7)
(0,1) (2,4) (3,5) (6,8)
(2,3) (4,5) (6,7)
(1,2) (3,4) (5,6)
```

### Thirteen inputs

```text
(0,12) (1,10) (2,9) (3,7) (5,11) (6,8)
(1,6) (2,3) (4,11) (7,9) (8,10)
(0,4) (1,2) (3,6) (7,8) (9,10) (11,12)
(4,6) (5,9) (8,11) (10,12)
(0,5) (3,8) (4,7) (6,11) (9,10)
(0,1) (2,5) (6,9) (7,8) (10,11)
(1,3) (2,4) (5,6) (9,10)
(1,2) (3,4) (5,7) (6,8)
(2,3) (4,5) (6,7) (8,9)
(3,4) (5,6)
```

A reproduction would enumerate all Boolean tuples, apply this model, and record
sortedness and preserved multiplicities. An independent comparison to the
source schedule is necessary: a correct model of the wrong schedule says
nothing about the Rust function.

The zero-one theorem can lift abstract Boolean-network correctness to ordered
values only after its hypotheses and the network encoding are established.
Permutation follows from the exchange operations, not from sortedness alone.
This does not prove stable ordering of distinct equal-key identities.

## Four-element selection model specification

Let identities be 0,1,2,3 and let `key(i)` return an immutable comparison key.
Define `select(c,x,y)` to return `x` for true and `y` for false.
Boolean-to-index conversion maps false to 0 and true to 1.

The five source decisions and selected indices are:

```text
c1 = key(1) < key(0)
c2 = key(3) < key(2)
a = int(c1)
b = int(not c1)
c = 2 + int(c2)
d = 2 + int(not c2)

c3 = key(c) < key(a)
c4 = key(d) < key(b)

min_id = select(c3, c, a)
max_id = select(c4, b, d)
unknown_left  = select(c3, a, select(c4, c, b))
unknown_right = select(c4, d, select(c3, b, c))

c5 = key(unknown_right) < key(unknown_left)
lo_id = select(c5, unknown_right, unknown_left)
hi_id = select(c5, unknown_left, unknown_right)

output identities = [min_id, lo_id, hi_id, max_id]
```

The intermediate identity partition is:

| c3 | c4 | Minimum | Maximum | Unknown left | Unknown right |
| --- | --- | --- | --- | --- | --- |
| false | false | a | d | b | c |
| false | true | a | b | c | d |
| true | false | c | d | a | b |
| true | true | c | b | a | d |

The proposed reproduction has two distinct modes:

1. **Key-driven decisions.** Enumerate every key tuple in `{0,1,2,3}^4`;
   preserve identity separately; check nondecreasing keys, each identity exactly
   once, and increasing original identities among equal keys. Compare by key
   only: using identity to break comparison ties would change the algorithm.
2. **Unconstrained decisions.** Enumerate `{false,true}^5`, replace c1..c5 by
   those independent decisions, and check only that the selected indices are
   exactly the four original identities. Do not assert sortedness or stability
   for inconsistent decisions.

The second mode is a selection/permutation check. It does not model callback
mutation, callback panics, allocation aliasing, pointer validity or ownership.

## What a future executable artifact must add

A new authorized hosted experiment would need:

- exact source SHA/blob, independently audited schedule and selection encoding;
- model code committed before execution, with stated order and identity domain;
- expected checks/counts and explicit failure reporting;
- hosted run URL, source/model hash, command/tool environment and retained output;
- a precise statement of what was checked separately from the actual Rust;
- a separate formal connection to actual source operations before claiming
  Challenge coverage.

These are reproduction requirements, not an instruction to implement or dispatch
a run now. The current phase/stop state in [STATUS.md](STATUS.md) remains in force.

