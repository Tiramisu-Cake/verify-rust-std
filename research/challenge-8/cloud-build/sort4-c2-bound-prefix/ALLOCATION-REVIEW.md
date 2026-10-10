# C2 bounded-prefix allocation review — saved inputs, before Cloud proof

Read-only review of the A5DE full source-linked AST and typed MIR, plus the
isolated VeriFast kernel. This is a conditional admission assessment for the
new bounded C1+C2 projection, not a proof result or profile acceptance. No
compiler, extractor, verifier or proof command was run for this review.

## Exact saved input and declaration inventory

The saved `actual-c2-unbound-scaffold-ast.ml` has SHA-256
`4fa7d49e420dc80681328bacdf08bb1d674dc2413001b99501da1c09b11dbb0a`.
The complete normal/readonly MIR hashes are respectively
`e270457999f9371bc94664917ebd96699eecec0b91148899aa48c511f398c82b`
and `3598b01b91af60d4ad5f96cabc8225aad30bb9a2bd73eb7fc7add15473fb1a29`.
All three saved file hashes were checked directly. The AST has 161 root
`DeclStmt`s. Every root declaration has no initializer and an initially false
`address_taken` reference. The proposed bounded AST retains 143 declarations:

| Placement | Count | Types and kernel effect |
| --- | ---: | --- |
| Outer function | 125 | 59 `std_tuple_0_` structs can call `produce_object`; 41 pointers, 19 bools and 6 `usize` values are uninitialized symbolic locals with no points-to chunk |
| C1 strict scope | 8 | `_28` is a `std_tuple_2_` object; five references and two raw pointers are symbolic locals |
| C2 strict scope | 10 | `_64` is a `std_tuple_2_` object; five references and four raw pointers are symbolic locals |
| Excluded future calls | 18 | `_99`, `_106`, `_135` are `std_tuple_2_` objects and the other 15 are references; none has an initializer or address taken before the boundary |

Among the 59 retained outer unit structs, `_148`, `_151`, `_155`, `_159`
and `_163` belong to source lines 253–257, after C2. They still allocate
abstract local objects eagerly in the bounded AST. They are extra framed
resources, not source/destination owners; all five must be consumed on each
normal or unwind exit. The four unit structs `_73`–`_76` belong to C2
source lines 224–227 and stay in the prefix. The other retained unit structs
are from earlier prefix operations.

## Why the three omitted objects are outside the bounded path

The complete normal MIR places the future `_98`–`_103`, `_105`–`_110` and
`_134`–`_139` first `StorageLive`s at source lines 241, 242 and 249. In the
readonly MIR the corresponding later locals are `_98`–`_109`, first live at
254–256; `_110` and `_134`–`_139` are absent. The saved-data gate pins the
full MIR hashes and checks the exact block graphs: normal 82 blocks, readonly
28 blocks, contiguous normal successors, no cleanup blocks, direct `Continue`
unwinds. C2's FnMut is normal BB53 / readonly BB4; the first future live is
BB62 / BB21. Neither C1 nor C2 direct unwind enters future storage.

This justifies omitting those declarations from the **bounded execution**:
the source/MIR boundary is after C2's normal join at line 227 and before the
later calls. The full source and pre-transform AST still include all five
FnMut calls, eight selects, four copies and all 161 declarations. The AST
projection does not grant ownership or infer permission from pointer values.
The MIR `StorageLive`/`StorageDead` cases lower to no proof statement in this
translator; their timing is source correspondence evidence, not an AST heap
event.

## Kernel resource and exit obligations

In `src/verifast.ml`, `DeclStmt` with an uninitialized struct calls
`produce_object` (near lines 1024–1072); uninitialized non-struct locals with
`address_taken=false` receive fresh symbolic initial values and no heap
chunk (near lines 1073–1130). `verify_c_func_body` wraps the function in a
`BlockStmt` with `outer_locals` (near line 3513). `BlockStmt` frees local
objects on normal exit, return and goto, including a goto leaving either
strict scope (near lines 180–198 and 2880–2900). Thus the expected footprint
is: 59 outer unit-struct producer sites on every bounded path; C1's tuple
producer only once C1 is entered; C2's tuple producer only after C1 normal recovery. A C1 direct
unwind cannot acquire C2's tuple, and each unwind goto must free the tuple
from its own scope before recovery/post checking. The five outer future unit
producer sites are an extra conservative produce/free burden on every bounded path.

This assessment depends on the **emitted post-transform AST and actual heap
trace**. Before accepting the bounded theorem, inspect the fresh Cloud
post-AST for exactly the retained 143 declarations and no future 18, no
duplicate/escaped scope locals, and the exact original callback/post arms.
Inspect normal, C1 direct-unwind and C2 direct-unwind traces for matching
`produce_object`/`Freeing locals` effects and full return/leak/post checks.
Check the first failing obligation of each resource and branch control at its
intended target location. A VF0 result alone cannot settle allocation
admissibility or accept the experimental profile.
