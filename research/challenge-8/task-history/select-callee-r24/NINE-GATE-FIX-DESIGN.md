# R24 mutually exclusive certificate-profile correction

Buildbba86d46 compiles (Brief console-build exit0), but ordinary positive stage
RAN/exit2. Exact log4-11 reports successful structural nine-body/A1Nine
admission followed by the new checked-outcome gate refusal. No formal proof
acceptance or successful projection is established.

The new gate incorrectly requires both A1Nine.active and A1Link.active. Existing
certify_sort4_a1_nine at13477 explicitly rejects A1_LINK_REPO_ROOT, while
initialization at14008 sets A1Link.active=false when that locator is absent.
These are independent nine-body and two-body entry profiles. The nine-body
certificate directly invokes A1Link.local_shape, A1Link.interface for both
local bodies (including exact req/ens/on_unwind_ens false), and check_graph,
then checks the outer call and only then sets A1Nine.active=true.

Correction: require A1Nine.active, A1Link.active=false and A1_LINK_REPO_ROOT
absent, keeping every other original gate condition. This selects the
already certified nine-body path and explicitly excludes the two-body route.
It adds no callee summary or premise. Ordinary verification of both checked
callee bodies remains mandatory; structural certificate acceptance is not
formal acceptance. No source, MIR, signatures, raw ten cleanup edges, typed
call matcher, projections, counters, contract, checker, prelude, or normal/
unwind/abort/Drop/leak/refinement/ownership/thread/provenance control changes.

Alternatives rejected: setting A1Link.active during nine-body certification
would conflate profiles and enable unrelated two-body behavior; removing all
A1 conditions would lose the necessary exact certificate. The correction
keeps the existing nine-body admission and explicit two-body exclusion.

Separate row31 applies after immutable rows29/30. Runner checks patch,
intermediate/final translator hashes and final four-file inventory, actual
profile metadata final hash, and exact recipe asset. Fingerprint and baseline
AST stay default-off; source/fingerprint rows unchanged. Static chain tests
and same-reviewer semantic delta precede a full1200 Cloud Build. No local
compiler, exporter, decoder, verifier or proof execution.
