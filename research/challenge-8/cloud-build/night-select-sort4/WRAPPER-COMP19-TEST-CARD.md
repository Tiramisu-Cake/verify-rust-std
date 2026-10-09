# Wrapper-rebase component 19 Move/Copy negative — draft Cloud TEST

The actual `select_unpredictable` SAFE forget in the wrapper-rebase source is
block 16 of the freshly observed 52-local/35-block NORMAL typed MIR graph. Its single
argument is `Move(_34)`, destination `_33`, normal successor 17, and cleanup
successor 34. This TEST changes only that argument operand to `Copy(_34)` in a
disposable exporter wrapper. The source, real exporter, READONLY export,
refinement, cleanup edge and all other NORMAL MIR fields remain exact.

First, prepare the fresh wrapper-rebase source and compare its source bytes,
NORMAL and READONLY MIR, and refinement with the same-build positive capture.
The synthetic Move-to-Copy NORMAL export must fail at component 17's complete
unit-SHA pin before any verification header. Capture all ten synthetic Marshal
records. Exactly the unit and body-7 hashes may differ; the other eight body
hashes must equal the manifest and the corresponding saved files.

Only in a separate TEST tool copy, replace the two component-17 owner hash
literals with those observed synthetic hashes. This two-hash patch must be
byte-reversible. Keep component 19, component 20, component 23's source and
graph checks, kernel, parser, schema, every effective `*.rsspec`, and the four
stock binaries unchanged; only the translator and rebuilt console may differ.
The same synthetic NORMAL export must then pass component 17 and fail first at
`SORT4-ACTUAL-FORGET-OWN: certificate mismatch: forget argument plain Move`,
with no verification header or A1 admission marker. The production tool and
proof source must match their pre-TEST snapshots afterward.

An exact component-19 refusal is an independent negative for this new graph,
not a positive proof. A source mismatch, setup error, wrong predicate, missing
artifact, timeout, or extra mutation is inconclusive. This TEST does not alter
production owner pins or admit the full normal/unwind post of the actual helper.
It runs in the opt-in R2 combined controls recipe; no production acceptance follows.
