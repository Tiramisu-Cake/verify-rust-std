# Cloud capture for the input-relation source candidate

The R2 hosted proof passed wrapper ownership and reached the unchanged
selected-pointer equality at verified line 143. The new source candidate
adds ghost bindings and checker assertions that relate saved input pointers to
payloads and wrapper inners; its runtime source, target normal/unwind posts,
generic applicability, parser, translator, kernel and specifications remain
unchanged. These assertions are new proof obligations, not assumptions.

The `o26-input-relation-capture` lane runs the canonical O26 baseline once,
then the isolated `--wrapper-input-relation --fingerprint` source capture.
The source must be exactly reversible to original runtime bytes; paired
NORMAL/readonly MIR and refinement must complete. All nine bodies and ten
independently hashed snapshots are preserved. The eight unaffected bodies
must match the same-build canonical capture, while unit and body 7 must
differ. The fingerprint must produce its intentional no-proof-rule refusal;
the historical owner17 source certificate is predicted to reject the changed
source, but this lane does not execute that certificate. A setup failure,
fingerprint mismatch, or missing snapshot is inconclusive. No R3 source/MIR
pin is invented by this Cloud lane.

Only after observing the actual graph and new hashes can a separately
reviewed R3 profile be proposed. This run cannot establish pointer equality,
the complete normal/unwind resources, or generic nested Drop. Its audit
always records `verification_accepted=false`.

Observed setup failure f9617843: baseline refresh21/22 patch inputs were missing
from this new recipe, despite the complete selected Git object closure. The
source/capture stage was never reached; no intended negative or proof credit.
Repair adds both exact baseline patch blobs, preserving proof source and tool
profile. Static scenario dependency gate now compares the complete canonical
o26-refresh proof-path set and every refresh-manifest patch path, not merely
the originally selected path set. A fresh source run is required.
