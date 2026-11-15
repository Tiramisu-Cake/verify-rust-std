# F7 prepared — exact recomposition

Source `8e299aa6243bc5f06a29c51e98aafa9564478220` is a separate commit directly
on accepted6 `3f5242bb1539fb88196d7e503b722f0905f2b46c`, clean branch
`fix/kani-3300-c2-slices-f7-w15`. All14 pinned historical F7 hunks in5 files are
present exactly once. The temporary pre-F7 import/writer adaptations are removed.
Tree exactly `9829702c1aa0ecb73c860fc0ad5451757917d6cb`; full diff with
`ad499e41dd2db9ccd432f89721638a1f3a0bbd44` empty, including modes/submodules/pins.
B1 and the six accepted source parents are preserved. No residual remains.

[Recomposition](RECOMPOSE.json), [seams](COMPILE-SEAMS.md), source.patch,
SOURCE-MAP-DELTA.json and ORACLE-MAP-DELTA.json bind the result. Historical
EXTRACTION-PLAN/F7-RESIDUAL files stay as immutable planning/patch anchors;
SLICE.json and this result describe the now-applied extraction.
[Worker14 source review](../reviews/f7-worker14.md): PASS, no findings.

[CI overlay/request](../ci/slice-07/CI-REQUEST.md) is prepared separately on F7;
Quick471, exact compiler76 and targeted28 units including F7 six+two, fresh
mixed-vs-isolated18 comparisons and affected LLBC build are requested. Native
checks/CI/push are NOT_RUN. Static and synthetic checks are not compilation,
new end-to-end isolation observations, Gate A or formal proof credit.

Stage8 final handoff/reconciliation is not started by this stage7 task.
